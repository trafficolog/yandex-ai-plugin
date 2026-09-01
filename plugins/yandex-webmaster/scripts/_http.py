from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.request import Request, urlopen


@dataclass
class WebmasterAPIError(RuntimeError):
    status: int
    code: str | None = None
    message: str | None = None

    def __str__(self) -> str:
        details = ": ".join(part for part in [self.code, self.message] if part)
        return f"Yandex Webmaster API HTTP {self.status}" + (f": {details}" if details else "")


def auth_headers(token: str, *, content_type: str = "application/json") -> dict[str, str]:
    if not token:
        raise ValueError("Yandex Webmaster OAuth token is required")
    headers = {"Authorization": f"OAuth {token}", "Accept": "application/json"}
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    result = dict(headers)
    if "Authorization" in result:
        result["Authorization"] = "OAuth ***"
    return result


def request_json(
    method: str,
    url: str,
    token: str,
    *,
    body: Any | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 30,
    opener: Callable[..., Any] = urlopen,
) -> tuple[int, Any]:
    request_headers = auth_headers(token)
    if headers:
        request_headers.update(headers)
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=data, headers=request_headers, method=method.upper())
    try:
        with opener(request, timeout=timeout) as response:
            raw = response.read()
            status = getattr(response, "status", response.getcode())
    except HTTPError as exc:
        raw = exc.read(65536)
        code = None
        message = None
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
            if isinstance(payload, dict):
                code = payload.get("error_code") or payload.get("code")
                message = payload.get("error_message") or payload.get("message")
        except (UnicodeDecodeError, json.JSONDecodeError):
            message = raw.decode("utf-8", errors="replace") if raw else None
        raise WebmasterAPIError(exc.code, code, message) from exc
    if not raw:
        return status, None
    text = raw.decode("utf-8")
    try:
        return status, json.loads(text)
    except json.JSONDecodeError:
        return status, text
