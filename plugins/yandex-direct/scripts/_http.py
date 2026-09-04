from __future__ import annotations

import json
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ERROR_BODY_LIMIT = 4096
SAFE_RESPONSE_HEADERS = {
    "RequestId": "request_id",
    "Units": "units",
    "Units-Used-Login": "units_used_login",
}


class DirectHTTPError(RuntimeError):
    """Operational failure raised by the Direct-local HTTP adapter."""


def redact_headers(headers: Mapping[str, str]) -> dict[str, str]:
    redacted = dict(headers)
    authorization = redacted.get("Authorization")
    if authorization:
        scheme, separator, _credential = authorization.partition(" ")
        redacted["Authorization"] = f"{scheme} ***" if separator else "***"
    return redacted


def _transport_metadata(headers: Mapping[str, str]) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for header_name, key in SAFE_RESPONSE_HEADERS.items():
        value = headers.get(header_name)
        if value is not None:
            metadata[key] = value
    return metadata


def request_json(
    url: str,
    headers: Mapping[str, str],
    body: Mapping[str, Any],
    *,
    timeout: int = 60,
    opener: Callable[..., Any] = urlopen,
) -> tuple[dict[str, Any], dict[str, str]]:
    payload = json.dumps(dict(body), ensure_ascii=False).encode("utf-8")
    request = Request(url, data=payload, headers=dict(headers), method="POST")
    try:
        with opener(request, timeout=timeout) as response:
            raw = response.read()
            transport = _transport_metadata(getattr(response, "headers", {}))
    except HTTPError as exc:
        raw = exc.read(ERROR_BODY_LIMIT)
        text = raw.decode("utf-8", errors="replace")
        raise DirectHTTPError(f"HTTP {exc.code}: {text}") from exc
    except URLError as exc:
        raise DirectHTTPError(f"Network error: {exc.reason}") from exc

    if not raw:
        return {}, transport
    text = raw.decode("utf-8", errors="replace")
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DirectHTTPError("Yandex Direct API returned invalid JSON") from exc
    if not isinstance(decoded, dict):
        raise DirectHTTPError("Yandex Direct API returned a non-object JSON payload")
    return decoded, transport
