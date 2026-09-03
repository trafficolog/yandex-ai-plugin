from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

ERROR = "execution requires approval of the exact preview; generate and show a fresh preview first"


def _canonical_json(envelope: Mapping[str, Any]) -> str:
    return json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def preview_id(envelope: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(envelope).encode("utf-8")).hexdigest()


def require_approval(envelope: Mapping[str, Any], supplied: str | None) -> str:
    expected = preview_id(envelope)
    if not supplied or supplied != expected:
        raise ValueError(ERROR)
    return expected
