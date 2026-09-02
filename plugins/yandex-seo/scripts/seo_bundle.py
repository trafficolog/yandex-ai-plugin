from __future__ import annotations

try:
    from .seo_context import (
        classify_device_alignment,
        classify_geo_alignment,
        classify_period_alignment,
        classify_search_alignment,
    )
except ImportError:
    from seo_context import (
        classify_device_alignment,
        classify_geo_alignment,
        classify_period_alignment,
        classify_search_alignment,
    )

ALLOWED_KINDS = {"OBSERVED", "DERIVED", "HYPOTHESIS"}
REQUIRED_CONTEXT_FIELDS = ("site", "analysis_period", "search_region_id")


def _validate_context(context: dict) -> dict:
    normalized = dict(context)
    site = normalized.get("site")
    if not isinstance(site, str) or not site.strip():
        raise ValueError("context.site is required")

    period = normalized.get("analysis_period")
    if not isinstance(period, dict) or not period.get("from") or not period.get("to"):
        raise ValueError("context.analysis_period must contain from and to")

    region = normalized.get("search_region_id")
    if region is None or (isinstance(region, str) and not region.strip()):
        raise ValueError("context.search_region_id is required")
    return normalized


def new_bundle(context: dict, coverage: dict) -> dict:
    normalized_context = _validate_context(context)
    period_evidence = normalized_context.get("period_evidence") or []
    geo_evidence = normalized_context.get("geo_evidence") or []
    search_evidence = normalized_context.get("search_evidence") or []
    device_evidence = normalized_context.get("device_evidence") or []
    return {
        "version": 1,
        "context": normalized_context,
        "coverage": dict(coverage),
        "alignment": {
            "period": classify_period_alignment(period_evidence),
            "geo": classify_geo_alignment(geo_evidence),
            "search": classify_search_alignment(search_evidence),
            "device": classify_device_alignment(device_evidence),
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
