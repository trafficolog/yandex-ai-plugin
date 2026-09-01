from __future__ import annotations

from typing import Any

try:
    from .ywstat_api import validate_folder_id
except ImportError:
    from ywstat_api import validate_folder_id

ALLOWED_REGION_TYPES = {"REGION_ALL", "REGION_CITIES", "REGION_REGIONS"}
ALLOWED_DEVICES = {"DEVICE_ALL", "DEVICE_DESKTOP", "DEVICE_PHONE", "DEVICE_TABLET"}


def build_regions_payload(
    phrase: str,
    *,
    region: str = "REGION_ALL",
    devices: list[str] | None = None,
    folder_id: str | None = None,
) -> dict[str, Any]:
    phrase = phrase.strip()
    if not phrase:
        raise ValueError("phrase is required")
    if len(phrase) > 400:
        raise ValueError("phrase must not exceed 400 characters")
    if region not in ALLOWED_REGION_TYPES:
        raise ValueError(f"unsupported region type: {region}")
    payload: dict[str, Any] = {"phrase": phrase, "region": region}
    if devices is not None:
        if len(devices) > 3:
            raise ValueError("devices supports at most 3 values")
        invalid = [item for item in devices if item not in ALLOWED_DEVICES]
        if invalid:
            raise ValueError(f"unsupported device values: {invalid}")
        payload["devices"] = list(devices)
    normalized_folder = validate_folder_id(folder_id)
    if normalized_folder is not None:
        payload["folderId"] = normalized_folder
    return payload


def normalize_regions(response: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for row in response.get("results") or []:
        region_id = str(row.get("region", "")).strip()
        if not region_id:
            continue
        try:
            count = int(row.get("count", 0))
            share = float(row.get("share", 0.0))
            affinity = float(row.get("affinityIndex", 0.0))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid region row: {row!r}") from exc
        result.append(
            {
                "region_id": region_id,
                "count": count,
                "share": share,
                "affinity_index": affinity,
            }
        )
    return result


def flatten_region_tree(response: dict[str, Any]) -> list[dict[str, Any]]:
    flat: list[dict[str, Any]] = []

    def walk(nodes: list[dict[str, Any]], parent_id: str | None, path: list[str]) -> None:
        for node in nodes:
            region_id = str(node.get("id", "")).strip()
            label = str(node.get("label", "")).strip()
            if not region_id or not label:
                continue
            current_path = path + [label]
            flat.append(
                {
                    "id": region_id,
                    "label": label,
                    "parent_id": parent_id,
                    "path": current_path,
                }
            )
            children = node.get("children") or []
            if not isinstance(children, list):
                raise ValueError("region tree children must be a list")
            walk(children, region_id, current_path)

    roots = response.get("regions") or []
    if not isinstance(roots, list):
        raise ValueError("regions must be a list")
    walk(roots, None, [])
    return flat


def search_regions(response: dict[str, Any], query: str) -> list[dict[str, Any]]:
    needle = query.strip().casefold()
    if not needle:
        raise ValueError("query is required")
    return [item for item in flatten_region_tree(response) if needle in item["label"].casefold()]


def rank_regions(
    records: list[dict[str, Any]],
    *,
    by: str = "volume",
    limit: int | None = None,
) -> list[dict[str, Any]]:
    if by == "volume":
        key = lambda item: (item.get("count", 0), item.get("affinity_index", 0))
    elif by == "affinity":
        key = lambda item: (item.get("affinity_index", 0), item.get("count", 0))
    else:
        raise ValueError("by must be 'volume' or 'affinity'")
    ranked = sorted(records, key=key, reverse=True)
    if limit is None:
        return ranked
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive integer")
    return ranked[:limit]
