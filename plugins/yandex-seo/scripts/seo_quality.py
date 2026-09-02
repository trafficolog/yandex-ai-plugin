from __future__ import annotations


def capability_mode(coverage: dict) -> str:
    have = {k for k, v in coverage.items() if v}
    if {'wordstat','search','webmaster','metrika'} <= have:
        return 'FULL'
    if have == {'wordstat','search'}:
        return 'DISCOVERY'
    if have == {'search','webmaster'}:
        return 'VISIBILITY'
    if have == {'webmaster','metrika'}:
        return 'PERFORMANCE'
    return 'PARTIAL'


def propagate_limitations(source_records: list[dict]) -> list[dict]:
    limitations: list[dict] = []
    for record in source_records:
        source = record.get('source')
        if source == 'yandex-metrika':
            quality = record.get('quality') or {}
            if quality.get('sampled'):
                limitations.append({
                    'kind':'METRIKA_SAMPLING',
                    'source':source,
                    'sample_share':quality.get('sample_share'),
                    'data_lag':quality.get('data_lag'),
                })
        if source == 'yandex-webmaster':
            coverage = record.get('coverage') or {}
            if coverage.get('top_n'):
                limitations.append({'kind':'WEBMASTER_TOP_N','source':source,'top_n':coverage['top_n']})
        if source == 'yandex-search':
            cluster = record.get('cluster') or {}
            if cluster.get('bridge_risk'):
                limitations.append({'kind':'SEARCH_BRIDGE_RISK','source':source,'cluster_id':cluster.get('cluster_id')})
        for limitation in record.get('limitations') or []:
            limitations.append({'kind':'SOURCE_LIMITATION','source':source,'detail':limitation})
    unique=[]
    seen=set()
    for item in limitations:
        key=repr(sorted(item.items()))
        if key not in seen:
            seen.add(key); unique.append(item)
    return unique
