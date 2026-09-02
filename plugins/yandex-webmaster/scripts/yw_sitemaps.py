from __future__ import annotations

from typing import Any

_VERSIONS = {
    "list": "v4",
    "user_list": "v4",
    "info": "v4",
    "add": "v4",
    "delete": "v4",
    "priority_limit": "v4.1",
    "priority_recrawl": "v4.1",
}


def endpoint_version(operation: str) -> str:
    try:
        return _VERSIONS[operation]
    except KeyError as exc:
        raise ValueError(f"Unknown sitemap operation: {operation}") from exc


def _host_path(user_id: int | str, host_id: str, suffix: str) -> str:
    return f"user/{user_id}/hosts/{host_id}/{suffix.lstrip('/')}"


def list_request(user_id: int | str, host_id: str, *, offset: int = 0, limit: int = 100) -> dict[str, Any]:
    return {"method": "GET", "version": endpoint_version("list"), "path": _host_path(user_id, host_id, "sitemaps"), "params": {"offset": offset, "limit": limit}}


def user_list_request(user_id: int | str, host_id: str, *, offset: int = 0, limit: int = 100) -> dict[str, Any]:
    return {"method": "GET", "version": endpoint_version("user_list"), "path": _host_path(user_id, host_id, "user-added-sitemaps"), "params": {"offset": offset, "limit": limit}}


def add_request(user_id: int | str, host_id: str, url: str) -> dict[str, Any]:
    if not url:
        raise ValueError("sitemap URL is required")
    return {"method": "POST", "version": endpoint_version("add"), "path": _host_path(user_id, host_id, "user-added-sitemaps"), "body": {"url": url}}


def delete_request(user_id: int | str, host_id: str, sitemap_id: str) -> dict[str, Any]:
    if not sitemap_id:
        raise ValueError("sitemap_id is required")
    return {"method": "DELETE", "version": endpoint_version("delete"), "path": _host_path(user_id, host_id, f"user-added-sitemaps/{sitemap_id}")}


def priority_limit_request(user_id: int | str, host_id: str) -> dict[str, Any]:
    return {"method": "GET", "version": endpoint_version("priority_limit"), "path": _host_path(user_id, host_id, "sitemaps/recrawl")}


def priority_recrawl_request(user_id: int | str, host_id: str, sitemap_id: str, *, parent_id: str | None = None) -> dict[str, Any]:
    if not sitemap_id:
        raise ValueError("sitemap_id is required")
    params = {"parent_id": parent_id} if parent_id else {}
    return {
        "method": "POST",
        "version": endpoint_version("priority_recrawl"),
        "path": _host_path(user_id, host_id, f"sitemaps/{sitemap_id}/recrawl"),
        "params": params,
        "body": None,
    }


def priority_state(response: dict[str, Any]) -> dict[str, Any]:
    recrawl = response.get("sitemap_recrawl_info") or {}
    quota = response.get("host_sitemaps_recrawl_limit_info") or response
    return {
        "pending": recrawl.get("pending"),
        "allowed": recrawl.get("allowed"),
        "last_request_time": recrawl.get("last_request_time"),
        "monthly_limit_requests": quota.get("monthly_limit_requests"),
        "requests_count": quota.get("requests_count"),
        "nearest_allowed_day": quota.get("nearest_allowed_day"),
    }
