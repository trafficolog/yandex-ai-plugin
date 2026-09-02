from __future__ import annotations

import argparse
import json
import os
from typing import Any, Callable
from urllib.parse import urlencode

try:
    from ._http import auth_headers, redact_headers, request_json
except ImportError:
    from _http import auth_headers, redact_headers, request_json

API_ROOT = "https://api.webmaster.yandex.net"
ALLOWED_VERSIONS = {"v4", "v4.1"}
READ_METHODS = {"GET", "HEAD", "OPTIONS"}


def api_url(path: str, *, params: dict[str, Any] | None = None, version: str = "v4") -> str:
    if version not in ALLOWED_VERSIONS:
        raise ValueError(f"Unsupported Yandex Webmaster API version: {version}")
    clean = path.strip("/")
    url = f"{API_ROOT}/{version}/{clean}"
    if params:
        url += "?" + urlencode(params, doseq=True)
    return url


def is_consequential(method: str) -> bool:
    return method.upper() not in READ_METHODS


def prepare_request(
    *, method: str, path: str, token: str, params: dict[str, Any] | None = None,
    body: Any | None = None, version: str = "v4"
) -> dict[str, Any]:
    return {
        "method": method.upper(),
        "url": api_url(path, params=params, version=version),
        "headers": redact_headers(auth_headers(token)),
        "body": body,
        "consequential": is_consequential(method),
        "version": version,
    }


def run_request(
    *, method: str, path: str, token: str, params: dict[str, Any] | None = None,
    body: Any | None = None, version: str = "v4", execute: bool = False,
    transport: Callable[..., Any] | None = None,
) -> Any:
    preview = prepare_request(method=method, path=path, token=token, params=params, body=body, version=version)
    if is_consequential(method) and not execute:
        return {"dry_run": True, **preview}
    if transport is not None:
        return transport(method=method.upper(), url=api_url(path, params=params, version=version), token=token, body=body)
    _, payload = request_json(method, api_url(path, params=params, version=version), token, body=body)
    return payload


def _json_arg(value: str | None) -> Any | None:
    return None if value is None else json.loads(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Yandex Webmaster API helper")
    parser.add_argument("path")
    parser.add_argument("--method", default="GET")
    parser.add_argument("--version", choices=sorted(ALLOWED_VERSIONS), default="v4")
    parser.add_argument("--params", help="JSON object with query parameters")
    parser.add_argument("--body", help="JSON request body")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    token = os.environ.get("YANDEX_WEBMASTER_TOKEN", "")
    payload = run_request(
        method=args.method, path=args.path, token=token, params=_json_arg(args.params),
        body=_json_arg(args.body), version=args.version, execute=args.execute,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
