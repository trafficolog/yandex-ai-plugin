from __future__ import annotations

from statistics import median
from typing import Any


def _month_key(date: str) -> tuple[int, int]:
    try:
        year = int(date[0:4])
        month = int(date[5:7])
    except (ValueError, IndexError) as exc:
        raise ValueError(f"invalid date: {date}") from exc
    if not 1 <= month <= 12:
        raise ValueError(f"invalid date month: {date}")
    return year, month


def _normalize(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for point in points:
        date = str(point.get("date", ""))
        _month_key(date)
        try:
            count = int(point.get("count", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid count: {point!r}") from exc
        if count < 0:
            raise ValueError("count must be non-negative")
        normalized.append({**point, "date": date, "count": count})
    return sorted(normalized, key=lambda item: item["date"])


def _baseline_before(points: list[dict[str, Any]], index: int) -> float:
    prior = [item["count"] for item in points[max(0, index - 3):index]]
    if not prior:
        return 0.0
    return float(median(prior))


def _seasonal_reference(
    points: list[dict[str, Any]],
    latest_index: int,
    *,
    growing_pct: float,
    tolerance_pct: float,
) -> dict[str, Any] | None:
    latest = points[latest_index]
    latest_year, latest_month = _month_key(latest["date"])
    candidates: list[tuple[int, dict[str, Any]]] = []
    for idx, point in enumerate(points[:latest_index]):
        year, month = _month_key(point["date"])
        if year == latest_year - 1 and month == latest_month:
            candidates.append((idx, point))
    if not candidates or latest["count"] <= 0:
        return None
    idx, prior = candidates[-1]
    difference_pct = abs(latest["count"] - prior["count"]) / latest["count"] * 100.0
    if difference_pct > tolerance_pct:
        return None
    prior_baseline = _baseline_before(points, idx)
    if prior_baseline <= 0:
        return None
    prior_growth = (prior["count"] - prior_baseline) / prior_baseline * 100.0
    if prior_growth < growing_pct:
        return None
    return {"date": prior["date"], "count": prior["count"], "difference_pct": round(difference_pct, 2)}


def classify_trend(
    points: list[dict[str, Any]],
    *,
    absolute_floor: int = 100,
    growing_pct: float = 50,
    explosive_pct: float = 200,
    seasonal_tolerance_pct: float = 25,
) -> dict[str, Any]:
    series = _normalize(points)
    if len(series) < 2:
        raise ValueError("At least two dynamics points are required")
    if absolute_floor < 0 or growing_pct < 0 or explosive_pct < growing_pct or seasonal_tolerance_pct < 0:
        raise ValueError("Invalid trend thresholds")

    latest_index = len(series) - 1
    latest = series[latest_index]
    baseline = _baseline_before(series, latest_index)
    if baseline <= 0:
        growth_pct = float("inf") if latest["count"] > 0 else 0.0
    else:
        growth_pct = (latest["count"] - baseline) / baseline * 100.0

    seasonal = _seasonal_reference(
        series,
        latest_index,
        growing_pct=growing_pct,
        tolerance_pct=seasonal_tolerance_pct,
    )

    if latest["count"] < absolute_floor:
        classification = "LOW_VOLUME_NOISE"
    elif seasonal is not None and growth_pct >= growing_pct:
        classification = "SEASONAL"
    elif growth_pct >= explosive_pct:
        classification = "EXPLOSIVE"
    elif growth_pct >= growing_pct:
        classification = "GROWING"
    else:
        classification = "STABLE"

    return {
        "classification": classification,
        "latest": latest,
        "baseline_median": baseline,
        "growth_pct": round(growth_pct, 2) if growth_pct != float("inf") else float("inf"),
        "seasonal_reference": seasonal,
        "thresholds": {
            "absolute_floor": absolute_floor,
            "growing_pct": growing_pct,
            "explosive_pct": explosive_pct,
            "seasonal_tolerance_pct": seasonal_tolerance_pct,
        },
    }
