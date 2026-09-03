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
DIRECT_SOURCE_ALIASES = {
    "direct",
    "директ",
    "yandexdirect",
    "яндексдирект",
    "directyandex",
    "yadirect",
}
DIRECT_SOURCE_TOKENS = {"direct", "директ"}
DIRECT_UTM_SOURCES = {"yandex", "яндекс", "yandexdirect", "яндексдирект", "ya"}
DIRECT_UTM_MEDIA = {"cpc", "ppc", "paidsearch", "context", "контекст"}
DIRECT_TRAFFIC_SOURCE_DETAILS = {"yandexdirectstar"}


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


def _compact_label(value: str) -> str:
    return re.sub(r"[^0-9a-zа-яё]+", "", value.strip().casefold())


def _label_tokens(value: str) -> set[str]:
    return {
        token
        for token in re.split(r"[^0-9a-zа-яё]+", value.strip().casefold())
        if token
    }


def guard_expense_source(source: str | None) -> None:
    if source is None:
        return
    compact = _compact_label(source)
    tokens = _label_tokens(source)
    if compact in DIRECT_SOURCE_ALIASES or tokens & DIRECT_SOURCE_TOKENS:
        raise ValueError(
            "Do not import Yandex Direct expenses into Metrika: Direct cost data is transferred automatically and manual upload can duplicate expenses"
        )


def classify_expense_source(path: Path) -> str:
    """Classify expense provenance as DIRECT, NON_DIRECT, or UNVERIFIED.

    The CSV may identify acquisition either with UTM fields or Metrika's
    TrafficSource/TrafficSourceDetail fields. A row that only says generic
    advertising traffic is not enough evidence to exclude Yandex Direct.
    """
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames:
                return "UNVERIFIED"

            normalized_names = {_compact_label(name): name for name in reader.fieldnames if name}
            utm_source_key = normalized_names.get("utmsource")
            utm_medium_key = normalized_names.get("utmmedium")
            traffic_source_key = normalized_names.get("trafficsource")
            traffic_detail_key = normalized_names.get("trafficsourcedetail")

            saw_row = False
            saw_unverified = False
            for row in reader:
                saw_row = True
                utm_source = _compact_label(str(row.get(utm_source_key) or "")) if utm_source_key else ""
                utm_medium = _compact_label(str(row.get(utm_medium_key) or "")) if utm_medium_key else ""
                traffic_source = (
                    _compact_label(str(row.get(traffic_source_key) or "")) if traffic_source_key else ""
                )
                traffic_detail = (
                    _compact_label(str(row.get(traffic_detail_key) or "")) if traffic_detail_key else ""
                )

                if traffic_detail in DIRECT_TRAFFIC_SOURCE_DETAILS:
                    return "DIRECT"
                if utm_source in {"yandexdirect", "яндексдирект"}:
                    return "DIRECT"
                if utm_source in DIRECT_UTM_SOURCES and utm_medium in DIRECT_UTM_MEDIA:
                    return "DIRECT"

                # A non-Direct TrafficSourceDetail is explicit source evidence.
                if traffic_detail:
                    continue

                if utm_source:
                    # Generic Yandex UTM source without a medium remains ambiguous.
                    if utm_source in DIRECT_UTM_SOURCES and not utm_medium:
                        saw_unverified = True
                    continue

                if traffic_source:
                    # `ad` is a channel class, not provider identity.
                    if traffic_source == "ad":
                        saw_unverified = True
                    continue

                saw_unverified = True

            if not saw_row or saw_unverified:
                return "UNVERIFIED"
            return "NON_DIRECT"
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded") from exc


def detect_direct_expense_risk(path: Path) -> bool:
    """Detect proven Direct expense rows without claiming every ad row is Direct."""
    return classify_expense_source(path) == "DIRECT"


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
    allow_direct_risk: bool = False,
    **query: Any,
) -> dict[str, Any]:
    file_path = Path(file_path)
    warnings: list[str] = []
    if kind == "expenses":
        guard_expense_source(source)
        provenance = classify_expense_source(file_path)
        warning: str | None = None
        if provenance == "DIRECT":
            warning = "DIRECT_DUPLICATION_RISK"
            message = (
                f"{warning}: CSV contains Yandex Direct expense provenance. "
                "Metrika receives Yandex Direct costs automatically; inspect the file and "
                "use --allow-direct-risk only after confirming these rows are intentionally uploaded."
            )
        elif provenance == "UNVERIFIED":
            warning = "DIRECT_SOURCE_UNVERIFIED"
            message = (
                f"{warning}: CSV does not contain enough source evidence to rule out Yandex Direct expenses. "
                "Add UTMSource/UTMMedium or TrafficSourceDetail, or use --allow-direct-risk only after "
                "confirming the expense provenance."
            )
        else:
            message = ""

        if warning:
            if not allow_direct_risk:
                raise ValueError(message)
            warnings.append(warning)

        if source is not None and "provider" not in query:
            query["provider"] = source
    file_info = inspect_csv(file_path)
    url = import_url(kind, counter_id, query)
    return {
        "method": "POST",
        "url": url,
        "headers": redact_headers(oauth_headers(token, content_type="multipart/form-data")),
        "file": file_info,
        "kind": kind,
        "counter_id": int(counter_id),
        "consequential": True,
        "warnings": warnings,
    }


def execute_import(
    kind: str,
    counter_id: int,
    file_path: Path,
    token: str,
    *,
    source: str | None = None,
    allow_direct_risk: bool = False,
    timeout: int = 120,
    opener: Callable[..., Any] = urlopen,
    **query: Any,
) -> Any:
    prepare_import(
        kind,
        counter_id,
        file_path,
        token,
        source=source,
        allow_direct_risk=allow_direct_risk,
        **query,
    )
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
    parser.add_argument("--source", help="Provider/source label. Direct/Yandex Direct aliases are rejected for expenses.")
    parser.add_argument(
        "--allow-direct-risk",
        action="store_true",
        help="Allow an expense CSV with Direct or unverified source provenance after explicitly reviewing duplication risk.",
    )
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
        allow_direct_risk=args.allow_direct_risk,
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
        allow_direct_risk=args.allow_direct_risk,
        **query,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
