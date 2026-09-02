from __future__ import annotations

DEFAULT_GROUP_ORDER = [
    'MEASUREMENT_RISK','GOAL_ALIGNMENT_RISK','ATTRIBUTION_MISMATCH','KPI_CONTEXT_MISMATCH','MATURITY_RISK',
    'BUDGET_CONSTRAINT_CANDIDATE','BUDGET_REALLOCATION_CANDIDATE','SPEND_EFFICIENCY_REVIEW',
    'DEMAND_EXPANSION_CANDIDATE','QUERY_COVERAGE_GAP','SEARCH_TERM_EXPANSION_CANDIDATE','SEARCH_TERM_EXCLUSION_REVIEW','SEASONALITY_ALERT',
    'LANDING_MISMATCH_HYPOTHESIS','QUERY_MISMATCH_HYPOTHESIS','TRAFFIC_QUALITY_HYPOTHESIS',
    'COMPETITIVE_CONTEXT','SERP_INTENT_CONTEXT',
]


def prioritize(findings: list[dict], priority_order: list[str] | None = None) -> list[dict]:
    order = list(priority_order or DEFAULT_GROUP_ORDER)
    rank = {name: i for i, name in enumerate(order)}
    mode = 'USER_ORDER' if priority_order is not None else 'DEFAULT_CATEGORICAL'
    result=[]
    for finding in findings:
        item=dict(finding)
        item['priority_basis']={'mode':mode,'type_rank':rank.get(item.get('type'), len(rank))}
        result.append(item)
    return sorted(result, key=lambda x: (x['priority_basis']['type_rank'], str(x.get('target', {}))))


def delegate_action(finding: dict) -> dict | None:
    type_ = finding.get('type')
    mapping = {
        'BUDGET_CONSTRAINT_CANDIDATE': ('yandex-direct','yandex-direct-budget'),
        'BUDGET_REALLOCATION_CANDIDATE': ('yandex-direct','yandex-direct-budget'),
        'SEARCH_TERM_EXPANSION_CANDIDATE': ('yandex-direct','yandex-direct-keywords'),
        'SEARCH_TERM_EXCLUSION_REVIEW': ('yandex-direct','yandex-direct-keywords'),
        'QUERY_COVERAGE_GAP': ('yandex-direct','yandex-direct-keywords'),
        'SPEND_EFFICIENCY_REVIEW': ('yandex-direct','yandex-direct-optimize'),
        'TRAFFIC_QUALITY_HYPOTHESIS': ('yandex-direct','yandex-direct-optimize'),
        'NEW_CAMPAIGN_CANDIDATE': ('yandex-direct','yandex-direct-create'),
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
