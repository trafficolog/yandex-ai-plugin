from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
try:
    from .ys_parse import parse_search_response
except ImportError:
    from ys_parse import parse_search_response
try:
    from ._http import auth_headers, redact_headers
except ImportError:
    from _http import auth_headers, redact_headers
OPERATIONS_BASE='https://operation.api.cloud.yandex.net/operations'
RETENTION_HOURS=12

def operation_record(query:str,operation:dict[str,Any])->dict[str,Any]:
    op_id=operation.get('id')
    if not op_id: raise ValueError('operation id is required')
    return {'query':query,'operation_id':op_id,'state':'done' if operation.get('done') else 'pending','submitted_at':operation.get('createdAt'),'last_response':operation}

def operation_status_request(operation_id:str,*,api_key:str|None=None,iam_token:str|None=None)->dict[str,Any]:
    op=(operation_id or '').strip()
    if not op: raise ValueError('operation_id is required')
    headers=auth_headers(api_key=api_key,iam_token=iam_token); url=f'{OPERATIONS_BASE}/{op}'
    return {'method':'GET','url':url,'headers':headers,'preview':{'method':'GET','url':url,'headers':redact_headers(headers)}}

def retention_state(submitted_at:str|None,*,now:datetime|None=None)->dict[str,Any]:
    if not submitted_at: return {'state':'unknown','age_hours':None,'retention_hours':RETENTION_HOURS}
    dt=datetime.fromisoformat(submitted_at.replace('Z','+00:00')); current=now or datetime.now(timezone.utc); age=(current-dt).total_seconds()/3600
    state='expired' if age>=RETENTION_HOURS else ('expiring_soon' if age>=RETENTION_HOURS-2 else 'available')
    return {'state':state,'age_hours':round(age,3),'retention_hours':RETENTION_HOURS}

def collect_operation_response(operation:dict[str,Any],response_format:str='FORMAT_XML')->dict[str,Any]:
    if not operation.get('done'):
        raise ValueError('operation is not complete')
    if operation.get('error'):
        raise RuntimeError(f"Yandex Search async operation failed: {operation['error']}")
    response=operation.get('response') or {}
    if 'rawData' not in response:
        raise ValueError('completed operation has no response.rawData')
    return parse_search_response(response,response_format)
