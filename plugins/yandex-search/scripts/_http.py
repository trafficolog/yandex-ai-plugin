from __future__ import annotations
import json
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.request import Request, urlopen

def auth_headers(*, api_key: str|None=None, iam_token: str|None=None) -> dict[str,str]:
    api_key=(api_key or '').strip(); iam_token=(iam_token or '').strip()
    if bool(api_key)==bool(iam_token): raise ValueError('Provide exactly one of api_key or iam_token')
    return {'Authorization': f'Api-Key {api_key}' if api_key else f'Bearer {iam_token}', 'Accept':'application/json','Content-Type':'application/json'}

def redact_headers(headers: dict[str,str]) -> dict[str,str]:
    out=dict(headers); value=out.get('Authorization','')
    if value.startswith('Api-Key '): out['Authorization']='Api-Key ***'
    elif value.startswith('Bearer '): out['Authorization']='Bearer ***'
    return out

def request_json(method:str,url:str,headers:dict[str,str],body:Any|None=None,*,timeout:int=60,opener:Callable[...,Any]=urlopen)->Any:
    data=None if body is None else json.dumps(body,ensure_ascii=False).encode('utf-8')
    req=Request(url,data=data,headers=headers,method=method.upper())
    try:
        with opener(req,timeout=timeout) as resp: raw=resp.read()
    except HTTPError as exc:
        text=exc.read(4096).decode('utf-8',errors='replace')
        raise RuntimeError(f'Yandex Search API HTTP {exc.code}: {text}') from exc
    if not raw: return None
    text=raw.decode('utf-8')
    try: return json.loads(text)
    except json.JSONDecodeError: return text
