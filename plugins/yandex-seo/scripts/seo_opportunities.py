from __future__ import annotations


def _finding(kind: str, type_: str, **extra) -> dict:
    return {"kind": kind, "type": type_, **extra}


def _bundle_has_limitation(bundle: dict, kind: str) -> bool:
    return any(item.get("kind") == kind for item in bundle.get("limitations") or [])


def find_content_gaps(bundle: dict) -> list[dict]:
    out: list[dict] = []
    coverage = bundle.get("coverage") or {}
    webmaster_top_n = _bundle_has_limitation(bundle, "WEBMASTER_TOP_N")

    for query in bundle.get("queries") or []:
        if not query.get("wordstat_count"):
            continue

        query_key = query.get("query_key")
        if coverage.get("search") and coverage.get("webmaster"):
            search_absent = query.get("search_site_present") is False
            impressions = query.get("webmaster_impressions")

            if search_absent and impressions == 0:
                limitations: list[str] = []
                confidence = "HIGH"
                if webmaster_top_n:
                    limitations.append("WEBMASTER_TOP_N")
                    confidence = "MEDIUM"
                out.append(_finding(
                    "DERIVED",
                    "CONTENT_GAP",
                    query_key=query_key,
                    confidence=confidence,
                    evidence=["wordstat", "search", "webmaster"],
                    limitations=limitations,
                ))
                continue

            if search_absent and impressions is None:
                out.append(_finding(
                    "DERIVED",
                    "DISCOVERY_CANDIDATE",
                    query_key=query_key,
                    confidence="LOW",
                    evidence=["wordstat", "search"],
                    limitations=["WEBMASTER_IMPRESSIONS_UNKNOWN"],
                ))
                continue
        else:
            out.append(_finding(
                "DERIVED",
                "DISCOVERY_CANDIDATE",
                query_key=query_key,
                confidence="LOW",
                evidence=["wordstat"],
                limitations=[],
            ))
    return out


def find_ctr_opportunities(bundle: dict) -> list[dict]:
    out: list[dict] = []
    for query in bundle.get("queries") or []:
        current = query.get("webmaster_ctr")
        baseline = query.get("own_baseline_ctr")
        if isinstance(current, (int, float)) and isinstance(baseline, (int, float)) and current < baseline:
            out.append(_finding(
                "DERIVED",
                "CTR_OPPORTUNITY",
                query_key=query.get("query_key"),
                current_ctr=current,
                own_baseline_ctr=baseline,
                confidence="MEDIUM",
            ))
    return out


def find_conversion_opportunities(bundle: dict) -> list[dict]:
    out: list[dict] = []
    for page in bundle.get("pages") or []:
        current = page.get("organic_conversion_rate")
        baseline = page.get("own_comparable_conversion_rate")
        if page.get("intent_evidence") and isinstance(current, (int, float)) and isinstance(baseline, (int, float)) and current < baseline:
            out.append(_finding(
                "HYPOTHESIS",
                "LANDING_OR_INTENT_MISMATCH",
                url_key=page.get("url_key"),
                current_conversion_rate=current,
                own_comparable_conversion_rate=baseline,
                confidence="MEDIUM",
                requires_validation=True,
            ))
    return out


def find_technical_blockers(bundle: dict) -> list[dict]:
    out: list[dict] = []
    for page in bundle.get("pages") or []:
        if page.get("technical_issue") and page.get("opportunity_evidence"):
            out.append(_finding(
                "DERIVED",
                "TECHNICAL_BLOCKER",
                url_key=page.get("url_key"),
                issue=page.get("technical_issue"),
                confidence="HIGH",
                causal_claim=False,
            ))
    return out
