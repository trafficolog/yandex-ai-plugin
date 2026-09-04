#!/usr/bin/env python3
"""Small dependency-free Yandex Direct API client."""
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

PRODUCTION_API_BASE = "https://api.direct.yandex.com/json/v501"
SANDBOX_API_BASE = "https://api-sandbox.direct.yandex.com/json/v5"
API_BASE = PRODUCTION_API_BASE
SUPPORTED_ENVIRONMENTS = {"production", "sandbox"}
SUPPORTED_SERVICES = {
    "adextensions",
    "adgroups",
    "adimages",
    "ads",
    "advideos",
    "agencyclients",
    "audiencetargets",
    "bids",
    "businesses",
    "bidmodifiers",
    "campaigns",
    "changes",
    "clients",
    "creatives",
    "dictionaries",
    "feeds",
    "keywordbids",
    "keywords",
    "keywordsresearch",
    "leads",
    "negativekeywordsharedsets",
    "retargetinglists",
    "sitelinks",
    "strategies",
    "turbopages",
}
READ_METHODS = {
    "check",
    "checkcampaigns",
    "checkdictionaries",
    "get",
    "getchanges",
}
AUTH_PRINCIPAL_DOMAIN = b"yandex-direct-auth-principal/v1"


class YandexDirectError(RuntimeError):
    def __init__(self, message: str, *, error_type: str = "api"):
        super().__init__(message)
        self.error_type = error_type


def is_read_method(method: str) -> bool:
    return method.strip().casefold() in READ_METHODS


def auth_principal_binding(token: str) -> str:
    return hmac.new(
        token.encode("utf-8"),
        AUTH_PRINCIPAL_DOMAIN,
        hashlib.sha256,
    ).hexdigest()


def emit_cli_error(error_type: str, message: str) -> int:
    json.dump({"error": {"type": error_type, "message": message}}, sys.stderr, ensure_ascii=False)
    sys.stderr.write("\n")
    return 2


def validate_service(service: str) -> str:
    if service != service.strip() or service != service.lower():
        raise ValueError("service must be an exact lowercase Yandex Direct service name")
    if service not in SUPPORTED_SERVICES:
        raise ValueError(f"unsupported Yandex Direct service: {service!r}")
    return service


def validate_environment(environment: str) -> str:
    if environment not in SUPPORTED_ENVIRONMENTS:
        raise ValueError(f"unsupported Yandex Direct environment: {environment!r}")
    return environment


@dataclass
class YandexDirectClient:
    token: str
    client_login: str | None = None
    language: str = "ru"
    timeout: int = 60
    opener: Callable[..., Any] = _http.urlopen
    environment: str = "production"

    def __post_init__(self) -> None:
        validate_environment(self.environment)

    def endpoint(self, service: str) -> str:
        service = validate_service(service)
        base = PRODUCTION_API_BASE if self.environment == "production" else SANDBOX_API_BASE
        return f"{base}/{service}"

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
        normalized_service = validate_service(service)
        normalized_method = method.strip().lower()
        return {
            "schema": "yandex-ai-approval/v1",
            "plugin": "yandex-direct",
            "operation": f"{normalized_service}.{normalized_method}",
            "method": "POST",
            "target": {
                "environment": self.environment,
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
                "environment": self.environment,
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
            raise YandexDirectError(str(exc), error_type=exc.error_type) from exc

        if data.get("error"):
            err = data["error"]
            request_id = transport.get("request_id") or data.get("request_id") or data.get("RequestId")
            suffix = f" request_id={request_id}" if request_id else ""
            raise YandexDirectError(f"Yandex Direct API error: {err}{suffix}", error_type="api")
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
    parser = argparse.ArgumentParser(description="Yandex Direct API helper")
    parser.add_argument("service", help="Exact supported service name, e.g. campaigns")
    parser.add_argument("method", help="get, add, update, set, ...")
    parser.add_argument("--params", help="JSON object with method params")
    parser.add_argument("--params-file", help="Path to JSON params file")
    parser.add_argument("--client-login", default=os.getenv("YANDEX_DIRECT_CLIENT_LOGIN"))
    parser.add_argument("--sandbox", action="store_true", help="Use the official Yandex Direct sandbox endpoint")
    parser.add_argument("--execute", action="store_true", help="Execute consequential operation")
    parser.add_argument("--approve", help="Full preview_id for the exact consequential preview")
    parser.add_argument("--dry-run", action="store_true", help="Preview any operation")
    args = parser.parse_args(argv)

    token = os.getenv("YANDEX_DIRECT_TOKEN")
    if not token:
        return emit_cli_error("validation", "YANDEX_DIRECT_TOKEN environment variable is required")

    try:
        if args.params and args.params_file:
            raise ValueError("Use only one of --params or --params-file")
        validate_service(args.service)
        params = _load_params(args)
        is_write = not is_read_method(args.method)
        dry_run = args.dry_run or (is_write and not args.execute)
        environment = "sandbox" if args.sandbox else "production"

        client = YandexDirectClient(
            token,
            client_login=args.client_login,
            environment=environment,
        )
        result = client.request(
            args.service,
            args.method,
            params,
            dry_run=dry_run,
            approve=args.approve,
        )
    except json.JSONDecodeError as exc:
        return emit_cli_error("input", str(exc))
    except OSError as exc:
        return emit_cli_error("input", str(exc))
    except YandexDirectError as exc:
        return emit_cli_error(exc.error_type, str(exc))
    except ValueError as exc:
        return emit_cli_error("validation", str(exc))

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    if is_write and dry_run:
        sys.stderr.write(
            "Preview only. Re-run with --execute --approve <preview_id> after the user approves this exact payload.\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())