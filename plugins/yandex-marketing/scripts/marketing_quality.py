from __future__ import annotations

from .marketing_context import compare_kpi_fingerprints

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


def canonical_metric(metric: str, records: list[dict]) -> dict | None:
    preferred = CANONICAL_SOURCE.get(metric)
    if preferred:
        for record in records:
            if record.get("metric") == metric and record.get("source") == preferred:
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
    }
    result.update(extra)
    return result


def reconcile_metric(metric: str, records: list[dict], context: dict) -> dict:
    relevant = [record for record in records if record.get("metric") == metric]
    if len(relevant) < 2:
        return _reconciliation_result(
            metric,
            "REVIEW",
            relevant,
            reason="insufficient overlapping evidence",
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
        raise ValueError("Direct evidence is required for yandex-marketing analysis")
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
