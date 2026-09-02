from __future__ import annotations

import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


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


def _normalize_region_ids(value) -> tuple[str, ...] | None:
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


def classify_geo_alignment(items: list[dict]) -> str:
    """Compare geography only when its semantic type is the same.

    `visitor_region` and `serp_region` may share a numeric region ID but describe
    different evidence and therefore are not interchangeable.
    """
    if not items:
        return "UNKNOWN"

    normalized: list[tuple[str, tuple[str, ...]]] = []
    for item in items:
        geo_type = str(item.get("geo_type") or "").strip()
        region_ids = _normalize_region_ids(item.get("region_ids"))
        if not geo_type or region_ids is None:
            return "UNKNOWN"
        normalized.append((geo_type, region_ids))

    geo_types = {geo_type for geo_type, _ in normalized}
    if len(geo_types) > 1:
        return "MISMATCHED"
    region_sets = {region_ids for _, region_ids in normalized}
    if len(region_sets) == 1:
        return "EXACT"
    return "MISMATCHED"
