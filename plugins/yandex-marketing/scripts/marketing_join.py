from __future__ import annotations
from collections import defaultdict
from .marketing_context import normalize_query, normalize_url_identity


def _group(records: list[dict], key_name: str) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        value = record.get(key_name)
        if value is None:
            continue
        grouped[str(value)].append(record)
    return dict(grouped)


def join_campaigns(records: list[dict]) -> dict[str, list[dict]]:
    return _group(records, 'campaign_id')


def join_goals(records: list[dict]) -> dict[str, list[dict]]:
    return _group(records, 'goal_id')


def join_queries(records: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        if record.get('query') is not None:
            grouped[normalize_query(record['query'])].append(record)
    return dict(grouped)


def join_landings(records: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        if not record.get('url'):
            continue
        url_key, tracking_params = normalize_url_identity(record['url'])
        item = dict(record)
        item['url_key'] = url_key
        if tracking_params:
            item['tracking_params'] = tracking_params
        else:
            item.pop('tracking_params', None)
        grouped[url_key].append(item)
    return dict(grouped)
