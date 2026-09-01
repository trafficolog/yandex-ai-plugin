from __future__ import annotations
import base64
import xml.etree.ElementTree as ET
from typing import Any

def decode_raw_data(raw_data:str|bytes)->str:
    if isinstance(raw_data,str): data=raw_data.encode('ascii')
    else: data=raw_data
    return base64.b64decode(data,validate=True).decode('utf-8',errors='replace')

def _text(node:ET.Element, path:str)->str|None:
    found=node.find(path)
    if found is None: return None
    text=''.join(found.itertext()).strip()
    return text or None

def parse_xml_results(xml_text:str)->list[dict[str,Any]]:
    root=ET.fromstring(xml_text); rows=[]
    for idx,doc in enumerate(root.findall('.//doc'),start=1):
        url=_text(doc,'url')
        if not url: continue
        passages=[''.join(p.itertext()).strip() for p in doc.findall('./passages/passage')]
        snippet=' '.join(p for p in passages if p) or _text(doc,'headline') or ''
        rows.append({'rank':len(rows)+1,'url':url,'domain':_text(doc,'domain'),'title':_text(doc,'title') or '','snippet':snippet,'modified_at':_text(doc,'modtime')})
    return rows

def parse_search_response(payload:dict[str,Any],response_format:str)->dict[str,Any]:
    raw=decode_raw_data(payload['rawData'])
    if response_format=='FORMAT_XML': return {'format':'xml','raw':raw,'results':parse_xml_results(raw)}
    if response_format=='FORMAT_HTML': return {'format':'html','raw':raw}
    raise ValueError('unsupported response_format')
