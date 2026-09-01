from __future__ import annotations

import argparse
import json
import math
import os
from typing import Any, Callable

try:
    from ._http import auth_headers, redact_headers, request_json
except ImportError:  # CLI execution
    from _http import auth_headers, redact_headers, request_json

BASE_URL = "https://searchapi.api.cloud.yandex.net/v2/wordstat"
ENDPOINTS = {
    "top": "topRequests",
    "dynamics": "dynamics",
    "regions": "regions",
    "regions_tree": "getRegionsTree",
}
PRICE_RUB_PER_1000 = {
    "top": 20.0,
    "dynamics": 20.0,
    "regions": 50.0,
    "regions_tree": 0.0,
}
PRICE_VERIFIED_AT = "2026-09-01"
DOCUMENTED_RPS = 10
DOCUMENTED_REQUESTS_PER_HOUR = 100
DEFAULT_HOURLY_SAFETY_BUDGET = 90


def validate_folder_id(folder_id: str | None) -> str | None:
    if folder_id is None:
        return None
    value = folder_id.strip()
    if not value:
        raise ValueError("folder_id must not be empty when provided")
    if len(value) > 50:
        raise ValueError("folder_id must not exceed 50 characters")
    return value


def build_request(
    method: str,
    payload: dict[str, Any],
    *,
    api_key: str | None = None,
    iam_token: str | None = None,
    folder_id: str | None = None,
) -> dict[str, Any]:
    if method not in ENDPOINTS:
        raise ValueError(f"Unsupported Wordstat method: {method}")
    headers = auth_headers(api_key=api_key, iam_token=iam_token)
    body = dict(payload)
    normalized_folder = validate_folder_id(folder_id)
    if normalized_folder is not None:
        body["folderId"] = normalized_folder
    url = f"{BASE_URL}/{ENDPOINTS[method]}"
    return {
        "method": "POST",
        "operation": method,
        "url": url,
        "headers": headers,
        "body": body,
        "preview": {
            "method": "POST",
            "operation": method,
            "url": url,
            "headers": redact_headers(headers),
            "body": body,
        },
    }


def execute_request(request: dict[str, Any], transport: Callable[..., Any] | None = None) -> Any:
    if transport is not None:
        return transport(request["method"], request["url"], request["headers"], request["body"])
    return request_json(request["method"], request["url"], request["headers"], request["body"])


def _validated_counts(request_counts: dict[str, int]) -> dict[str, int]:
    result: dict[str, int] = {}
    for method, count in request_counts.items():
        if method not in ENDPOINTS:
            raise ValueError(f"Unsupported Wordstat method in plan: {method}")
        if not isinstance(count, int) or count < 0:
            raise ValueError("Request counts must be non-negative integers")
        result[method] = count
    return result


def estimate_cost(
    request_counts: dict[str, int],
    prices: dict[str, float] | None = None,
) -> dict[str, Any]:
    counts = _validated_counts(request_counts)
    rate = dict(PRICE_RUB_PER_1000)
    if prices:
        for method, value in prices.items():
            if method not in ENDPOINTS or value < 0:
                raise ValueError("Invalid price override")
            rate[method] = float(value)
    by_method = {
        method: round(count * rate[method] / 1000.0, 6)
        for method, count in counts.items()
    }
    return {
        "requests": sum(counts.values()),
        "estimated_rub": round(sum(by_method.values()), 6),
        "by_method_rub": by_method,
        "prices_rub_per_1000": rate,
        "verified_at": PRICE_VERIFIED_AT,
        "billing_guarantee": False,
    }


def plan_quota(
    request_counts: dict[str, int],
    *,
    hourly_budget: int = DEFAULT_HOURLY_SAFETY_BUDGET,
) -> dict[str, Any]:
    counts = _validated_counts(request_counts)
    if not isinstance(hourly_budget, int) or hourly_budget < 1 or hourly_budget > DOCUMENTED_REQUESTS_PER_HOUR:
        raise ValueError("hourly_budget must be an integer from 1 to 100")
    total = sum(counts.values())
    return {
        "requests": total,
        "documented_requests_per_hour": DOCUMENTED_REQUESTS_PER_HOUR,
        "documented_requests_per_second": DOCUMENTED_RPS,
        "hourly_safety_budget": hourly_budget,
        "fits_safety_budget": total <= hourly_budget,
        "minimum_hourly_windows": 0 if total == 0 else math.ceil(total / hourly_budget),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Yandex Cloud Wordstat v2 raw helper")
    parser.add_argument("method", choices=sorted(ENDPOINTS))
    parser.add_argument("--body", default="{}", help="JSON request payload")
    parser.add_argument("--execute", action="store_true", help="Perform the paid/read API request")
    args = parser.parse_args()

    api_key = os.environ.get("YANDEX_WORDSTAT_API_KEY")
    iam_token = os.environ.get("YANDEX_WORDSTAT_IAM_TOKEN")
    folder_id = os.environ.get("YANDEX_WORDSTAT_FOLDER_ID") or None
    request = build_request(
        args.method,
        json.loads(args.body),
        api_key=api_key,
        iam_token=iam_token,
        folder_id=folder_id,
    )
    if not args.execute:
        print(json.dumps({"dry_run": True, **request["preview"]}, ensure_ascii=False, indent=2))
        return 0
    payload = execute_request(request)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
