from __future__ import annotations

from typing import Any

try:
    from .ywstat_api import validate_folder_id
except ImportError:  # CLI execution
    from ywstat_api import validate_folder_id

ALLOWED_DEVICES = {"DEVICE_ALL", "DEVICE_DESKTOP", "DEVICE_PHONE", "DEVICE_TABLET"}
MAX_ASSOCIATIONS = 20


def _validate_phrase(phrase: str) -> str:
    value = phrase.strip()
    if not value:
        raise ValueError("phrase is required")
    if len(value) > 400:
        raise ValueError("phrase must not exceed 400 characters")
    return value


def _validate_devices(devices: list[str] | None) -> list[str] | None:
    if devices is None:
        return None
    if len(devices) > 3:
        raise ValueError("devices supports at most 3 values")
    invalid = [item for item in devices if item not in ALLOWED_DEVICES]
    if invalid:
        raise ValueError(f"unsupported device values: {invalid}")
    return list(devices)


def build_top_payload(
    phrase: str,
    *,
    num_phrases: int = 50,
    regions: list[str] | None = None,
    devices: list[str] | None = None,
    folder_id: str | None = None,
) -> dict[str, Any]:
    phrase = _validate_phrase(phrase)
    if not isinstance(num_phrases, int) or not 1 <= num_phrases <= 2000:
        raise ValueError("num_phrases must be an integer from 1 to 2000")
    if regions is not None and len(regions) > 100:
        raise ValueError("regions supports at most 100 IDs")
    payload: dict[str, Any] = {"phrase": phrase, "numPhrases": num_phrases}
    if regions is not None:
        payload["regions"] = [str(item) for item in regions]
    normalized_devices = _validate_devices(devices)
    if normalized_devices is not None:
        payload["devices"] = normalized_devices
    normalized_folder = validate_folder_id(folder_id)
    if normalized_folder is not None:
        payload["folderId"] = normalized_folder
    return payload


def _count(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid Wordstat count: {value!r}") from exc


def _normalize_records(
    rows: list[dict[str, Any]] | None,
    *,
    seed: str,
    relation: str,
    operator_expression: str | None,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in rows or []:
        phrase = str(row.get("phrase", "")).strip()
        if not phrase:
            continue
        result.append(
            {
                "phrase": phrase,
                "count": _count(row.get("count", 0)),
                "relation": relation,
                "sources": [seed],
                "operator_expression": operator_expression,
            }
        )
    return result


def normalize_top_response(
    response: dict[str, Any],
    *,
    seed: str,
    operator_expression: str | None = None,
) -> dict[str, Any]:
    seed = _validate_phrase(seed)
    nested = _normalize_records(
        response.get("results"),
        seed=seed,
        relation="nested",
        operator_expression=operator_expression,
    )
    associations = _normalize_records(
        response.get("associations"),
        seed=seed,
        relation="association",
        operator_expression=operator_expression,
    )
    associations_count = len(associations)
    return {
        "seed": seed,
        "total_count": _count(response.get("totalCount", 0)),
        "results": nested,
        "associations": associations,
        "records": nested + associations,
        "coverage": {
            "associations_cap": MAX_ASSOCIATIONS,
            "associations_count": associations_count,
            "associations_truncated": associations_count >= MAX_ASSOCIATIONS,
        },
    }
