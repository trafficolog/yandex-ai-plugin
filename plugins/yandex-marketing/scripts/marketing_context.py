from __future__ import annotations

from datetime import date
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

MATERIAL_KPI_FIELDS = (
    "business_objective",
    "goal_ids",
    "attribution_model",
    "metric_basis",
    "currency",
    "vat_basis",
    "period",
)


def normalize_query(text: str) -> str:
    value = unicodedata.normalize("NFKC", str(text)).casefold().strip()
    return " ".join(value.split())


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    host = (parts.hostname or "").lower()
    port = parts.port
    if port and not ((scheme == "https" and port == 443) or (scheme == "http" and port == 80)):
        host = f"{host}:{port}"
    path = parts.path or "/"
    query = urlencode(sorted(parse_qsl(parts.query, keep_blank_values=True)), doseq=True)
    return urlunsplit((scheme, host, path, query, ""))


def kpi_fingerprint(data: dict) -> dict:
    result = {key: data.get(key) for key in MATERIAL_KPI_FIELDS}
    goals = result.get("goal_ids")
    if goals is not None:
        result["goal_ids"] = sorted(str(item) for item in goals)
    period = result.get("period")
    if isinstance(period, dict):
        result["period"] = {"from": period.get("from"), "to": period.get("to")}
    return result


def _missing_material_fields(fingerprint: dict) -> list[str]:
    missing: list[str] = []
    for key in MATERIAL_KPI_FIELDS:
        value = fingerprint.get(key)
        if key == "period":
            if not isinstance(value, dict) or not value.get("from") or not value.get("to"):
                missing.append(key)
        elif key == "goal_ids":
            if not value:
                missing.append(key)
        elif value is None or value == "":
            missing.append(key)
    return missing


def compare_kpi_fingerprints(left: dict, right: dict) -> dict:
    first = kpi_fingerprint(left)
    second = kpi_fingerprint(right)
    missing = sorted(set(_missing_material_fields(first) + _missing_material_fields(second)))
    mismatches = [
        key
        for key in MATERIAL_KPI_FIELDS
        if key not in missing and first.get(key) != second.get(key)
    ]
    return {
        "compatible": not missing and not mismatches,
        "missing": missing,
        "mismatches": mismatches,
        "left": first,
        "right": second,
    }


def _parse_period(item: dict) -> tuple[date, date] | None:
    period = item.get("period")
    if not isinstance(period, dict) or not period.get("from") or not period.get("to"):
        return None
    return date.fromisoformat(period["from"]), date.fromisoformat(period["to"])


def classify_period_alignment(items: list[dict]) -> str:
    periods = [_parse_period(item) for item in items]
    if not periods or any(period is None for period in periods):
        return "MISMATCHED"
    if all(period == periods[0] for period in periods[1:]):
        return "EXACT"
    latest_start = max(period[0] for period in periods if period)
    earliest_end = min(period[1] for period in periods if period)
    if latest_start <= earliest_end and any(item.get("approximate_period") for item in items):
        return "APPROXIMATE"
    return "MISMATCHED"


def classify_maturity(evidence: dict) -> str:
    if evidence.get("conversion_delay_days") is not None and evidence.get("days_since_period_end") is not None:
        return "MATURE" if evidence["days_since_period_end"] >= evidence["conversion_delay_days"] else "IMMATURE"
    if evidence.get("data_lag_hours") is not None and evidence.get("hours_since_period_end") is not None:
        return "MATURE" if evidence["hours_since_period_end"] >= evidence["data_lag_hours"] else "IMMATURE"
    return "MATURITY_UNKNOWN"
