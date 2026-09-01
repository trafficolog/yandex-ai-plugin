from __future__ import annotations


def find_cannibalization(bundle: dict) -> list[dict]:
    out=[]
    for cluster in bundle.get('clusters') or []:
        urls=list(dict.fromkeys(cluster.get('own_urls') or []))
        if len(urls) < 2:
            continue
        if not (cluster.get('search_evidence') and cluster.get('webmaster_evidence')):
            continue
        confidence='HIGH' if cluster.get('position_instability') else 'MEDIUM'
        out.append({
            'kind':'HYPOTHESIS',
            'type':'CANNIBALIZATION_CANDIDATE',
            'cluster_id':cluster.get('cluster_id'),
            'own_urls':urls,
            'confidence':confidence,
            'requires_validation':True,
        })
    return out
