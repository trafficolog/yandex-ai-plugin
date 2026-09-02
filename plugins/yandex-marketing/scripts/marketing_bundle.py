from __future__ import annotations

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


def add_evidence(bundle: dict, evidence: dict) -> dict:
    if evidence.get("kind") not in ALLOWED_KINDS:
        raise ValueError("evidence.kind must be OBSERVED, DERIVED, or HYPOTHESIS")
    if evidence.get("metric") == "demand":
        raise ValueError("ambiguous demand metric is forbidden; use wordstat_count or another source-specific metric")
    if not evidence.get("source"):
        raise ValueError("evidence.source is required")
    bundle["evidence"].append(dict(evidence))
    return bundle
