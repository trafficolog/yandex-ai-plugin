from __future__ import annotations


def _finding(type_: str, kind: str, target: dict, evidence, confidence='MEDIUM', limitations=None, next_step='Review evidence before delegated changes.'):
    return {
        'type': type_, 'kind': kind, 'confidence': confidence,
        'target': target, 'evidence': evidence,
        'limitations': list(limitations or []), 'next_step': next_step,
    }


def find_query_candidates(bundle: dict) -> list[dict]:
    findings=[]
    for item in bundle.get('search_queries', []):
        query=item.get('query')
        evidence={}
        if item.get('wordstat_context') is not None:
            evidence['wordstat_context']=item['wordstat_context']
        if item.get('search_context') is not None:
            evidence['search_context']=item['search_context']
        if item.get('expansion_signal'):
            findings.append(_finding(
                'SEARCH_TERM_EXPANSION_CANDIDATE','DERIVED',{'query':query},evidence,
                next_step='Review criterion coverage, negatives and business relevance before adding targeting.'
            ))
        if (
            item.get('exclusion_signal') and item.get('performance_sufficient') and
            item.get('maturity') == 'MATURE' and item.get('business_goal_aligned')
        ):
            evidence.update({'clicks':item.get('clicks'),'conversions':item.get('conversions')})
            findings.append(_finding(
                'SEARCH_TERM_EXCLUSION_REVIEW','DERIVED',{'query':query},evidence,
                limitations=['This is a review candidate, not an automatic negative-keyword rule.'],
                next_step='Review query intent and exact change preview in yandex-direct-keywords.'
            ))
    return findings


def find_landing_hypotheses(bundle: dict) -> list[dict]:
    findings=[]
    for item in bundle.get('landings', []):
        if item.get('intent_mismatch_signal'):
            findings.append(_finding(
                'LANDING_MISMATCH_HYPOTHESIS','HYPOTHESIS',{'url':item.get('url')},
                item.get('evidence', []),
                limitations=['Observational evidence does not establish causality.'],
                next_step='Validate query/ad/landing intent and measurement before changing ads or landing pages.'
            ))
    return findings


def find_budget_candidates(bundle: dict) -> list[dict]:
    findings=[]
    for item in bundle.get('campaigns', []):
        ready = item.get('kpi_compatible') and item.get('performance_sufficient') and item.get('maturity') == 'MATURE'
        if not ready:
            continue
        if item.get('budget_constraint_signal'):
            findings.append(_finding(
                'BUDGET_CONSTRAINT_CANDIDATE','DERIVED',{'campaign_id':item.get('campaign_id')},
                item.get('evidence', []), next_step='Prepare a reversible budget-change preview in yandex-direct-budget.'
            ))
        if item.get('budget_reallocation_signal'):
            findings.append(_finding(
                'BUDGET_REALLOCATION_CANDIDATE','DERIVED',{'campaign_id':item.get('campaign_id')},
                item.get('evidence', []), next_step='Compare only KPI-compatible campaigns, then preview the reallocation.'
            ))
    return findings


def find_measurement_risks(bundle: dict) -> list[dict]:
    findings=[]
    for item in bundle.get('campaigns', []):
        target={'campaign_id':item.get('campaign_id')}
        if item.get('kpi_compatible') is False:
            findings.append(_finding('KPI_CONTEXT_MISMATCH','DERIVED',target,['incompatible KPI fingerprint'], confidence='HIGH'))
        if item.get('attribution_compatible') is False:
            findings.append(_finding('ATTRIBUTION_MISMATCH','DERIVED',target,['incompatible attribution context'], confidence='HIGH'))
        if item.get('measurement_risk'):
            findings.append(_finding('MEASUREMENT_RISK','DERIVED',target,item.get('evidence', [])))
    return findings
