from __future__ import annotations

from collections import defaultdict
from .seo_context import normalize_query, normalize_url_identity


def join_queries(records: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        raw = record.get('query') or record.get('query_raw')
        if not isinstance(raw, str) or not raw.strip():
            continue
        out[normalize_query(raw)].append(record)
    return dict(out)


def join_pages(records: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        raw = record.get('url') or record.get('page_url') or record.get('startURL')
        if not isinstance(raw, str) or not raw.strip():
            continue
        url_key, tracking_params = normalize_url_identity(raw)
        item = dict(record)
        item['url_key'] = url_key
        if tracking_params:
            item['tracking_params'] = tracking_params
        else:
            item.pop('tracking_params', None)
        out[url_key].append(item)
    return dict(out)
