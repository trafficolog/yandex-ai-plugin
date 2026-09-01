from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit


def _host_path(user_id: int | str, host_id: str, suffix: str) -> str:
    return f"user/{user_id}/hosts/{host_id}/{suffix.lstrip('/')}"


def validate_host_https(host_url: str) -> None:
    parsed = urlsplit(host_url)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise ValueError("Yandex Webmaster feed mutations require an HTTPS host")


def list_request(user_id: int | str, host_id: str) -> dict[str, Any]:
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, "feeds/list")}


def start_request(
    user_id: int | str,
    host_id: str,
    *,
    host_url: str,
    feed_url: str,
    feed_type: str,
    region_ids: list[int] | None = None,
) -> dict[str, Any]:
    validate_host_https(host_url)
    if not feed_url or not feed_type:
        raise ValueError("feed_url and feed_type are required")
    body: dict[str, Any] = {"url": feed_url, "type": feed_type}
    if region_ids is not None:
        body["regionIds"] = list(region_ids)
    return {"method": "POST", "version": "v4", "path": _host_path(user_id, host_id, "feeds/add/start"), "body": body}


def status_request(user_id: int | str, host_id: str, request_id: str) -> dict[str, Any]:
    if not request_id:
        raise ValueError("request_id is required")
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, "feeds/add/info"), "params": {"requestId": request_id}}


def batch_add_request(user_id: int | str, host_id: str, *, host_url: str, feeds: list[dict[str, Any]]) -> dict[str, Any]:
    validate_host_https(host_url)
    if not feeds or len(feeds) > 50:
        raise ValueError("feeds must contain between 1 and 50 items")
    return {"method": "POST", "version": "v4", "path": _host_path(user_id, host_id, "feeds/batch/add"), "body": feeds}


def delete_request(user_id: int | str, host_id: str, *, host_url: str, urls: list[str]) -> dict[str, Any]:
    validate_host_https(host_url)
    if not urls:
        raise ValueError("at least one feed URL is required")
    return {"method": "DELETE", "version": "v4", "path": _host_path(user_id, host_id, "feeds/batch/remove"), "body": {"urls": list(urls)}}
