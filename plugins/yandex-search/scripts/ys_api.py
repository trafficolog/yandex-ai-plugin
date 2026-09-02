from __future__ import annotations
from typing import Any
SYNC_URL='https://searchapi.api.cloud.yandex.net/v2/web/search'
ASYNC_URL='https://searchapi.api.cloud.yandex.net/v2/web/searchAsync'
PRICE_RUB_PER_1000={'sync':{'day':488.0,'night':366.0},'async':{'day':30.5,'night':25.41}}
PRICE_VERIFIED_AT='2026-09-01'
QUOTAS={'sync_per_hour':10000,'sync_rps':10,'async_per_hour':35000,'async_rps':10,'async_result_rps':10}

def validate_query_text(query:str)->str:
    value=(query or '').strip()
    if not value: raise ValueError('query must not be empty')
    if len(value)>400: raise ValueError('query must not exceed 400 characters')
    if len(value.split())>40: raise ValueError('query must not exceed 40 words')
    return value

def estimate_cost(requests:int,*,mode:str,period:str='day')->dict[str,Any]:
    if not isinstance(requests,int) or requests<0: raise ValueError('requests must be a non-negative integer')
    if mode not in PRICE_RUB_PER_1000 or period not in ('day','night'): raise ValueError('unsupported mode or period')
    rate=PRICE_RUB_PER_1000[mode][period]
    return {'requests':requests,'mode':mode,'period':period,'rub_per_1000':rate,'estimated_rub':round(requests*rate/1000,6),'verified_at':PRICE_VERIFIED_AT,'billing_guarantee':False}

def recommend_mode(requests:int,*,interactive_threshold:int=5)->dict[str,Any]:
    if requests<0: raise ValueError('requests must be non-negative')
    mode='sync' if requests<=interactive_threshold else 'async'
    return {'requests':requests,'mode':mode,'reason':'interactive workload' if mode=='sync' else 'batch workload; deferred mode is materially cheaper'}
