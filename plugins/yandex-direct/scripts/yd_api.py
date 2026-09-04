#!/usr/bin/env python3
"""Small dependency-free Yandex Direct API v501 client.

Only explicitly known read operations execute without --execute. Every other
method is treated as consequential by default and is previewed first.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Callable, Mapping

try:
    from . import _http
    from ._approval import preview_id, require_approval
except ImportError:  # CLI execution from scripts directory
    import _http
    from _approval import preview_id, require_approval

API_BASE = "https://api.direct.yandex.com/json/v501"
READ_METHODS = {
    "check",
    "checkcampaigns",
    "checkdictionaries",
    "get",
    "getchanges",
}
AUTH_PRINCIPAL_DOMAIN = b"yandex-direct-auth-principal/v1"


class YandexDirectError(RuntimeError):
    pass


def is_read_method(method: str) -> bool:
    return method.strip().casefold() in READ_METHODS


def auth_principal_binding(token: str) -> str:
    """Return a stable token-sensitive pseudonymous principal binding."""
    return hmac.new(
        token.encode("utf-8"),
        AUTH_PRINCIPAL_DOMAIN,
        hashlib.sha256,
    ).hexdigest()


@dataclass
class YandexDirectClient:
    token: str
    client_login: str | None = None
    language: str = "ru"
    timeout: int = 60
    opener: Callable[..., Any] = _http.urlopen

    def endpoint(self, service: str) -> str:
        service = service.strip().lower()
        if not service or "/" in service:
            raise ValueError("service must be a single Yandex Direct service name")
        return f"{API_BASE}/{service}"

    def headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept-Language": self.language,
        }
        if self.client_login:
            headers["Client-Login"] = self.client_login
        return headers

    @staticmethod
    def body(method: str, params: Mapping[str, Any] | None) -> dict[str, Any]:
        return {"method": method, "params": dict(params or {})}

    def approval_envelope(
        self,
        service: str,
        method: str,
        params: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        normalized_service = service.strip().lower()
        normalized_method = method.strip().lower()
        return {
            "schema": "yandex-ai-approval/v1",
            "plugin": "yandex-direct",
            "operation": f"{normalized_service}.{normalized_method}",
            "method": "POST",
            "target": {
                "environment": "production",
                "client_login": self.client_login,
                "auth_principal_hmac_sha256": auth_principal_binding(self.token),
            },
            "url": self.endpoint(service),
            "body": self.body(method, params),
            "artifacts": [],
        }

    def request(
        self,
        service: str,
        method: str,
        params: Mapping[str, Any] | None = None,
        *,
        dry_run: bool = False,
        approve: str | None = None,
    ) -> dict[str, Any]:
        body = self.body(method, params)
        envelope = self.approval_envelope(service, method, params)
        if dry_run:
            safe_headers = self.headers()
            safe_headers["Authorization"] = "Bearer ***REDACTED***"
            return {
                "dry_run": True,
                "preview_id": preview_id(envelope),
                "endpoint": self.endpoint(service),
                "headers": safe_headers,
                "body": body,
            }

        if not is_read_method(method):
            require_approval(envelope, approve)

        try:
            data, transport = _http.request_json(
                self.endpoint(service),
                self.headers(),
                body,
                timeout=self.timeout,
                opener=self.opener,
            )
        except _http.DirectHTTPError as exc:
            raise YandexDirectError(str(exc)) from exc

        if data.get("error"):
            err = data["error"]
            request_id = transport.get("request_id") or data.get("request_id") or data.get("RequestId")
            suffix = f" request_id={request_id}" if request_id else ""
            raise YandexDirectError(f"Yandex Direct API error: {err}{suffix}")
        return {"result": data, "transport": transport}


def _load_params(args: argparse.Namespace) -> dict[str, Any]:
    if args.params_file:
        with open(args.params_file, "r", encoding="utf-8") as fh:
            value = json.load(fh)
    else:
        value = json.loads(args.params or "{}")
    if not isinstance(value, dict):
        raise ValueError("params must be a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Yandex Direct API v501 helper")
    parser.add_argument("service", help="campaigns, adgroups, keywords, ads, ...")
    parser.add_argument("method", help="get, add, update, set, ...")
    parser.add_argument("--params", help="JSON object with method params")
    parser.add_argument("--params-file", help="Path to JSON params file")
    parser.add_argument("--token", default=os.getenv("YANDEX_DIRECT_TOKEN"))
    parser.add_argument("--client-login", default=os.getenv("YANDEX_DIRECT_CLIENT_LOGIN"))
    parser.add_argument("--execute", action="store_true", help="Execute consequential operation")
    parser.add_argument("--approve", help="Full preview_id for the exact consequential preview")
    parser.add_argument("--dry-run", action="store_true", help="Preview any operation")
    args = parser.parse_args(argv)

    if not args.token:
        parser.error("Provide --token or YANDEX_DIRECT_TOKEN")
    if args.params and args.params_file:
        parser.error("Use only one of --params or --params-file")

    params = _load_params(args)
    is_write = not is_read_method(args.method)
    dry_run = args.dry_run or (is_write and not args.execute)

    client = YandexDirectClient(args.token, client_login=args.client_login)
    result = client.request(
        args.service,
        args.method,
        params,
        dry_run=dry_run,
        approve=args.approve,
    )
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    if is_write and dry_run:
        sys.stderr.write(
            "Preview only. Re-run with --execute --approve <preview_id> after the user approves this exact payload.\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())