from __future__ import annotations
from typing import Any, Iterable
try:
    from .ys_api import estimate_cost, recommend_mode, validate_query_text, QUOTAS
except ImportError:
    from ys_api import estimate_cost, recommend_mode, validate_query_text, QUOTAS

def plan_batch(queries:Iterable[str],*,period:str='day',interactive_threshold:int=5)->dict[str,Any]:
    unique=[]; seen=set()
    for q in queries:
        value=validate_query_text(q)
        if value not in seen: seen.add(value); unique.append(value)
    recommendation=recommend_mode(len(unique),interactive_threshold=interactive_threshold)
    return {'queries':unique,'requests':len(unique),'recommended_mode':recommendation['mode'],'recommendation_reason':recommendation['reason'],'cost_preview':{'sync':estimate_cost(len(unique),mode='sync',period=period),'async':estimate_cost(len(unique),mode='async',period=period)},'quotas':QUOTAS,'automatic_execution':False}
