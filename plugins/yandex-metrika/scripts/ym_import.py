from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import re
import secrets
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from ._http import oauth_headers, redact_headers
except ImportError:
    from _http import oauth_headers, redact_headers

BASE = "https://api-metrika.yandex.net/management/v1/counter"
IMPORT_PATHS = {
    "offline-conversions": "offline_conversions/upload",
    "calls": "offline_conversions/upload_calls",
    "expenses": "expense/upload",
}


def inspect_csv(path: Path) -> dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded") from exc
    rows = list(csv.reader(text.splitlines()))
    if not rows or not rows[0]:
        raise ValueError("CSV must contain a header row")
    return {
        "rows": max(0, len(rows) - 1),
        "columns": rows[0],
        "size_bytes": path.stat().st_size,
        "encoding": "utf-8",
        "name": path.name,
    }


def _normalize_source(source: str) -> str:
    return re.sub(r"[.\s]+", " ", source.strip().casefold())


def guard_expense_source(source: str | None) -> None:
    if source is None:
        return
    normalized = _normalize_source(source)
    if normalized in {"direct", "yandex direct", "яндекс директ"}:
        raise ValueError(
            "Do not import Yandex Direct expenses into Metrika: Direct cost data is transferred automatically and manual upload can duplicate expenses"
        )


def import_url(kind: str, counter_id: int, query: dict[str, Any] | None = None) -> str:
    try:
        suffix = IMPORT_PATHS[kind]
    except KeyError as exc:
        raise ValueError(f"Unknown import kind: {kind}") from exc
    url = f"{BASE}/{int(counter_id)}/{suffix}"
    if query:
        clean = {k: v for k, v in query.items() if v is not None}
        if clean:
            url += "?" + urlencode(clean)
    return url


def build_multipart_file(path: Path, *, boundary: str | None = None) -> tuple[str, bytes]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    boundary = boundary or f"----YandexMetrika{secrets.token_hex(12)}"
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'.encode("utf-8"),
            b"Content-Type: text/csv\r\n\r\n",
            path.read_bytes(),
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    return f"multipart/form-data; boundary={boundary}", body


def prepare_import(
    kind: str,
    counter_id: int,
    file_path: Path,
    token: str,
    *,
    source: str | None = None,
    **query: Any,
) -> dict[str, Any]:
    if kind == "expenses":
        guard_expense_source(source)
        if source is not None and "provider" not in query:
            query["provider"] = source
    file_info = inspect_csv(Path(file_path))
    url = import_url(kind, counter_id, query)
    return {
        "method": "POST",
        "url": url,
        "headers": redact_headers(oauth_headers(token, content_type="multipart/form-data")),
        "file": file_info,
        "kind": kind,
        "counter_id": int(counter_id),
        "consequential": True,
    }


def execute_import(
    kind: str,
    counter_id: int,
    file_path: Path,
    token: str,
    *,
    source: str | None = None,
    timeout: int = 120,
    opener: Callable[..., Any] = urlopen,
    **query: Any,
) -> Any:
    prepare_import(kind, counter_id, file_path, token, source=source, **query)
    if kind == "expenses" and source is not None and "provider" not in query:
        query["provider"] = source
    url = import_url(kind, counter_id, query)
    content_type, body = build_multipart_file(Path(file_path))
    headers = oauth_headers(token, content_type=content_type)
    request = Request(url, data=body, headers=headers, method="POST")
    with opener(request, timeout=timeout) as response:
        raw = response.read()
    if not raw:
        return None
    return json.loads(raw.decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Yandex Metrika data import helper")
    parser.add_argument("kind", choices=sorted(IMPORT_PATHS))
    parser.add_argument("counter", type=int)
    parser.add_argument("file")
    parser.add_argument("--comment")
    parser.add_argument("--source", help="Provider/source label. Direct/Yandex Direct is rejected for expenses.")
    parser.add_argument("--new-goal-name", help="Calls import new_goal_name")
    parser.add_argument("--type", dest="offline_type", choices=["BASIC", "CALLS", "CHATS"])
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("YANDEX_METRIKA_TOKEN", "")
    query: dict[str, Any] = {"comment": args.comment}
    if args.kind == "calls":
        query["new_goal_name"] = args.new_goal_name
    if args.kind == "offline-conversions":
        query["type"] = args.offline_type
    preview = prepare_import(
        args.kind,
        args.counter,
        Path(args.file),
        token,
        source=args.source,
        **query,
    )
    if not args.execute:
        print(json.dumps({"dry_run": True, **preview}, ensure_ascii=False, indent=2))
        return 0
    payload = execute_import(
        args.kind,
        args.counter,
        Path(args.file),
        token,
        source=args.source,
        **query,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
