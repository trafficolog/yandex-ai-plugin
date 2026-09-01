from __future__ import annotations
from itertools import combinations
from typing import Any

def _urls(snapshot:dict[str,Any],top_k:int)->set[str]:
    if snapshot.get('group_mode')!='GROUP_MODE_FLAT' or snapshot.get('docs_in_group',1)!=1: raise ValueError('clustering requires FLAT snapshots')
    return {r['url_key'] for r in snapshot.get('results',[])[:top_k] if r.get('url_key')}

def pairwise_overlap(a:dict[str,Any],b:dict[str,Any],*,top_k:int=10)->dict[str,Any]:
    if top_k<1: raise ValueError('top_k must be positive')
    ua,ub=_urls(a,top_k),_urls(b,top_k); inter=ua&ub; union=ua|ub
    return {'query_a':a['query'],'query_b':b['query'],'shared_urls':len(inter),'shared_url_keys':sorted(inter),'jaccard':0.0 if not union else round(len(inter)/len(union),6)}

def cluster_queries(snapshots:list[dict[str,Any]],*,min_shared_urls:int,top_k:int=10)->dict[str,Any]:
    if not isinstance(min_shared_urls,int) or min_shared_urls<1: raise ValueError('min_shared_urls must be a positive integer')
    fingerprints={s.get('config_fingerprint') for s in snapshots}
    if len(fingerprints)>1: raise ValueError('all clustering snapshots must share one config_fingerprint')
    queries_raw=[s['query'] for s in snapshots]
    if len(set(queries_raw))!=len(queries_raw): raise ValueError('snapshot queries must be unique')
    by_query={s['query']:s for s in snapshots}; queries=list(by_query); edges={q:set() for q in queries}; pairs=[]
    for qa,qb in combinations(queries,2):
        m=pairwise_overlap(by_query[qa],by_query[qb],top_k=top_k); pairs.append(m)
        if m['shared_urls']>=min_shared_urls: edges[qa].add(qb); edges[qb].add(qa)
    seen=set(); clusters=[]
    pair_map={frozenset((p['query_a'],p['query_b'])):p for p in pairs}
    for q in queries:
        if q in seen: continue
        stack=[q]; comp=[]; seen.add(q)
        while stack:
            cur=stack.pop(); comp.append(cur)
            for nxt in sorted(edges[cur]):
                if nxt not in seen: seen.add(nxt); stack.append(nxt)
        direct=[]
        for a,b in combinations(sorted(comp),2): direct.append(pair_map[frozenset((a,b))])
        weakest=min(direct,key=lambda x:(x['shared_urls'],x['jaccard'])) if direct else {'query_a':q,'query_b':q,'shared_urls':top_k,'jaccard':1.0}
        bridge=any(p['shared_urls']<min_shared_urls for p in direct)
        degree={x:len(edges[x]&set(comp)) for x in comp}; representative=sorted(comp,key=lambda x:(-degree[x],x))[0]
        clusters.append({'queries':sorted(comp),'representative':representative,'weakest_pair':weakest,'bridge_risk':bridge})
    return {'top_k':top_k,'min_shared_urls':min_shared_urls,'pairs':pairs,'clusters':clusters}
