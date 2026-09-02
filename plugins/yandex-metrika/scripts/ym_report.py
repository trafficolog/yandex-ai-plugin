from __future__ import annotations

import argparse
import json
import os
from typing import Any
from urllib.parse import urlencode

try:
    from ._http import request_json
except ImportError:
    from _http import request_json

API_BASE = "https://api-metrika.yandex.net"
REPORT_PATHS = {
    "table": "/stat/v1/data",
    "bytime": "/stat/v1/data/bytime",
    "comparison": "/stat/v1/data/comparison",
    "drilldown": "/stat/v1/data/drilldown",
    "comparison-drilldown": "/stat/v1/data/comparison/drilldown",
}
CURRENT_ATTRIBUTION_MODELS = {
    "cross_device_first",
    "last",
    "cross_device_last_significant",
    "automatic",
}
DEFAULT_ATTRIBUTION_MODEL = "last"
QUALITY_FIELDS = (
    "sampled",
    "sample_share",
    "sample_size",
    "sample_space",
    "data_lag",
    "contains_sensitive_data",
    "total_rows_rounded",
)


def validate_attribution_model(model: str | None) -> str | None:
    if model is None:
        return None
    if model not in CURRENT_ATTRIBUTION_MODELS:
        allowed = ", ".join(sorted(CURRENT_ATTRIBUTION_MODELS))
        raise ValueError(f"Unsupported attribution model '{model}'. Allowed: {allowed}")
    return model


def _normalize_params(params: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple, set)):
            normalized[key] = ",".join(str(item) for item in value)
        else:
            normalized[key] = value
    attribution = str(normalized.get("attribution") or DEFAULT_ATTRIBUTION_MODEL)
    validate_attribution_model(attribution)
    normalized["attribution"] = attribution
    return normalized


def build_report_url(mode: str, params: dict[str, Any]) -> str:
    try:
        path = REPORT_PATHS[mode]
    except KeyError as exc:
        raise ValueError(f"Unknown report mode: {mode}") from exc
    query = urlencode(_normalize_params(params))
    return f"{API_BASE}{path}" + (f"?{query}" if query else "")


def extract_quality_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: payload[key] for key in QUALITY_FIELDS if key in payload}


def fetch_report(mode: str, params: dict[str, Any], token: str) -> dict[str, Any]:
    normalized = _normalize_params(params)
    try:
        path = REPORT_PATHS[mode]
    except KeyError as exc:
        raise ValueError(f"Unknown report mode: {mode}") from exc
    query = urlencode(normalized)
    url = f"{API_BASE}{path}" + (f"?{query}" if query else "")
    _, payload = request_json("GET", url, token)
    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected Yandex Metrika Reporting API response")
    metadata = {
        "attribution_model": normalized["attribution"],
        "date1": normalized.get("date1"),
        "date2": normalized.get("date2"),
        "ids": normalized.get("ids"),
    }
    return {
        "data": payload,
        "quality": extract_quality_metadata(payload),
        "metadata": metadata,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Yandex Metrika Reporting API helper")
    parser.add_argument("mode", choices=sorted(REPORT_PATHS))
    parser.add_argument("counter", type=int)
    parser.add_argument("--metrics", required=True, help="Comma-separated metrics")
    parser.add_argument("--dimensions", help="Comma-separated dimensions")
    parser.add_argument("--date1")
    parser.add_argument("--date2")
    parser.add_argument("--filters")
    parser.add_argument("--accuracy")
    parser.add_argument(
        "--attribution",
        choices=sorted(CURRENT_ATTRIBUTION_MODELS),
        default=DEFAULT_ATTRIBUTION_MODEL,
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--offset", type=int)
    args = parser.parse_args()

    params: dict[str, Any] = {
        "ids": args.counter,
        "metrics": args.metrics.split(","),
        "dimensions": args.dimensions.split(",") if args.dimensions else None,
        "date1": args.date1,
        "date2": args.date2,
        "filters": args.filters,
        "accuracy": args.accuracy,
        "attribution": args.attribution,
        "limit": args.limit,
        "offset": args.offset,
    }
    token = os.environ.get("YANDEX_METRIKA_TOKEN", "")
    result = fetch_report(args.mode, params, token)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
