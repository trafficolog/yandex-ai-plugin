from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

try:
    from .ys_request import MAX_RESULTS
except ImportError:
    from ys_request import MAX_RESULTS


def normalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower()
    if not scheme or not host:
        raise ValueError("absolute URL is required")
    port = parsed.port
    if port is None or (scheme == "https" and port == 443) or (scheme == "http" and port == 80):
        netloc = host
    else:
        netloc = f"{host}:{port}"
    path = parsed.path or "/"
    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)), doseq=True)
    return urlunsplit((scheme, netloc, path, query, ""))


def _fingerprint(config: dict[str, Any]) -> str:
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:20]


def build_snapshot(
    query: str,
    results: list[dict[str, Any]],
    *,
    search_type: str = "SEARCH_TYPE_RU",
    region: int | None = None,
    page: int = 0,
    group_mode: str = "GROUP_MODE_FLAT",
    groups_on_page: int = 20,
    docs_in_group: int = 1,
    results_within: str = "WITHIN_ALL_TIME",
    sort_mode: str = "SORT_MODE_BY_RELEVANCE",
    family_mode: str = "FAMILY_MODE_MODERATE",
    fix_typo_mode: str = "FIX_TYPO_MODE_ON",
    response_format: str = "FORMAT_XML",
    collected_at: str | None = None,
) -> dict[str, Any]:
    if group_mode != "GROUP_MODE_FLAT" or docs_in_group != 1:
        raise ValueError("structured SEO snapshots require GROUP_MODE_FLAT and docs_in_group=1")
    if page < 0 or groups_on_page < 1:
        raise ValueError("page must be non-negative and groups_on_page positive")

    requested_per_page = groups_on_page * docs_in_group
    window_start = page * requested_per_page
    window_end = window_start + requested_per_page
    if requested_per_page > MAX_RESULTS:
        raise ValueError(f"snapshot page exceeds {MAX_RESULTS}-result API ceiling")
    if window_start >= MAX_RESULTS:
        raise ValueError(f"snapshot page starts outside the {MAX_RESULTS}-result API ceiling")
    if window_end > MAX_RESULTS:
        raise ValueError(f"snapshot result window crosses the {MAX_RESULTS}-result API ceiling")
    if len(results) > requested_per_page:
        raise ValueError("snapshot contains more results than the configured result window")

    config = {
        "search_type": search_type,
        "region": region,
        "page": page,
        "group_mode": group_mode,
        "groups_on_page": groups_on_page,
        "docs_in_group": docs_in_group,
        "results_within": results_within,
        "sort_mode": sort_mode,
        "family_mode": family_mode,
        "fix_typo_mode": fix_typo_mode,
        "response_format": response_format,
    }
    normalized = []
    for position, item in enumerate(results, start=1):
        row = dict(item)
        rank = window_start + position
        if rank > MAX_RESULTS:
            raise ValueError(f"observed rank cannot exceed {MAX_RESULTS}")
        row["position_on_page"] = position
        row["rank"] = rank
        row["url_key"] = normalize_url(row["url"])
        row["host"] = urlsplit(row["url_key"]).hostname
        normalized.append(row)
    return {
        "query": query,
        **config,
        "max_supported_results": MAX_RESULTS,
        "window_start": window_start,
        "window_end": window_end,
        "reaches_result_ceiling": window_end == MAX_RESULTS,
        "config_fingerprint": _fingerprint(config),
        "collected_at": collected_at or datetime.now(timezone.utc).isoformat(),
        "results": normalized,
    }
