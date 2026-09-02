from __future__ import annotations

IMPLEMENTED_FINDING_TYPES = {
    'MEASUREMENT_RISK',
    'KPI_CONTEXT_MISMATCH',
    'ATTRIBUTION_MISMATCH',
    'BUDGET_CONSTRAINT_CANDIDATE',
    'BUDGET_REALLOCATION_CANDIDATE',
    'DEMAND_EXPANSION_CANDIDATE',
    'SEARCH_TERM_EXPANSION_CANDIDATE',
    'SEARCH_TERM_EXCLUSION_REVIEW',
    'LANDING_MISMATCH_HYPOTHESIS',
}

DEFERRED_FINDING_TYPES = {
    'GOAL_ALIGNMENT_RISK',
    'MATURITY_RISK',
    'SPEND_EFFICIENCY_REVIEW',
    'QUERY_COVERAGE_GAP',
    'SEASONALITY_ALERT',
    'QUERY_MISMATCH_HYPOTHESIS',
    'TRAFFIC_QUALITY_HYPOTHESIS',
    'COMPETITIVE_CONTEXT',
    'SERP_INTENT_CONTEXT',
}

APPROVED_EXTERNAL_FINDING_TYPES = {'GOAL_ALIGNMENT_RISK'}

DEFAULT_GROUP_ORDER = [
    'MEASUREMENT_RISK',
    'KPI_CONTEXT_MISMATCH',
    'ATTRIBUTION_MISMATCH',
    'BUDGET_CONSTRAINT_CANDIDATE',
    'BUDGET_REALLOCATION_CANDIDATE',
    'DEMAND_EXPANSION_CANDIDATE',
    'SEARCH_TERM_EXPANSION_CANDIDATE',
    'SEARCH_TERM_EXCLUSION_REVIEW',
    'LANDING_MISMATCH_HYPOTHESIS',
]


def prioritize(findings: list[dict], priority_order: list[str] | None = None) -> list[dict]:
    use_default = not priority_order
    order = list(DEFAULT_GROUP_ORDER if use_default else priority_order)
    rank = {name: i for i, name in enumerate(order)}
    mode = 'DEFAULT_CATEGORICAL' if use_default else 'USER_ORDER'
    result=[]
    for finding in findings:
        item=dict(finding)
        type_ = item.get('type')
        item['priority_basis']={'mode':mode,'type_rank':rank.get(type_, len(rank))}
        if use_default and type_ not in IMPLEMENTED_FINDING_TYPES:
            limitations = list(item.get('limitations') or [])
            if 'UNKNOWN_OR_DEFERRED_TYPE' not in limitations:
                limitations.append('UNKNOWN_OR_DEFERRED_TYPE')
            item['limitations'] = limitations
        result.append(item)
    return sorted(result, key=lambda x: (x['priority_basis']['type_rank'], str(x.get('target', {}))))


def delegate_action(finding: dict) -> dict | None:
    type_ = finding.get('type')
    if type_ not in IMPLEMENTED_FINDING_TYPES and type_ not in APPROVED_EXTERNAL_FINDING_TYPES:
        return None
    mapping = {
        'BUDGET_CONSTRAINT_CANDIDATE': ('yandex-direct','yandex-direct-budget'),
        'BUDGET_REALLOCATION_CANDIDATE': ('yandex-direct','yandex-direct-budget'),
        'SEARCH_TERM_EXPANSION_CANDIDATE': ('yandex-direct','yandex-direct-keywords'),
        'SEARCH_TERM_EXCLUSION_REVIEW': ('yandex-direct','yandex-direct-keywords'),
        'DEMAND_EXPANSION_CANDIDATE': ('yandex-direct','yandex-direct-keywords'),
    }
    if type_ == 'GOAL_ALIGNMENT_RISK' and finding.get('recommended_action') == 'goal_change':
        mapping[type_] = ('yandex-metrika','yandex-metrika-goals')
    route = mapping.get(type_)
    if route is None:
        return None
    service, skill = route
    return {
        'service': service,
        'skill': skill,
        'target': finding.get('target', {}),
        'reason': finding.get('next_step') or finding.get('reason') or type_,
        'requires_approval': True,
        'mode': 'preview-only',
    }
