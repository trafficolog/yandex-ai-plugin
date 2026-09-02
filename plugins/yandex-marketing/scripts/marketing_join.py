from __future__ import annotations
from collections import defaultdict
from .marketing_context import normalize_query, normalize_url


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
        if record.get('url'):
            grouped[normalize_url(record['url'])].append(record)
    return dict(grouped)
