from __future__ import annotations

import argparse
import json
import os
from typing import Any
from urllib.parse import urlencode

try:
    from ._http import oauth_headers, redact_headers, request_json
except ImportError:  # CLI execution from scripts directory
    from _http import oauth_headers, redact_headers, request_json

MANAGEMENT_BASE = "https://api-metrika.yandex.net/management/v1"
READ_METHODS = {"GET", "HEAD", "OPTIONS"}


def build_management_url(path: str, query: dict[str, Any] | None = None) -> str:
    clean = path.strip("/")
    url = f"{MANAGEMENT_BASE}/{clean}"
    if query:
        url += "?" + urlencode(query, doseq=True)
    return url


def is_consequential(method: str) -> bool:
    return method.upper() not in READ_METHODS


def prepare_request(
    *, method: str, path: str, token: str, query: dict[str, Any] | None = None, body: Any | None = None
) -> dict[str, Any]:
    headers = oauth_headers(token)
    return {
        "method": method.upper(),
        "url": build_management_url(path, query),
        "headers": redact_headers(headers),
        "body": body,
        "consequential": is_consequential(method),
    }


def execute_request(
    *, method: str, path: str, token: str, query: dict[str, Any] | None = None, body: Any | None = None
) -> Any:
    url = build_management_url(path, query)
    _, payload = request_json(method, url, token, body=body)
    return payload


def _json_arg(value: str | None) -> Any | None:
    if value is None:
        return None
    return json.loads(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Yandex Metrika Management API helper")
    parser.add_argument("path")
    parser.add_argument("--method", default="GET")
    parser.add_argument("--query", help="JSON object with query parameters")
    parser.add_argument("--body", help="JSON request body")
    parser.add_argument("--execute", action="store_true", help="Execute consequential writes")
    args = parser.parse_args()

    token = os.environ.get("YANDEX_METRIKA_TOKEN", "")
    query = _json_arg(args.query)
    body = _json_arg(args.body)
    preview = prepare_request(method=args.method, path=args.path, token=token, query=query, body=body)
    if is_consequential(args.method) and not args.execute:
        print(json.dumps({"dry_run": True, **preview}, ensure_ascii=False, indent=2))
        return 0
    payload = execute_request(method=args.method, path=args.path, token=token, query=query, body=body)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
