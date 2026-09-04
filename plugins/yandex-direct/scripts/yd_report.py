#!/usr/bin/env python3
"""Yandex Direct Reports v501 helper with explicit KPI context."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Mapping, Sequence

REPORTS_URL = "https://api.direct.yandex.com/json/v501/reports"
ERROR_BODY_LIMIT = 4096
ATTRIBUTION_MODELS = {"FCCD", "LC", "LSCCD", "AUTO"}
LEGACY_TOKEN_OPTIONS = {"--t", "--to", "--tok", "--toke", "--token"}


class ReportError(RuntimeError):
    """Expected Direct Reports operational failure safe for the CLI boundary."""

    def __init__(self, message: str, *, error_type: str) -> None:
        super().__init__(message)
        self.error_type = error_type


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


def _normalize_attribution_models(values: Sequence[str] | None) -> list[str]:
    models = [str(value).strip().upper() for value in (values or ["LC"])]
    if not models or any(model not in ATTRIBUTION_MODELS for model in models):
        allowed = ", ".join(sorted(ATTRIBUTION_MODELS))
        raise ValueError(f"Attribution models must be one of: {allowed}")
    return models


def build_report_body(
    preset: str,
    date_from: str,
    date_to: str,
    *,
    report_name: str | None = None,
    include_vat: str = "YES",
    goals: Sequence[int | str] | None = None,
    attribution_models: Sequence[str] | None = None,
) -> dict[str, Any]:
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset: {preset}")
    if include_vat not in {"YES", "NO"}:
        raise ValueError("include_vat must be YES or NO")
    report_type, fields = PRESETS[preset]
    name = report_name or f"yd-{preset}-{uuid.uuid4().hex[:12]}"
    params: dict[str, Any] = {
        "SelectionCriteria": {"DateFrom": date_from, "DateTo": date_to},
        "FieldNames": fields,
        "ReportName": name,
        "ReportType": report_type,
        "DateRangeType": "CUSTOM_DATE",
        "Format": "TSV",
        "IncludeVAT": include_vat,
        "AttributionModels": _normalize_attribution_models(attribution_models),
    }
    if goals is not None:
        goal_values = list(goals)
        if not goal_values or len(goal_values) > 10:
            raise ValueError("goals must contain between 1 and 10 IDs")
        params["Goals"] = goal_values
    return {"params": params}


def build_report_metadata(preset: str, body: Mapping[str, Any]) -> dict[str, Any]:
    """Build a serializable provenance sidecar for downstream KPI reconciliation."""
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset: {preset}")
    params = body.get("params")
    if not isinstance(params, Mapping):
        raise ValueError("report body must contain params")
    selection = params.get("SelectionCriteria")
    if not isinstance(selection, Mapping):
        raise ValueError("report body must contain SelectionCriteria")
    date_from = selection.get("DateFrom")
    date_to = selection.get("DateTo")
    if not date_from or not date_to:
        raise ValueError("report body must contain DateFrom and DateTo")

    include_vat = params.get("IncludeVAT")
    if include_vat not in {"YES", "NO"}:
        raise ValueError("report body must contain a valid IncludeVAT value")

    return {
        "schema_version": 1,
        "source": "yandex-direct",
        "artifact_type": "reports-v501-tsv",
        "preset": preset,
        "report_name": params.get("ReportName"),
        "report_type": params.get("ReportType"),
        "period": {"from": str(date_from), "to": str(date_to)},
        "goal_ids": list(params.get("Goals") or []),
        "attribution_models": list(params.get("AttributionModels") or []),
        "vat_basis": "included" if include_vat == "YES" else "excluded",
        "currency": None,
        "currency_source": "not_returned_by_reports_helper",
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


def _read_response_text(
    response,
    *,
    context: str,
    limit: int | None = None,
    decode_errors: str = "strict",
) -> str:
    try:
        raw = response.read() if limit is None else response.read(limit)
    except (TimeoutError, OSError) as exc:
        raise ReportError(
            f"Direct Reports network error while {context}",
            error_type="network",
        ) from exc
    return raw.decode("utf-8", errors=decode_errors)


def fetch_report(
    token: str,
    body: Mapping[str, Any],
    *,
    client_login: str | None = None,
    max_attempts: int = 20,
    timeout: int = 120,
    opener=None,
    sleep=None,
) -> str:
    opener = opener or urllib.request.urlopen
    sleep = sleep or time.sleep
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

    payload = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    retried_server_error = False

    for attempt in range(1, max_attempts + 1):
        req = urllib.request.Request(REPORTS_URL, data=payload, headers=headers, method="POST")
        try:
            with opener(req, timeout=timeout) as response:
                status = response.status
                response_headers = dict(response.headers.items())
                text = _read_response_text(response, context="reading response")
        except urllib.error.HTTPError as exc:
            status = exc.code
            response_headers = dict(exc.headers.items()) if exc.headers else {}
            try:
                text = _read_response_text(
                    exc,
                    context=f"reading HTTP {status} error response",
                    limit=ERROR_BODY_LIMIT,
                    decode_errors="replace",
                )
            finally:
                exc.close()
        except urllib.error.URLError as exc:
            raise ReportError(
                f"Direct Reports network error: {exc.reason}",
                error_type="network",
            ) from exc

        if status == 200:
            return text
        if status in {201, 202}:
            if attempt == max_attempts:
                raise ReportError(
                    f"Report still not ready after {max_attempts} attempts",
                    error_type="api",
                )
            sleep(parse_retry_in(response_headers))
            continue
        if status == 400:
            raise ReportError(f"Bad report request: {text}", error_type="api")
        if status == 500 and not retried_server_error and attempt < max_attempts:
            retried_server_error = True
            sleep(parse_retry_in(response_headers))
            continue
        if status == 500:
            raise ReportError(f"Yandex report server error: {text}", error_type="http")
        raise ReportError(f"Unexpected HTTP {status}: {text}", error_type="http")

    raise ReportError("Unreachable", error_type="api")


def _parse_csv_values(raw: str | None) -> list[str] | None:
    if raw is None:
        return None
    values = [item.strip() for item in raw.split(",") if item.strip()]
    return values or None


def contains_legacy_token_option(argv: list[str]) -> bool:
    return any(arg.partition("=")[0] in LEGACY_TOKEN_OPTIONS for arg in argv)


def emit_cli_error(error_type: str, message: str) -> int:
    json.dump({"error": {"type": error_type, "message": message}}, sys.stderr, ensure_ascii=False)
    sys.stderr.write("\n")
    return 2


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    if contains_legacy_token_option(raw_argv):
        return emit_cli_error(
            "validation",
            "--token is no longer supported; set YANDEX_DIRECT_TOKEN in the environment",
        )

    parser = argparse.ArgumentParser(description="Yandex Direct Reports v501 helper")
    parser.add_argument("preset", choices=sorted(PRESETS))
    parser.add_argument("date_from")
    parser.add_argument("date_to")
    parser.add_argument("--report-name")
    parser.add_argument("--client-login", default=os.getenv("YANDEX_DIRECT_CLIENT_LOGIN"))
    parser.add_argument("--include-vat", choices=["YES", "NO"], default="YES")
    parser.add_argument("--goals", help="Comma-separated Metrika goal IDs (max 10)")
    parser.add_argument(
        "--attribution-models",
        default="LC",
        help="Comma-separated attribution models: FCCD, LC, LSCCD, AUTO",
    )
    parser.add_argument("--output", help="Write TSV to file instead of stdout")
    args = parser.parse_args(raw_argv)
    token = os.getenv("YANDEX_DIRECT_TOKEN")
    if not token:
        parser.error("Set YANDEX_DIRECT_TOKEN")

    goals = _parse_csv_values(args.goals)
    attribution_models = _parse_csv_values(args.attribution_models)
    body = build_report_body(
        args.preset,
        args.date_from,
        args.date_to,
        report_name=args.report_name,
        include_vat=args.include_vat,
        goals=goals,
        attribution_models=attribution_models,
    )
    try:
        text = fetch_report(token, body, client_login=args.client_login)
    except ReportError as exc:
        return emit_cli_error(exc.error_type, str(exc))

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(text, encoding="utf-8", newline="")
        metadata_path = Path(str(output_path) + ".metadata.json")
        metadata_path.write_text(
            json.dumps(build_report_metadata(args.preset, body), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
