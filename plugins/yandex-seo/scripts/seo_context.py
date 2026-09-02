from __future__ import annotations

import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

GEO_FIELD_TYPES = (
    ("wordstat_region_id", "wordstat_query_region"),
    ("wordstat_region_ids", "wordstat_query_region"),
    ("search_region_id", "search_ranking_region"),
    ("webmaster_region_id", "webmaster_query_region"),
    ("webmaster_region_ids", "webmaster_query_region"),
    ("metrika_visitor_region", "metrika_visitor_region"),
    ("metrika_visitor_region_ids", "metrika_visitor_region"),
)
SEARCH_CONTEXT_FIELDS = (
    "search_type",
    "family_mode",
    "fix_typo_mode",
    "sort_mode",
    "results_within",
    "group_mode",
    "docs_in_group",
)


def normalize_query(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.casefold().split())


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    host = (parts.hostname or "").lower()
    port = parts.port
    if port and not ((scheme == "https" and port == 443) or (scheme == "http" and port == 80)):
        netloc = f"{host}:{port}"
    else:
        netloc = host
    path = parts.path or "/"
    query = urlencode(sorted(parse_qsl(parts.query, keep_blank_values=True)), doseq=True)
    return urlunsplit((scheme, netloc, path, query, ""))


def classify_period_alignment(items: list[dict]) -> str:
    if not items:
        return "UNKNOWN"

    periods: list[tuple[str, str]] = []
    rolling_windows: list[str] = []
    for item in items:
        period = item.get("period")
        if isinstance(period, dict) and period.get("from") and period.get("to"):
            periods.append((str(period["from"]), str(period["to"])))
            continue
        window = item.get("window")
        if isinstance(window, str) and window.strip():
            rolling_windows.append(window.strip())
            continue
        return "UNKNOWN"

    if periods and len(set(periods)) > 1:
        return "MISMATCHED"
    if periods and rolling_windows:
        return "APPROXIMATE"
    if rolling_windows:
        return "EXACT" if len(set(rolling_windows)) == 1 and len(rolling_windows) == len(items) else "APPROXIMATE"
    return "EXACT"


def _normalize_values(value) -> tuple[str, ...] | None:
    if value is None:
        return None
    if isinstance(value, (str, int)):
        values = [value]
    elif isinstance(value, (list, tuple, set)):
        values = list(value)
    else:
        return None
    normalized = tuple(sorted({str(item).strip() for item in values if str(item).strip()}))
    return normalized or None


def _geo_context(item: dict) -> tuple[str, tuple[str, ...]] | None:
    generic_type = str(item.get("geo_type") or "").strip()
    if generic_type:
        region_ids = _normalize_values(item.get("region_ids"))
        return (generic_type, region_ids) if region_ids is not None else None

    found: list[tuple[str, tuple[str, ...]]] = []
    for field, semantic_type in GEO_FIELD_TYPES:
        if field not in item:
            continue
        region_ids = _normalize_values(item.get(field))
        if region_ids is None:
            return None
        found.append((semantic_type, region_ids))
    if len(found) != 1:
        return None
    return found[0]


def classify_geo_alignment(items: list[dict]) -> str:
    """Compare geography only when its semantic type is the same."""
    if not items:
        return "UNKNOWN"

    normalized: list[tuple[str, tuple[str, ...]]] = []
    for item in items:
        context = _geo_context(item)
        if context is None:
            return "UNKNOWN"
        normalized.append(context)

    geo_types = {geo_type for geo_type, _ in normalized}
    if len(geo_types) > 1:
        return "MISMATCHED"
    region_sets = {region_ids for _, region_ids in normalized}
    return "EXACT" if len(region_sets) == 1 else "MISMATCHED"


def classify_search_alignment(items: list[dict]) -> str:
    if not items:
        return "UNKNOWN"
    if any(not str(item.get("search_type") or "").strip() for item in items):
        return "UNKNOWN"

    material_fields = {
        field
        for field in SEARCH_CONTEXT_FIELDS
        if any(item.get(field) is not None for item in items)
    }
    fingerprints: list[tuple[tuple[str, str], ...]] = []
    for item in items:
        pairs: list[tuple[str, str]] = []
        for field in sorted(material_fields):
            value = item.get(field)
            if value is None:
                return "UNKNOWN"
            pairs.append((field, str(value)))
        fingerprints.append(tuple(pairs))
    return "EXACT" if len(set(fingerprints)) == 1 else "MISMATCHED"


def classify_device_alignment(items: list[dict]) -> str:
    if not items:
        return "UNKNOWN"
    normalized: list[tuple[str, ...]] = []
    for item in items:
        value = item.get("devices") if "devices" in item else item.get("device")
        devices = _normalize_values(value)
        if devices is None:
            return "UNKNOWN"
        normalized.append(devices)
    return "EXACT" if len(set(normalized)) == 1 else "MISMATCHED"
