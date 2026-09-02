from __future__ import annotations

from typing import Any


def _host_path(user_id: int | str, host_id: str, suffix: str) -> str:
    return f"user/{user_id}/hosts/{host_id}/{suffix.lstrip('/')}"


def _dates(date_from: str | None, date_to: str | None) -> dict[str, str]:
    params: dict[str, str] = {}
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    return params


def indexing_history_request(user_id: int | str, host_id: str, *, date_from: str | None = None, date_to: str | None = None) -> dict[str, Any]:
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, "indexing/history"), "params": _dates(date_from, date_to)}


def in_search_request(user_id: int | str, host_id: str, *, date_from: str | None = None, date_to: str | None = None) -> dict[str, Any]:
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, "search-urls/in-search/history"), "params": _dates(date_from, date_to)}


def search_events_request(user_id: int | str, host_id: str, *, date_from: str | None = None, date_to: str | None = None) -> dict[str, Any]:
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, "search-urls/events/history"), "params": _dates(date_from, date_to)}


def important_urls_request(user_id: int | str, host_id: str, *, offset: int = 0, limit: int = 100) -> dict[str, Any]:
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, "important-urls"), "params": {"offset": offset, "limit": limit}}


def archive_start_request(user_id: int | str, host_id: str) -> dict[str, Any]:
    return {"method": "POST", "version": "v4", "path": _host_path(user_id, host_id, "indexing/archive"), "body": None}


def archive_status_request(user_id: int | str, host_id: str, task_id: str) -> dict[str, Any]:
    if not task_id:
        raise ValueError("task_id is required")
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, f"indexing/archive/{task_id}")}


def archive_download_url(response: dict[str, Any]) -> str | None:
    if response.get("state") != "DONE":
        return None
    value = response.get("download_url")
    return value if isinstance(value, str) and value else None
