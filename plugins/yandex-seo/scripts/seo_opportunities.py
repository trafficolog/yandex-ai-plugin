from __future__ import annotations


def _finding(kind: str, type_: str, **extra) -> dict:
    return {'kind': kind, 'type': type_, **extra}


def find_content_gaps(bundle: dict) -> list[dict]:
    out=[]
    coverage=bundle.get('coverage') or {}
    for q in bundle.get('queries') or []:
        if not q.get('wordstat_count'):
            continue
        if coverage.get('search') and coverage.get('webmaster'):
            absent = q.get('search_site_present') is False and (q.get('webmaster_impressions') or 0) == 0
            if absent:
                out.append(_finding('DERIVED','CONTENT_GAP',query_key=q.get('query_key'),confidence='HIGH',evidence=['wordstat','search','webmaster']))
        else:
            out.append(_finding('DERIVED','DISCOVERY_CANDIDATE',query_key=q.get('query_key'),confidence='LOW',evidence=['wordstat']))
    return out


def find_ctr_opportunities(bundle: dict) -> list[dict]:
    out=[]
    for q in bundle.get('queries') or []:
        current=q.get('webmaster_ctr'); baseline=q.get('own_baseline_ctr')
        if isinstance(current,(int,float)) and isinstance(baseline,(int,float)) and current < baseline:
            out.append(_finding('DERIVED','CTR_OPPORTUNITY',query_key=q.get('query_key'),current_ctr=current,own_baseline_ctr=baseline,confidence='MEDIUM'))
    return out


def find_conversion_opportunities(bundle: dict) -> list[dict]:
    out=[]
    for p in bundle.get('pages') or []:
        current=p.get('organic_conversion_rate'); baseline=p.get('own_comparable_conversion_rate')
        if p.get('intent_evidence') and isinstance(current,(int,float)) and isinstance(baseline,(int,float)) and current < baseline:
            out.append(_finding('HYPOTHESIS','LANDING_OR_INTENT_MISMATCH',url_key=p.get('url_key'),current_conversion_rate=current,own_comparable_conversion_rate=baseline,confidence='MEDIUM',requires_validation=True))
    return out


def find_technical_blockers(bundle: dict) -> list[dict]:
    out=[]
    for p in bundle.get('pages') or []:
        if p.get('technical_issue') and p.get('opportunity_evidence'):
            out.append(_finding('DERIVED','TECHNICAL_BLOCKER',url_key=p.get('url_key'),issue=p.get('technical_issue'),confidence='HIGH',causal_claim=False))
    return out
