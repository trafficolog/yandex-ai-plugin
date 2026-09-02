from __future__ import annotations


def find_demand_candidates(bundle: dict) -> list[dict]:
    findings=[]
    for item in bundle.get('demand', []):
        if not item.get('context_compatible'):
            continue
        if item.get('direct_coverage') not in {'weak','none'}:
            continue
        findings.append({
            'type':'DEMAND_EXPANSION_CANDIDATE',
            'kind':'DERIVED',
            'confidence':'MEDIUM',
            'query':item.get('query'),
            'evidence':{
                'wordstat_count':item.get('wordstat_count'),
                'direct_coverage':item.get('direct_coverage'),
                'source':item.get('source','yandex-wordstat'),
            },
            'limitations':['Wordstat demand is external demand evidence, not guaranteed ad inventory.'],
            'next_step':'Review targeting, negatives, budget, bidding, region, schedule, strategy and eligibility before changing coverage.',
        })
    return findings
