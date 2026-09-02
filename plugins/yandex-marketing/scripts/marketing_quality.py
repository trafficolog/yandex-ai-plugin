from __future__ import annotations

from .marketing_context import compare_kpi_fingerprints

EVIDENCE_ROLES = {"canonical", "reconciliation_only", "enrichment"}
MONEY_METRICS = {"cost", "cpc", "cpa", "revenue", "roas", "drr"}
CANONICAL_SOURCE = {
    "impressions": "yandex-direct",
    "clicks": "yandex-direct",
    "cost": "yandex-direct",
    "cpc": "yandex-direct",
    "search_query": "yandex-direct",
    "sessions": "yandex-metrika",
    "visits": "yandex-metrika",
    "conversions": "yandex-metrika",
    "revenue": "yandex-metrika",
    "orders": "yandex-metrika",
    "wordstat_count": "yandex-wordstat",
    "serp_context": "yandex-search",
}


def derive_evidence_role(metric: str | None, source: str | None) -> str:
    preferred = CANONICAL_SOURCE.get(metric)
    if preferred is None:
        return "enrichment"
    return "canonical" if source == preferred else "reconciliation_only"


def _role_record(record: dict) -> dict:
    item = dict(record)
    role = item.get("role")
    if role is None:
        item["role"] = derive_evidence_role(item.get("metric"), item.get("source"))
    elif role not in EVIDENCE_ROLES:
        raise ValueError(f"unsupported evidence role: {role}")
    return item


def canonical_metric(metric: str, records: list[dict]) -> dict | None:
    preferred = CANONICAL_SOURCE.get(metric)
    if preferred:
        for record in records:
            if record.get("metric") == metric and record.get("source") == preferred:
                return record
    for record in records:
        if record.get("metric") == metric and record.get("role") == "canonical":
            return record
    for record in records:
        if record.get("metric") == metric:
            return record
    return None


def _reconciliation_result(metric: str, status: str, relevant: list[dict], **extra) -> dict:
    result = {
        "metric": metric,
        "status": status,
        "records": relevant,
        "canonical": canonical_metric(metric, relevant),
        "compatibility_limitations": list(extra.pop("compatibility_limitations", [])),
    }
    result.update(extra)
    return result


def _money_context_complete(record: dict) -> bool:
    kpi = record.get("kpi")
    if not isinstance(kpi, dict):
        return False
    period = kpi.get("period")
    return bool(
        kpi.get("currency")
        and kpi.get("vat_basis")
        and isinstance(period, dict)
        and period.get("from")
        and period.get("to")
    )


def reconcile_metric(metric: str, records: list[dict], context: dict) -> dict:
    relevant = [_role_record(record) for record in records if record.get("metric") == metric]
    if len(relevant) < 2:
        return _reconciliation_result(
            metric,
            "REVIEW",
            relevant,
            reason="insufficient overlapping evidence",
        )

    if metric in MONEY_METRICS and any(not _money_context_complete(record) for record in relevant):
        return _reconciliation_result(
            metric,
            "INCOMPARABLE",
            relevant,
            compatibility_limitations=["MONEY_CONTEXT_UNKNOWN"],
            reason="monetary evidence is missing currency/VAT/period context",
        )

    kpis = [record.get("kpi") for record in relevant if isinstance(record.get("kpi"), dict)]
    if len(kpis) >= 2:
        baseline = kpis[0]
        for other in kpis[1:]:
            comparison = compare_kpi_fingerprints(baseline, other)
            if not comparison["compatible"]:
                return _reconciliation_result(
                    metric,
                    "INCOMPARABLE",
                    relevant,
                    mismatches=comparison["mismatches"],
                    missing=comparison.get("missing", []),
                    compatibility_limitations=["KPI_CONTEXT_INCOMPATIBLE"],
                )

    values = [record.get("value") for record in relevant]
    if all(value == values[0] for value in values[1:]):
        return _reconciliation_result(metric, "ALIGNED", relevant)
    if context.get("known_difference_reason"):
        return _reconciliation_result(
            metric,
            "EXPLAINABLE_DIFFERENCE",
            relevant,
            reason=context["known_difference_reason"],
        )
    return _reconciliation_result(metric, "REVIEW", relevant)


def propagate_limitations(source_records: list[dict]) -> list[dict]:
    result: list[dict] = []
    for record in source_records:
        source = record.get("source")
        if source == "yandex-metrika":
            if "quality" not in record or not isinstance(record.get("quality"), dict):
                result.append({"code": "QUALITY_METADATA_MISSING", "source": source})
            else:
                quality = record["quality"]
                if quality.get("sampled"):
                    result.append({
                        "code": "METRIKA_SAMPLED",
                        "source": source,
                        "sample_share": quality.get("sample_share"),
                    })
                if quality.get("data_lag") not in (None, 0):
                    result.append({
                        "code": "DATA_LAG",
                        "source": source,
                        "value": quality.get("data_lag"),
                    })
        if source == "yandex-wordstat":
            coverage = record.get("coverage")
            if isinstance(coverage, dict) and coverage.get("associations_truncated"):
                result.append({"code": "WORDSTAT_ASSOCIATIONS_CAPPED", "source": source})
        if record.get("maturity") == "IMMATURE":
            result.append({"code": "IMMATURE", "source": source})
        if record.get("maturity") == "MATURITY_UNKNOWN":
            result.append({"code": "MATURITY_UNKNOWN", "source": source})
        if record.get("bridge_risk"):
            result.append({"code": "SEARCH_BRIDGE_RISK", "source": source})
        if record.get("approximate_period"):
            result.append({"code": "APPROXIMATE_PERIOD", "source": source})
    return result


def capability_mode(coverage: dict) -> str:
    if not coverage.get("direct"):
        return "ROUTING_REQUIRED"
    metrika = bool(coverage.get("metrika"))
    wordstat = bool(coverage.get("wordstat"))
    search = bool(coverage.get("search"))
    if metrika and wordstat:
        return "FULL_ACQUISITION"
    if coverage.get("workflow") == "queries" and wordstat:
        return "QUERY_INTELLIGENCE"
    if metrika:
        return "PAID_PERFORMANCE"
    if wordstat:
        return "DEMAND_PLANNING"
    if search:
        return "COMPETITIVE_CONTEXT"
    return "DIRECT_ONLY"
