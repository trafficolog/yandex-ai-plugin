from __future__ import annotations

try:
    from .marketing_quality import EVIDENCE_ROLES, MONEY_METRICS, derive_evidence_role
except ImportError:
    from marketing_quality import EVIDENCE_ROLES, MONEY_METRICS, derive_evidence_role

ALLOWED_KINDS = {"OBSERVED", "DERIVED", "HYPOTHESIS"}


def new_bundle(context: dict, coverage: dict) -> dict:
    if "direct" not in coverage:
        raise ValueError("coverage.direct must be explicit")
    normalized_coverage = {
        name: bool(coverage.get(name, False))
        for name in ("direct", "metrika", "wordstat", "search")
    }
    return {
        "version": 1,
        "context": dict(context),
        "coverage": normalized_coverage,
        "routing_required": not normalized_coverage["direct"],
        "campaigns": [],
        "criteria": [],
        "search_queries": [],
        "landings": [],
        "goals": [],
        "demand": [],
        "sources": {},
        "evidence": [],
        "findings": [],
        "limitations": [],
    }


def _money_context_complete(evidence: dict) -> bool:
    kpi = evidence.get("kpi")
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


def add_evidence(bundle: dict, evidence: dict) -> dict:
    if evidence.get("kind") not in ALLOWED_KINDS:
        raise ValueError("evidence.kind must be OBSERVED, DERIVED, or HYPOTHESIS")
    if evidence.get("metric") == "demand":
        raise ValueError("ambiguous demand metric is forbidden; use wordstat_count or another source-specific metric")
    if not evidence.get("source"):
        raise ValueError("evidence.source is required")

    item = dict(evidence)
    explicit_role = item.get("role")
    if explicit_role is not None:
        if explicit_role not in EVIDENCE_ROLES:
            raise ValueError(f"evidence.role must be one of {sorted(EVIDENCE_ROLES)}")
    else:
        item["role"] = derive_evidence_role(item.get("metric"), item.get("source"))

    if item.get("metric") in MONEY_METRICS and not _money_context_complete(item):
        limitations = list(item.get("limitations") or [])
        if "MONEY_CONTEXT_UNKNOWN" not in limitations:
            limitations.append("MONEY_CONTEXT_UNKNOWN")
        item["limitations"] = limitations

    bundle["evidence"].append(item)
    return bundle
