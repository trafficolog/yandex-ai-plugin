from __future__ import annotations
from .marketing_context import kpi_fingerprint, compare_kpi_fingerprints
from .marketing_quality import reconcile_metric


def derive_performance(record: dict, kpi: dict) -> dict:
    out = {'kpi': kpi_fingerprint(kpi), 'limitations': []}
    for key in ('impressions','clicks','cost','conversions','revenue'):
        if record.get(key) is not None:
            out[key] = record[key]
    impressions, clicks = record.get('impressions'), record.get('clicks')
    cost, conversions, revenue = record.get('cost'), record.get('conversions'), record.get('revenue')
    if clicks not in (None, 0) and cost is not None:
        out['cpc'] = cost / clicks
    if impressions not in (None, 0) and clicks is not None:
        out['ctr'] = clicks / impressions
    if clicks not in (None, 0) and conversions is not None:
        out['cr'] = conversions / clicks
    if conversions not in (None, 0) and cost is not None:
        out['cpa'] = cost / conversions
    if cost not in (None, 0) and revenue is not None:
        out['roas'] = revenue / cost
        if revenue != 0:
            out['drr'] = cost / revenue
    maturity = record.get('maturity')
    if maturity in {'IMMATURE','MATURITY_UNKNOWN'}:
        out['limitations'].append(maturity)
    return out


def compare_performance(left: dict, right: dict) -> dict:
    comparison = compare_kpi_fingerprints(left.get('kpi', {}), right.get('kpi', {}))
    if not comparison['compatible']:
        return {'status': 'INCOMPARABLE', 'mismatches': comparison['mismatches']}
    deltas = {}
    for metric in ('cpc','ctr','cr','cpa','roas','drr','cost','conversions','revenue'):
        if metric in left and metric in right:
            deltas[metric] = right[metric] - left[metric]
    return {'status': 'ALIGNED', 'deltas': deltas}


def reconcile_conversions(direct: dict, metrika: dict, context: dict) -> dict:
    return reconcile_metric('conversions', [direct, metrika], context)
