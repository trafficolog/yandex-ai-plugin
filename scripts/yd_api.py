#!/usr/bin/env python3
"""Small dependency-free Yandex Direct API v501 client.

Read operations execute normally. Mutating operations should be previewed first;
the CLI requires --execute for write methods.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping

API_BASE = "https://api.direct.yandex.com/json/v501"
WRITE_METHODS = {
    "add", "update", "delete", "suspend", "resume", "archive", "unarchive",
    "setAuto", "moderate",
}


class YandexDirectError(RuntimeError):
    pass


@dataclass
class YandexDirectClient:
    token: str
    client_login: str | None = None
    language: str = "ru"
    timeout: int = 60

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

    def request(
        self,
        service: str,
        method: str,
        params: Mapping[str, Any] | None = None,
        *,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        body = self.body(method, params)
        if dry_run:
            safe_headers = self.headers()
            safe_headers["Authorization"] = "Bearer ***REDACTED***"
            return {
                "dry_run": True,
                "endpoint": self.endpoint(service),
                "headers": safe_headers,
                "body": body,
            }

        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint(service), data=payload, headers=self.headers(), method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise YandexDirectError(f"HTTP {exc.code}: {raw}") from exc
        except urllib.error.URLError as exc:
            raise YandexDirectError(f"Network error: {exc.reason}") from exc

        if isinstance(data, dict) and data.get("error"):
            err = data["error"]
            request_id = data.get("request_id") or data.get("RequestId")
            suffix = f" request_id={request_id}" if request_id else ""
            raise YandexDirectError(f"Yandex Direct API error: {err}{suffix}")
        return data


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
    parser.add_argument("method", help="get, add, update, suspend, ...")
    parser.add_argument("--params", help="JSON object with method params")
    parser.add_argument("--params-file", help="Path to JSON params file")
    parser.add_argument("--token", default=os.getenv("YANDEX_DIRECT_TOKEN"))
    parser.add_argument("--client-login", default=os.getenv("YANDEX_DIRECT_CLIENT_LOGIN"))
    parser.add_argument("--execute", action="store_true", help="Execute mutating operation")
    parser.add_argument("--dry-run", action="store_true", help="Preview any operation")
    args = parser.parse_args(argv)

    if not args.token:
        parser.error("Provide --token or YANDEX_DIRECT_TOKEN")
    if args.params and args.params_file:
        parser.error("Use only one of --params or --params-file")

    params = _load_params(args)
    is_write = args.method in WRITE_METHODS
    dry_run = args.dry_run or (is_write and not args.execute)

    client = YandexDirectClient(args.token, client_login=args.client_login)
    result = client.request(args.service, args.method, params, dry_run=dry_run)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    if is_write and dry_run:
        sys.stderr.write("Preview only. Re-run with --execute after reviewing the payload.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
