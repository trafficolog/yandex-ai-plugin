from __future__ import annotations

import argparse
import hashlib
import json
import os
from typing import Any, Callable
from urllib.parse import urlencode, urlsplit, urlunsplit

try:
    from ._approval import preview_id, require_approval
    from ._http import auth_headers, redact_headers, request_json
except ImportError:
    from _approval import preview_id, require_approval
    from _http import auth_headers, redact_headers, request_json

API_ROOT = "https://api.webmaster.yandex.net"
ALLOWED_VERSIONS = {"v4", "v4.1"}
READ_METHODS = {"GET", "HEAD", "OPTIONS"}
APPROVAL_SCHEMA = "yandex-ai-approval/v1"


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


def redact_url_credentials(value: str) -> str:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return value
    if not parsed.scheme or not parsed.hostname or (parsed.username is None and parsed.password is None):
        return value
    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    netloc = f"***:***@{host}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))


def _approval_url_credentials(value: str) -> str:
    """Remove URL credentials from approval data while still binding their exact values."""
    try:
        parsed = urlsplit(value)
    except ValueError:
        return value
    if not parsed.scheme or not parsed.hostname or (parsed.username is None and parsed.password is None):
        return value
    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    username = parsed.username or ""
    password = parsed.password or ""
    credential_fingerprint = hashlib.sha256(
        f"{username}\0{password}".encode("utf-8")
    ).hexdigest()
    netloc = f"credential-sha256:{credential_fingerprint}@{host}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))


def _redact_preview_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_url_credentials(value)
    if isinstance(value, list):
        return [_redact_preview_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_preview_value(item) for item in value)
    if isinstance(value, dict):
        return {key: _redact_preview_value(item) for key, item in value.items()}
    return value


def _approval_value(value: Any) -> Any:
    if isinstance(value, str):
        return _approval_url_credentials(value)
    if isinstance(value, list):
        return [_approval_value(item) for item in value]
    if isinstance(value, tuple):
        return [_approval_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _approval_value(item) for key, item in value.items()}
    return value


def approval_envelope(
    *,
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    body: Any | None = None,
    version: str = "v4",
) -> dict[str, Any]:
    safe_params = _approval_value(params or {})
    safe_body = _approval_value(body)
    return {
        "schema": APPROVAL_SCHEMA,
        "plugin": "yandex-webmaster",
        "environment": "production",
        "api_version": version,
        "method": method.upper(),
        "path": path.strip("/"),
        "url": api_url(path, params=safe_params or None, version=version),
        "query": safe_params,
        "body": safe_body,
    }


def prepare_request(
    *, method: str, path: str, token: str, params: dict[str, Any] | None = None,
    body: Any | None = None, version: str = "v4"
) -> dict[str, Any]:
    result = {
        "method": method.upper(),
        "url": api_url(path, params=params, version=version),
        "headers": redact_headers(auth_headers(token)),
        "body": _redact_preview_value(body),
        "consequential": is_consequential(method),
        "version": version,
    }
    if result["consequential"]:
        result["preview_id"] = preview_id(
            approval_envelope(
                method=method,
                path=path,
                params=params,
                body=body,
                version=version,
            )
        )
    return result


def run_request(
    *, method: str, path: str, token: str, params: dict[str, Any] | None = None,
    body: Any | None = None, version: str = "v4", execute: bool = False,
    approve: str | None = None,
    transport: Callable[..., Any] | None = None,
) -> Any:
    preview = prepare_request(
        method=method,
        path=path,
        token=token,
        params=params,
        body=body,
        version=version,
    )
    consequential = is_consequential(method)
    if consequential and not execute:
        return {"dry_run": True, **preview}
    if consequential:
        require_approval(
            approval_envelope(
                method=method,
                path=path,
                params=params,
                body=body,
                version=version,
            ),
            approve,
        )
    url = api_url(path, params=params, version=version)
    if transport is not None:
        return transport(method=method.upper(), url=url, token=token, body=body)
    _, payload = request_json(method, url, token, body=body)
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
    parser.add_argument("--approve", help="Exact preview_id for the consequential operation")
    args = parser.parse_args()
    token = os.environ.get("YANDEX_WEBMASTER_TOKEN", "")
    payload = run_request(
        method=args.method,
        path=args.path,
        token=token,
        params=_json_arg(args.params),
        body=_json_arg(args.body),
        version=args.version,
        execute=args.execute,
        approve=args.approve,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
