from __future__ import annotations

try:
    from .seo_context import classify_geo_alignment, classify_period_alignment
except ImportError:
    from seo_context import classify_geo_alignment, classify_period_alignment

ALLOWED_KINDS = {"OBSERVED", "DERIVED", "HYPOTHESIS"}


def new_bundle(context: dict, coverage: dict) -> dict:
    normalized_context = dict(context)
    period_evidence = normalized_context.get("period_evidence") or []
    geo_evidence = normalized_context.get("geo_evidence") or []
    return {
        "version": 1,
        "context": normalized_context,
        "coverage": dict(coverage),
        "alignment": {
            "period": classify_period_alignment(period_evidence),
            "geo": classify_geo_alignment(geo_evidence),
        },
        "queries": [],
        "pages": [],
        "clusters": [],
        "sources": {},
        "evidence": [],
        "findings": [],
        "limitations": [],
    }


def add_evidence(bundle: dict, evidence: dict) -> dict:
    if evidence.get("kind") not in ALLOWED_KINDS:
        raise ValueError("evidence kind must be OBSERVED, DERIVED, or HYPOTHESIS")
    if evidence.get("metric") == "demand":
        raise ValueError("ambiguous demand metric is forbidden; use source-specific metric name")
    if not evidence.get("source"):
        raise ValueError("evidence source is required")
    bundle.setdefault("evidence", []).append(dict(evidence))
    return bundle
