from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from ._http import oauth_headers, redact_headers, request_json
except ImportError:
    from _http import oauth_headers, redact_headers, request_json

BASE = "https://api-metrika.yandex.net/management/v1"
CONSEQUENTIAL_ACTIONS = {"create", "clean"}


def _anniversary(day: date) -> date:
    try:
        return day.replace(year=day.year + 1)
    except ValueError:  # Feb 29 -> Feb 28 next year
        return day.replace(year=day.year + 1, day=28)


def validate_period(date1: str, date2: str, *, today: date | None = None) -> tuple[date, date]:
    start = date.fromisoformat(date1)
    end = date.fromisoformat(date2)
    if end < start:
        raise ValueError("Logs date2 must be on or after date1")
    today = today or date.today()
    if end >= today:
        raise ValueError("Logs date2 must be earlier than the current day")
    if end > _anniversary(start):
        raise ValueError("A Yandex Metrika Logs request cannot exceed one year")
    return start, end


def logs_endpoint(
    counter_id: int,
    action: str,
    *,
    request_id: int | None = None,
    part_number: int | None = None,
) -> str:
    prefix = f"{BASE}/counter/{int(counter_id)}"
    if action == "evaluate":
        return f"{prefix}/logrequests/evaluate"
    if action == "create":
        return f"{prefix}/logrequests"
    if request_id is None:
        raise ValueError(f"request_id is required for Logs action '{action}'")
    if action == "status":
        return f"{prefix}/logrequest/{int(request_id)}"
    if action == "clean":
        return f"{prefix}/logrequest/{int(request_id)}/clean"
    if action == "download":
        if part_number is None:
            raise ValueError("part_number is required for Logs download")
        return f"{prefix}/logrequest/{int(request_id)}/part/{int(part_number)}/download"
    raise ValueError(f"Unknown Logs action: {action}")


def _query_url(url: str, query: dict[str, Any] | None) -> str:
    if not query:
        return url
    normalized = {k: v for k, v in query.items() if v is not None}
    return url + "?" + urlencode(normalized)


def prepare_logs_request(
    counter_id: int,
    action: str,
    *,
    token: str,
    request_id: int | None = None,
    part_number: int | None = None,
    query: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if action in {"evaluate", "create"} and query:
        if query.get("date1") and query.get("date2"):
            validate_period(str(query["date1"]), str(query["date2"]))
    method = "POST" if action in CONSEQUENTIAL_ACTIONS else "GET"
    url = _query_url(
        logs_endpoint(counter_id, action, request_id=request_id, part_number=part_number),
        query,
    )
    return {
        "method": method,
        "url": url,
        "headers": redact_headers(oauth_headers(token, content_type="")),
        "consequential": action in CONSEQUENTIAL_ACTIONS,
    }


def execute_json_action(
    counter_id: int,
    action: str,
    *,
    token: str,
    request_id: int | None = None,
    query: dict[str, Any] | None = None,
) -> Any:
    preview = prepare_logs_request(
        counter_id,
        action,
        token=token,
        request_id=request_id,
        query=query,
    )
    _, payload = request_json(preview["method"], preview["url"], token)
    return payload


def download_part(
    counter_id: int,
    request_id: int,
    part_number: int,
    token: str,
    output: Path,
    *,
    timeout: int = 60,
    opener: Callable[..., Any] = urlopen,
) -> Path:
    url = logs_endpoint(counter_id, "download", request_id=request_id, part_number=part_number)
    request = Request(url, headers=oauth_headers(token, content_type=""), method="GET")
    with opener(request, timeout=timeout) as response:
        data = response.read()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Yandex Metrika Logs API helper")
    parser.add_argument("action", choices=["evaluate", "create", "status", "download", "clean"])
    parser.add_argument("counter", type=int)
    parser.add_argument("--request-id", type=int)
    parser.add_argument("--part-number", type=int)
    parser.add_argument("--date1")
    parser.add_argument("--date2")
    parser.add_argument("--fields")
    parser.add_argument("--source", choices=["hits", "visits"])
    parser.add_argument("--attribution")
    parser.add_argument("--output")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("YANDEX_METRIKA_TOKEN", "")
    query = None
    if args.action in {"evaluate", "create"}:
        if not all([args.date1, args.date2, args.fields, args.source]):
            parser.error("evaluate/create require --date1 --date2 --fields --source")
        validate_period(args.date1, args.date2)
        query = {
            "date1": args.date1,
            "date2": args.date2,
            "fields": args.fields,
            "source": args.source,
            "attribution": args.attribution if args.action == "create" else None,
        }

    if args.action == "download":
        if args.request_id is None or args.part_number is None or not args.output:
            parser.error("download requires --request-id --part-number --output")
        path = download_part(args.counter, args.request_id, args.part_number, token, Path(args.output))
        print(json.dumps({"output": str(path)}, ensure_ascii=False))
        return 0

    preview = prepare_logs_request(
        args.counter,
        args.action,
        token=token,
        request_id=args.request_id,
        query=query,
    )
    if preview["consequential"] and not args.execute:
        print(json.dumps({"dry_run": True, **preview}, ensure_ascii=False, indent=2))
        return 0
    payload = execute_json_action(
        args.counter,
        args.action,
        token=token,
        request_id=args.request_id,
        query=query,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
