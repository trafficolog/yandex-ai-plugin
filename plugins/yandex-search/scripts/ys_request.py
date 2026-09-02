from __future__ import annotations
import hashlib, json
from typing import Any
try:
    from ._http import auth_headers, redact_headers
    from .ys_api import SYNC_URL, ASYNC_URL, validate_query_text
except ImportError:
    from _http import auth_headers, redact_headers
    from ys_api import SYNC_URL, ASYNC_URL, validate_query_text
SEARCH_TYPES={'SEARCH_TYPE_RU','SEARCH_TYPE_TR','SEARCH_TYPE_COM','SEARCH_TYPE_KK','SEARCH_TYPE_BE','SEARCH_TYPE_UZ'}
FAMILY_MODES={'FAMILY_MODE_NONE','FAMILY_MODE_MODERATE','FAMILY_MODE_STRICT'}
RESULTS_WITHIN={'WITHIN_ALL_TIME','WITHIN_1_DAY','WITHIN_2_WEEKS','WITHIN_1_MONTH'}
SORT_MODES={'SORT_MODE_BY_RELEVANCE','SORT_MODE_BY_TIME'}

def build_search_request(query:str,*,folder_id:str,api_key:str|None=None,iam_token:str|None=None,mode:str='sync',search_type:str='SEARCH_TYPE_RU',region:int|None=None,page:int=0,groups_on_page:int=20,response_format:str='FORMAT_XML',family_mode:str='FAMILY_MODE_MODERATE',fix_typo_mode:str='FIX_TYPO_MODE_ON',sort_mode:str='SORT_MODE_BY_RELEVANCE',results_within:str='WITHIN_ALL_TIME',group_mode:str='GROUP_MODE_FLAT',docs_in_group:int=1,user_agent:str|None=None,localization:str|None=None)->dict[str,Any]:
    q=validate_query_text(query); folder=(folder_id or '').strip()
    if not folder: raise ValueError('folder_id is required')
    if mode not in ('sync','async'): raise ValueError('mode must be sync or async')
    if search_type not in SEARCH_TYPES: raise ValueError('unsupported search_type')
    if family_mode not in FAMILY_MODES or results_within not in RESULTS_WITHIN or sort_mode not in SORT_MODES: raise ValueError('unsupported search option')
    if response_format not in ('FORMAT_XML','FORMAT_HTML'): raise ValueError('unsupported response_format')
    if group_mode not in ('GROUP_MODE_FLAT','GROUP_MODE_DEEP'): raise ValueError('unsupported group_mode')
    if not (0<=page) or not (1<=groups_on_page<=100) or not (1<=docs_in_group<=3): raise ValueError('invalid pagination/grouping')
    body={'query':{'searchType':search_type,'queryText':q,'familyMode':family_mode,'page':str(page),'fixTypoMode':fix_typo_mode},'sortSpec':{'sortMode':sort_mode,'sortOrder':'SORT_ORDER_DESC'},'groupSpec':{'groupMode':group_mode,'groupsOnPage':str(groups_on_page),'docsInGroup':str(docs_in_group)},'maxPassages':'3','region':str(region) if region is not None else '', 'folderId':folder,'responseFormat':response_format,'resultsWithin':results_within}
    if region is None: body.pop('region')
    if user_agent: body['userAgent']=user_agent
    if localization: body['l10n']=localization
    headers=auth_headers(api_key=api_key,iam_token=iam_token); url=SYNC_URL if mode=='sync' else ASYNC_URL
    return {'method':'POST','mode':mode,'url':url,'headers':headers,'body':body,'preview':{'method':'POST','url':url,'headers':redact_headers(headers),'body':body}}

def config_fingerprint(body:dict[str,Any])->str:
    data=json.loads(json.dumps(body)); data.get('query',{}).pop('queryText',None)
    canonical=json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:20]
