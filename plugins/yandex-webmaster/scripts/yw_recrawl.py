from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit


def _host_path(user_id: int | str, host_id: str, suffix: str) -> str:
    return f"user/{user_id}/hosts/{host_id}/{suffix.lstrip('/')}"


def validate_url_for_host(url: str, host_url: str) -> None:
    target = urlsplit(url)
    host = urlsplit(host_url)
    if target.scheme not in {"http", "https"} or not target.hostname:
        raise ValueError("recrawl URL must be an absolute http(s) URL")
    if host.scheme not in {"http", "https"} or not host.hostname:
        raise ValueError("host_url must be an absolute http(s) URL")
    if target.scheme.lower() != host.scheme.lower():
        raise ValueError("recrawl URL scheme does not match the selected host")
    if target.hostname.lower().rstrip(".") != host.hostname.lower().rstrip("."):
        raise ValueError("recrawl URL does not belong to the selected host")

    def effective_port(parsed):
        if parsed.port is not None:
            return parsed.port
        return 443 if parsed.scheme.lower() == "https" else 80

    if effective_port(target) != effective_port(host):
        raise ValueError("recrawl URL port does not match the selected host")


def quota_request(user_id: int | str, host_id: str) -> dict[str, Any]:
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, "recrawl/quota")}


def queue_request(user_id: int | str, host_id: str, *, offset: int = 0, limit: int = 100, date_from: str | None = None, date_to: str | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {"offset": offset, "limit": limit}
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, "recrawl/queue"), "params": params}


def task_request(user_id: int | str, host_id: str, task_id: str) -> dict[str, Any]:
    if not task_id:
        raise ValueError("task_id is required")
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, f"recrawl/queue/{task_id}")}


def submit_request(user_id: int | str, host_id: str, url: str, *, host_url: str) -> dict[str, Any]:
    validate_url_for_host(url, host_url)
    return {"method": "POST", "version": "v4", "path": _host_path(user_id, host_id, "recrawl/queue"), "body": {"url": url}}


def normalize_submit_error(status: int, code: str | None) -> dict[str, Any] | None:
    if status == 409 and code == "URL_ALREADY_ADDED":
        return {
            "state": "already_queued",
            "retry_required": False,
            "message": "URL is already in the Yandex Webmaster recrawl queue.",
        }
    return None
