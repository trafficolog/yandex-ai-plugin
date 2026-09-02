from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit
from urllib.request import urlopen

DOWNLOAD_URL_LIFETIME_HOURS = 24


def _host_path(user_id: int | str, host_id: str, suffix: str) -> str:
    return f"user/{user_id}/hosts/{host_id}/{suffix.lstrip('/')}"


def _validate_https_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise ValueError("artifact download URL must be absolute HTTPS")
    return url


def _validate_export_paths(paths: list[str]) -> list[str]:
    normalized: list[str] = []
    for path in paths:
        if not isinstance(path, str) or not path.strip():
            raise ValueError("each export path must be a non-empty string")
        value = path.strip()
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            raise ValueError("export paths must be host-relative paths, not full URLs")
        if not value.startswith("/"):
            raise ValueError("export paths must start with '/'")
        normalized.append(value)
    return normalized


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
        "paths": _validate_export_paths(paths),
        "region_ids": list(region_ids or []),
        "use_pro_tariff": "true" if use_pro_tariff else "false",
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


def _aware_datetime(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def export_state(
    response: dict[str, Any],
    *,
    completed_at: datetime | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    status = response.get("download_status")
    if status == "IN_PROGRESS":
        return {"state": "PENDING", "download_status": status, "download_age": "UNKNOWN"}
    if status == "FAILED":
        return {
            "state": "FAILED",
            "download_status": status,
            "error_code": response.get("error_code"),
            "error_message": response.get("error_message"),
            "download_age": "UNKNOWN",
        }
    if status != "SUCCESS":
        raise ValueError(f"unsupported download_status: {status!r}")

    value = response.get("url")
    if not isinstance(value, str) or not value:
        return {"state": "DOWNLOAD_URL_MISSING", "download_status": status, "download_age": "UNKNOWN"}
    url = _validate_https_url(value)
    result: dict[str, Any] = {
        "state": "READY",
        "download_status": status,
        "url": url,
        "download_age": "UNKNOWN",
    }
    if completed_at is None:
        return result
    completed = _aware_datetime(completed_at, "completed_at")
    observed_now = _aware_datetime(now or datetime.now(timezone.utc), "now")
    age_hours = (observed_now - completed).total_seconds() / 3600
    result["download_age"] = "KNOWN"
    result["download_age_hours"] = age_hours
    if age_hours > DOWNLOAD_URL_LIFETIME_HOURS:
        result["state"] = "DOWNLOAD_EXPIRED"
    return result


def plan_quota(
    requested_units: int,
    *,
    known_remaining: int | None = None,
    initialization_response: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(requested_units, int) or requested_units < 0:
        raise ValueError("requested_units must be a non-negative integer")

    quota_source = "caller"
    quota_used = None
    remaining = known_remaining
    if initialization_response is not None and initialization_response.get("quota_remaining") is not None:
        remaining = initialization_response.get("quota_remaining")
        quota_used = initialization_response.get("quota_used")
        quota_source = "initialization_response"

    if remaining is None:
        return {
            "status": "QUOTA_USAGE_UNKNOWN",
            "requested_units": requested_units,
            "known_remaining": None,
            "quota_used": quota_used,
            "quota_source": "unknown",
        }
    try:
        remaining_value = int(remaining)
    except (TypeError, ValueError) as exc:
        raise ValueError("known quota remaining must be an integer") from exc
    if remaining_value < 0:
        raise ValueError("known quota remaining must not be negative")
    return {
        "status": "WITHIN_KNOWN_QUOTA" if requested_units <= remaining_value else "QUOTA_LIMIT_RISK",
        "requested_units": requested_units,
        "known_remaining": remaining_value,
        "quota_used": quota_used,
        "quota_source": quota_source,
    }


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
