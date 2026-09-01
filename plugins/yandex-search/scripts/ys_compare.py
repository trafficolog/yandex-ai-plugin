from __future__ import annotations
from statistics import median
from typing import Any

def compare_rankings(before:dict[str,Any],after:dict[str,Any])->dict[str,Any]:
    if before.get('query')!=after.get('query'): raise ValueError('snapshot queries differ')
    if before.get('config_fingerprint')!=after.get('config_fingerprint'): raise ValueError('snapshot configuration fingerprints differ')
    old={r['url_key']:r['rank'] for r in before.get('results',[])}; new={r['url_key']:r['rank'] for r in after.get('results',[])}
    changes=[]
    for url in sorted(set(old)|set(new)):
        a,b=old.get(url),new.get(url); delta=None if a is None or b is None else a-b
        changes.append({'url_key':url,'before_rank':a,'after_rank':b,'delta':delta,'status':'new' if a is None else ('dropped' if b is None else 'present')})
    return {'query':after.get('query'),'config_fingerprint':after.get('config_fingerprint'),'changes':changes}

def competitor_presence(snapshots:list[dict[str,Any]],host:str)->dict[str,Any]:
    target=host.lower().strip('.'); ranks=[]; urls=set()
    for snap in snapshots:
        matches=[r for r in snap.get('results',[]) if (r.get('host') or '').lower().strip('.')==target]
        if matches:
            best=min(r['rank'] for r in matches); ranks.append(best); urls.update(r.get('url_key') for r in matches if r.get('url_key'))
    total=len(snapshots); present=len(ranks)
    return {'host':target,'queries_total':total,'queries_present':present,'serp_presence_rate':0.0 if not total else round(present/total,6),'top_3_presence':sum(r<=3 for r in ranks),'top_10_presence':sum(r<=10 for r in ranks),'median_rank_when_present':None if not ranks else float(median(ranks)),'urls_found':sorted(urls),'metric_name':'SERP presence rate','market_share_claim':False}
