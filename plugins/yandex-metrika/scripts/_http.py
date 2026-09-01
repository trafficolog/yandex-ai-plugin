from __future__ import annotations

import json
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def oauth_headers(token: str, *, content_type: str = "application/json") -> dict[str, str]:
    if not token:
        raise ValueError("Yandex Metrika OAuth token is required")
    headers = {"Authorization": f"OAuth {token}", "Accept": "application/json"}
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    redacted = dict(headers)
    if "Authorization" in redacted:
        redacted["Authorization"] = "OAuth ***"
    return redacted


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
    request_headers = oauth_headers(token)
    if headers:
        request_headers.update(headers)
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=data, headers=request_headers, method=method.upper())
    try:
        with opener(request, timeout=timeout) as response:
            raw = response.read()
            status = getattr(response, "status", response.getcode())
    except HTTPError as exc:
        raw = exc.read(4096)
        text = raw.decode("utf-8", errors="replace")
        raise RuntimeError(f"Yandex Metrika API HTTP {exc.code}: {text}") from exc
    if not raw:
        return status, None
    text = raw.decode("utf-8")
    try:
        return status, json.loads(text)
    except json.JSONDecodeError:
        return status, text
