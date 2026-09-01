#!/usr/bin/env python3
"""Yandex Direct Reports v501 helper with correct offline polling semantics."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from typing import Any, Mapping

REPORTS_URL = "https://api.direct.yandex.com/json/v501/reports"

PRESETS: dict[str, tuple[str, list[str]]] = {
    "campaign": (
        "CAMPAIGN_PERFORMANCE_REPORT",
        ["Date", "CampaignName", "CampaignId", "Impressions", "Clicks", "Ctr", "AvgCpc", "Cost", "Conversions", "ConversionRate", "CostPerConversion"],
    ),
    "adgroup": (
        "ADGROUP_PERFORMANCE_REPORT",
        ["Date", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "Impressions", "Clicks", "Ctr", "AvgCpc", "Cost", "Conversions", "CostPerConversion"],
    ),
    "criteria": (
        "CRITERIA_PERFORMANCE_REPORT",
        ["Date", "CampaignName", "AdGroupName", "Criterion", "CriterionId", "CriterionType", "Impressions", "Clicks", "Ctr", "AvgCpc", "Cost", "Conversions", "CostPerConversion"],
    ),
    "search_query": (
        "SEARCH_QUERY_PERFORMANCE_REPORT",
        ["Date", "CampaignName", "AdGroupName", "Query", "CriterionId", "Impressions", "Clicks", "Ctr", "AvgCpc", "Cost", "Conversions"],
    ),
}


def build_report_body(
    preset: str,
    date_from: str,
    date_to: str,
    *,
    report_name: str | None = None,
    include_vat: str = "YES",
) -> dict[str, Any]:
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset: {preset}")
    report_type, fields = PRESETS[preset]
    name = report_name or f"yd-{preset}-{uuid.uuid4().hex[:12]}"
    return {
        "params": {
            "SelectionCriteria": {"DateFrom": date_from, "DateTo": date_to},
            "FieldNames": fields,
            "ReportName": name,
            "ReportType": report_type,
            "DateRangeType": "CUSTOM_DATE",
            "Format": "TSV",
            "IncludeVAT": include_vat,
            "IncludeDiscount": "YES",
        }
    }


def parse_retry_in(headers: Mapping[str, str], default: int = 5) -> int:
    lowered = {str(k).lower(): str(v) for k, v in headers.items()}
    raw = lowered.get("retryin")
    if raw is None:
        return default
    try:
        return max(1, int(float(raw)))
    except ValueError:
        return default


def fetch_report(
    token: str,
    body: Mapping[str, Any],
    *,
    client_login: str | None = None,
    max_attempts: int = 20,
    timeout: int = 120,
) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept-Language": "ru",
        "processingMode": "auto",
        "returnMoneyInMicros": "false",
        "skipReportHeader": "true",
        "skipReportSummary": "true",
    }
    if client_login:
        headers["Client-Login"] = client_login

    # Important: payload remains byte-identical for every retry. Yandex requires
    # the same report request while an offline report is being generated.
    payload = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    for attempt in range(1, max_attempts + 1):
        req = urllib.request.Request(REPORTS_URL, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status = response.status
                response_headers = dict(response.headers.items())
                text = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            status = exc.code
            response_headers = dict(exc.headers.items()) if exc.headers else {}
            text = exc.read().decode("utf-8", errors="replace")

        if status == 200:
            return text
        if status in {201, 202}:
            if attempt == max_attempts:
                raise RuntimeError(f"Report still not ready after {max_attempts} attempts")
            time.sleep(parse_retry_in(response_headers))
            continue
        if status == 400:
            raise RuntimeError(f"Bad report request: {text}")
        if status == 500:
            raise RuntimeError(f"Yandex report server error: {text}")
        raise RuntimeError(f"Unexpected HTTP {status}: {text}")

    raise RuntimeError("Unreachable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Yandex Direct Reports v501 helper")
    parser.add_argument("preset", choices=sorted(PRESETS))
    parser.add_argument("date_from")
    parser.add_argument("date_to")
    parser.add_argument("--report-name")
    parser.add_argument("--token", default=os.getenv("YANDEX_DIRECT_TOKEN"))
    parser.add_argument("--client-login", default=os.getenv("YANDEX_DIRECT_CLIENT_LOGIN"))
    parser.add_argument("--include-vat", choices=["YES", "NO"], default="YES")
    parser.add_argument("--output", help="Write TSV to file instead of stdout")
    args = parser.parse_args(argv)
    if not args.token:
        parser.error("Provide --token or YANDEX_DIRECT_TOKEN")

    body = build_report_body(
        args.preset,
        args.date_from,
        args.date_to,
        report_name=args.report_name,
        include_vat=args.include_vat,
    )
    text = fetch_report(args.token, body, client_login=args.client_login)
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
