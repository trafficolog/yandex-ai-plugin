from __future__ import annotations

import json
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def auth_headers(*, api_key: str | None = None, iam_token: str | None = None) -> dict[str, str]:
    api_key = (api_key or "").strip()
    iam_token = (iam_token or "").strip()
    if bool(api_key) == bool(iam_token):
        raise ValueError("Provide exactly one of api_key or iam_token")
    authorization = f"Api-Key {api_key}" if api_key else f"Bearer {iam_token}"
    return {
        "Authorization": authorization,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    redacted = dict(headers)
    value = redacted.get("Authorization", "")
    if value.startswith("Api-Key "):
        redacted["Authorization"] = "Api-Key ***"
    elif value.startswith("Bearer "):
        redacted["Authorization"] = "Bearer ***"
    return redacted


def request_json(
    method: str,
    url: str,
    headers: dict[str, str],
    body: Any | None = None,
    *,
    timeout: int = 30,
    opener: Callable[..., Any] = urlopen,
) -> Any:
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=data, headers=headers, method=method.upper())
    try:
        with opener(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as exc:
        raw = exc.read(4096)
        text = raw.decode("utf-8", errors="replace")
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = {"message": text}
        code = payload.get("code") or payload.get("error_code")
        message = payload.get("message") or payload.get("error_message") or text
        raise RuntimeError(f"Yandex Wordstat API HTTP {exc.code}: {code or 'ERROR'}: {message}") from exc
    if not raw:
        return None
    text = raw.decode("utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text
