from __future__ import annotations
from datetime import datetime, timezone
import hashlib,json
from typing import Any
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode

def normalize_url(url:str)->str:
    p=urlsplit(url.strip())
    scheme=p.scheme.lower(); host=(p.hostname or '').lower()
    if not scheme or not host: raise ValueError('absolute URL is required')
    port=p.port
    netloc=host if port is None or (scheme=='https' and port==443) or (scheme=='http' and port==80) else f'{host}:{port}'
    path=p.path or '/'
    query=urlencode(sorted(parse_qsl(p.query,keep_blank_values=True)),doseq=True)
    return urlunsplit((scheme,netloc,path,query,''))

def _fingerprint(config:dict[str,Any])->str:
    return hashlib.sha256(json.dumps(config,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:20]

def build_snapshot(query:str,results:list[dict[str,Any]],*,search_type:str='SEARCH_TYPE_RU',region:int|None=None,page:int=0,group_mode:str='GROUP_MODE_FLAT',groups_on_page:int=20,docs_in_group:int=1,results_within:str='WITHIN_ALL_TIME',sort_mode:str='SORT_MODE_BY_RELEVANCE',family_mode:str='FAMILY_MODE_MODERATE',fix_typo_mode:str='FIX_TYPO_MODE_ON',response_format:str='FORMAT_XML',collected_at:str|None=None)->dict[str,Any]:
    if group_mode!='GROUP_MODE_FLAT' or docs_in_group!=1: raise ValueError('structured SEO snapshots require GROUP_MODE_FLAT and docs_in_group=1')
    config={'search_type':search_type,'region':region,'page':page,'group_mode':group_mode,'groups_on_page':groups_on_page,'docs_in_group':docs_in_group,'results_within':results_within,'sort_mode':sort_mode,'family_mode':family_mode,'fix_typo_mode':fix_typo_mode,'response_format':response_format}
    normalized=[]
    for item in results:
        row=dict(item); row['url_key']=normalize_url(row['url']); row['host']=urlsplit(row['url_key']).hostname
        normalized.append(row)
    return {'query':query,**config,'config_fingerprint':_fingerprint(config),'collected_at':collected_at or datetime.now(timezone.utc).isoformat(),'results':normalized}
