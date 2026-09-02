from __future__ import annotations

import re
from datetime import datetime
from typing import Any

try:
    from .ywstat_api import validate_folder_id
except ImportError:
    from ywstat_api import validate_folder_id

ALLOWED_PERIODS = {"PERIOD_MONTHLY", "PERIOD_WEEKLY", "PERIOD_DAILY"}
ALLOWED_DEVICES = {"DEVICE_ALL", "DEVICE_DESKTOP", "DEVICE_PHONE", "DEVICE_TABLET"}


def _parse_datetime(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("date must be a non-empty RFC3339 string")
    normalized = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"invalid RFC3339 date: {value}") from exc


def _has_unsupported_operator(expression: str) -> bool:
    # '-' is an operator only when it starts a token; keep hyphenated words valid.
    if re.search(r"(^|\s)-\S", expression):
        return True
    return any(symbol in expression for symbol in ['!', '"', '[', ']', '(', ')', '|'])


def validate_expression_for_period(phrase: str, period: str) -> None:
    if period not in ALLOWED_PERIODS:
        raise ValueError(f"unsupported period: {period}")
    if not isinstance(phrase, str) or not phrase.strip():
        raise ValueError("phrase is required")
    if len(phrase.strip()) > 400:
        raise ValueError("phrase must not exceed 400 characters")
    if period in {"PERIOD_MONTHLY", "PERIOD_WEEKLY"} and _has_unsupported_operator(phrase):
        raise ValueError(
            "Plugin compatibility guard cannot guarantee monthly/weekly Dynamics behavior for this "
            "operator expression; use PERIOD_DAILY for the supported Wordstat operator path"
        )


def build_dynamics_payload(
    phrase: str,
    *,
    period: str,
    from_date: str,
    to_date: str,
    regions: list[str] | None = None,
    devices: list[str] | None = None,
    folder_id: str | None = None,
) -> dict[str, Any]:
    phrase = phrase.strip()
    validate_expression_for_period(phrase, period)
    start = _parse_datetime(from_date)
    end = _parse_datetime(to_date)
    if start > end:
        raise ValueError("from_date must not be after to_date")
    if regions is not None and len(regions) > 100:
        raise ValueError("regions supports at most 100 IDs")
    if devices is not None:
        if len(devices) > 3:
            raise ValueError("devices supports at most 3 values")
        invalid = [item for item in devices if item not in ALLOWED_DEVICES]
        if invalid:
            raise ValueError(f"unsupported device values: {invalid}")
    payload: dict[str, Any] = {
        "phrase": phrase,
        "period": period,
        "fromDate": from_date,
        "toDate": to_date,
    }
    if regions is not None:
        payload["regions"] = [str(item) for item in regions]
    if devices is not None:
        payload["devices"] = list(devices)
    normalized_folder = validate_folder_id(folder_id)
    if normalized_folder is not None:
        payload["folderId"] = normalized_folder
    return payload


def normalize_series(response: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in response.get("results") or []:
        date = str(row.get("date", "")).strip()
        if not date:
            continue
        try:
            count = int(row.get("count", 0))
            share = float(row.get("share", 0.0))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid dynamics row: {row!r}") from exc
        result.append({"date": date, "count": count, "share": share})
    return sorted(result, key=lambda item: item["date"])
