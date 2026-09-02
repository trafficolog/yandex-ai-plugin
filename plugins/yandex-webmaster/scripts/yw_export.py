from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit
from urllib.request import urlopen


def _host_path(user_id: int | str, host_id: str, suffix: str) -> str:
    return f"user/{user_id}/hosts/{host_id}/{suffix.lstrip('/')}"


def _validate_https_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise ValueError("artifact download URL must be absolute HTTPS")
    return url


def limits_request(user_id: int | str, host_id: str) -> dict[str, Any]:
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, "pro/limits")}


def regions_request(user_id: int | str, host_id: str) -> dict[str, Any]:
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, "pro/regions")}


def available_dates_request(user_id: int | str, host_id: str) -> dict[str, Any]:
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, "pro/serp/dates")}


def start_request(
    user_id: int | str,
    host_id: str,
    *,
    dates: list[str],
    paths: list[str],
    region_ids: list[int] | None = None,
    use_pro_tariff: bool = False,
) -> dict[str, Any]:
    if not dates:
        raise ValueError("dates must not be empty")
    if not paths:
        raise ValueError("paths must not be empty")
    body = {
        "dates": list(dates),
        "paths": list(paths),
        "region_ids": list(region_ids or []),
        "use_pro_tariff": bool(use_pro_tariff),
    }
    return {"method": "POST", "version": "v4", "path": _host_path(user_id, host_id, "pro/serp/queries/download"), "body": body}


def status_request(user_id: int | str, host_id: str, task_id: str) -> dict[str, Any]:
    if not task_id:
        raise ValueError("task_id is required")
    return {"method": "GET", "version": "v4", "path": _host_path(user_id, host_id, f"pro/serp/queries/download/{task_id}")}


def download_url(response: dict[str, Any]) -> str | None:
    if response.get("download_status") != "SUCCESS":
        return None
    value = response.get("url")
    if not isinstance(value, str) or not value:
        return None
    return _validate_https_url(value)


def download_to_file(
    url: str,
    output: Path,
    *,
    transport: Callable[[str], bytes] | None = None,
) -> Path:
    _validate_https_url(url)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if transport is not None:
        payload = transport(url)
    else:
        with urlopen(url, timeout=60) as response:
            payload = response.read()
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("download transport must return bytes")
    output.write_bytes(bytes(payload))
    return output
