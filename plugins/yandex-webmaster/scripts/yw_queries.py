from __future__ import annotations

from typing import Any


def _host_path(user_id: int | str, host_id: str, suffix: str) -> str:
    return f"user/{user_id}/hosts/{host_id}/{suffix.lstrip('/')}"


def popular_request(
    user_id: int | str,
    host_id: str,
    *,
    order_by: str = "TOTAL_SHOWS",
    device: str = "ALL",
    date_from: str | None = None,
    date_to: str | None = None,
    offset: int = 0,
    limit: int = 500,
) -> dict[str, Any]:
    if limit < 1 or limit > 500:
        raise ValueError("popular query limit must be between 1 and 500")
    params: dict[str, Any] = {
        "order_by": order_by,
        "device_type_indicator": device,
        "query_indicator": ["TOTAL_SHOWS", "TOTAL_CLICKS", "AVG_SHOW_POSITION", "AVG_CLICK_POSITION"],
        "offset": offset,
        "limit": limit,
    }
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, "search-queries/popular"), "params": params}


def history_request(
    user_id: int | str,
    host_id: str,
    *,
    date_from: str,
    date_to: str | None = None,
    query_id: str | None = None,
    device: str = "ALL",
) -> dict[str, Any]:
    target = f"search-queries/{query_id}/history" if query_id else "search-queries/all/history"
    params: dict[str, Any] = {
        "date_from": date_from,
        "device_type_indicator": device,
        "query_indicator": ["TOTAL_SHOWS", "TOTAL_CLICKS", "AVG_SHOW_POSITION"],
    }
    if date_to:
        params["date_to"] = date_to
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, target), "params": params}


def analytics_request(user_id: int | str, host_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(payload)
    limit = body.get("limit", 500)
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("query analytics limit must be a positive integer")
    return {"method": "POST", "version": "v4", "path": _host_path(user_id, host_id, "query-analytics/list"), "body": body}


def coverage_note(kind: str, *, returned: int, limit: int | None = None) -> str:
    if kind == "popular":
        suffix = f" (returned {returned}, request limit {limit})" if limit is not None else f" (returned {returned})"
        return "Yandex popular queries is a top-N view and is not complete query coverage" + suffix + "."
    return f"Returned {returned} rows; completeness depends on the endpoint, filters and pagination."
