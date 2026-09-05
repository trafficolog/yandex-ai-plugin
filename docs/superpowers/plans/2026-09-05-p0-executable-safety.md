# P0 Executable Safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace heterogeneous `yandex-ai-approval/v1` write gates in Direct, Metrika, and Webmaster with one mechanically convergent `yandex-ai-approval/v2` contract that binds target, authenticated principal, operation scale, risk context, and declared safety capability, adds a mechanical bulk gate, and returns `yandex-ai-execution/v1` receipts.

**Architecture:** Direct is the reference implementation. Each independently installable write-capable plugin keeps its own local `_approval.py` canonicalizer and gains its own local `_safety.py`; no root runtime dependency is introduced. Repository tests verify behavioural convergence by running each plugin in isolation. Generic operations whose cardinality cannot be derived safely are `UNKNOWN` scale and require `--ack-bulk`.

**Tech Stack:** Python 3.10/3.13 stdlib only, `unittest`, argparse, existing repository validator/contract matrix, existing generic immutable release publisher.

**Spec:** `docs/superpowers/specs/2026-09-05-p0-executable-safety-design.md`

## Global constraints

- Approval schema: `yandex-ai-approval/v2`.
- Execution receipt schema: `yandex-ai-execution/v1`.
- Repository policy: `BULK_THRESHOLD = 20`.
- Cardinality shape: `scale=KNOWN|UNKNOWN`; unknown uses `items=null`, `bulk=true`.
- Bulk or unknown-scale execution requires exact `--approve <preview_id>` plus `--ack-bulk`.
- A `yandex-ai-approval/v1` digest never authorizes a v2 write.
- Raw OAuth/API credentials never appear in previews, receipts, errors, fixtures, or committed docs.
- Read-only operations stay approval-free.
- SEO and Marketing remain Yandex-credential/transport-free; owning service plugins execute writes.
- P0 creates no `.yandex-ai/`, `decisions.jsonl`, durable rollback storage, dashboard, Electron app, or new Yandex plugin.
- Rollback is never automatic. Until a callable, separately approved restore/compensating path has executable tests, advertise `rollback=NOT_AVAILABLE`.
- `EXECUTED` and `VERIFIED` are separate facts. The initial P0 implementation uses `RESPONSE_ONLY` + `UNVERIFIED` unless an operation-specific tested read-back contract is deliberately added.
- Version/release surfaces are staged only after runtime, plugin, root, and documentation tests are green.

## File map

### New local runtime files

- `plugins/yandex-direct/scripts/_safety.py`
- `plugins/yandex-metrika/scripts/_safety.py`
- `plugins/yandex-webmaster/scripts/_safety.py`

Each local kernel exposes these exact interfaces:

```text
APPROVAL_SCHEMA: str = "yandex-ai-approval/v2"
EXECUTION_SCHEMA: str = "yandex-ai-execution/v1"
BULK_THRESHOLD: int = 20
principal_binding(token: str, *, domain: bytes) -> str
known_cardinality(items: int, *, artifact_rows: int | None = None) -> dict[str, object]
unknown_cardinality(*, artifact_rows: int | None = None) -> dict[str, object]
require_bulk_ack(cardinality: dict[str, object], ack_bulk: bool) -> None
execution_receipt(preview_id: str, plugin: str, operation: str, target: dict[str, object], cardinality: dict[str, object], result: object, verification_capability: str, verification_state: str, rollback_capability: str) -> dict[str, object]
```

`_approval.py` remains the local deterministic SHA-256 canonicalizer; P0 changes the envelopes passed into it, not its hashing algorithm.

### Runtime files modified

- `plugins/yandex-direct/scripts/yd_api.py`
- `plugins/yandex-metrika/scripts/ym_api.py`
- `plugins/yandex-metrika/scripts/ym_logs.py`
- `plugins/yandex-metrika/scripts/ym_import.py`
- `plugins/yandex-webmaster/scripts/yw_api.py`

### Tests

- `plugins/yandex-direct/tests/test_approval.py`
- `plugins/yandex-direct/tests/test_yd_api.py`
- `plugins/yandex-direct/tests/test_safety.py` (new)
- `plugins/yandex-metrika/tests/test_approval.py`
- `plugins/yandex-metrika/tests/test_ym_api.py`
- `plugins/yandex-metrika/tests/test_ym_logs.py`
- `plugins/yandex-metrika/tests/test_ym_import.py`
- `plugins/yandex-metrika/tests/test_safety.py` (new)
- `plugins/yandex-webmaster/tests/test_approval.py`
- `plugins/yandex-webmaster/tests/test_yw_api.py`
- `plugins/yandex-webmaster/tests/test_safety.py` (new)
- `tests/test_p0_executable_safety_contract.py` (new)
- `tests/test_documentation_ux_contracts.py`
- `tests/test_repository_1_1_0_release_surfaces.py` (new, final staging only)
- `docs/CONTRACT_MATRIX.json`

### Production documentation and release files

- `docs/PLUGIN_STANDARD.md`, `docs/PLUGIN_STANDARD.en.md`
- `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE.en.md`
- `SECURITY.md`, `SECURITY.en.md`
- Direct/Metrika/Webmaster `references/safety.md`
- Direct/Metrika/Webmaster `README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`
- Direct/Metrika/Webmaster `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- root `README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`
- `.github/releases/1.1.0.md`
- `.github/releases/yandex-direct-2.1.0.md`
- `.github/releases/yandex-metrika-2.1.0.md`
- `.github/releases/yandex-webmaster-2.1.0.md`
- `.github/releases/release.json`

---

## Task 1: Direct approval/v2 kernel and reference envelope

**Files**
- Create: `plugins/yandex-direct/scripts/_safety.py`
- Create: `plugins/yandex-direct/tests/test_safety.py`
- Modify: `plugins/yandex-direct/tests/test_approval.py`
- Modify: `plugins/yandex-direct/scripts/yd_api.py`
- Modify: `plugins/yandex-direct/tests/test_yd_api.py`
- Create: `tests/test_p0_executable_safety_contract.py`

**Produces**
- Direct local safety kernel.
- Direct v2 envelope.
- Direct-only root smoke test; Task 5 expands it to all three plugins.

- [ ] **Step 1: Write the Direct local-kernel RED test**

Create `plugins/yandex-direct/tests/test_safety.py`:

```python
import unittest
from scripts import _safety


class SafetyKernelTests(unittest.TestCase):
    def test_exact_contract(self):
        self.assertEqual(_safety.APPROVAL_SCHEMA, "yandex-ai-approval/v2")
        self.assertEqual(_safety.EXECUTION_SCHEMA, "yandex-ai-execution/v1")
        self.assertEqual(_safety.BULK_THRESHOLD, 20)
        self.assertEqual(
            _safety.known_cardinality(3),
            {"scale": "KNOWN", "items": 3, "threshold": 20, "bulk": False},
        )
        self.assertEqual(
            _safety.unknown_cardinality(),
            {"scale": "UNKNOWN", "items": None, "threshold": 20, "bulk": True},
        )

    def test_bulk_ack_gate(self):
        _safety.require_bulk_ack(_safety.known_cardinality(20), False)
        with self.assertRaisesRegex(ValueError, "ack-bulk"):
            _safety.require_bulk_ack(_safety.known_cardinality(21), False)
        with self.assertRaisesRegex(ValueError, "ack-bulk"):
            _safety.require_bulk_ack(_safety.unknown_cardinality(), False)
        _safety.require_bulk_ack(_safety.known_cardinality(21), True)

    def test_principal_binding_is_stable_and_token_sensitive(self):
        first = _safety.principal_binding("secret-a", domain=b"yandex-direct-auth-principal/v2")
        same = _safety.principal_binding("secret-a", domain=b"yandex-direct-auth-principal/v2")
        changed = _safety.principal_binding("secret-b", domain=b"yandex-direct-auth-principal/v2")
        self.assertEqual(first, same)
        self.assertNotEqual(first, changed)
        self.assertNotIn("secret-a", first)
```

- [ ] **Step 2: Update approval canonicalizer tests to use v2 sample envelopes**

In `plugins/yandex-direct/tests/test_approval.py`, replace sample schema literals `yandex-ai-approval/v1` with `yandex-ai-approval/v2`. Keep the existing assertions that canonical JSON is key-order independent and missing/wrong approval does not leak the expected digest.

- [ ] **Step 3: Add Direct envelope RED tests**

Append to `TestYandexDirectClient`:

```python
def test_v2_envelope_binds_target_principal_and_scale(self):
    client = YandexDirectClient("secret-token", client_login="client-a")
    envelope = client.approval_envelope(
        "campaigns", "update", {"Campaigns": [{"Id": 1}, {"Id": 2}]}
    )
    self.assertEqual(envelope["schema"], "yandex-ai-approval/v2")
    self.assertEqual(envelope["target"]["client_login"], "client-a")
    self.assertIn("auth_principal_binding", envelope["target"])
    self.assertEqual(envelope["cardinality"]["items"], 2)
    self.assertFalse(envelope["cardinality"]["bulk"])
    self.assertNotIn("secret-token", str(envelope))


def test_v1_digest_cannot_authorize_v2_execution(self):
    client = YandexDirectClient("token", client_login="client")
    params = {"Campaigns": [{"Id": 123}]}
    legacy = {
        "schema": "yandex-ai-approval/v1",
        "plugin": "yandex-direct",
        "operation": "campaigns.update",
        "method": "POST",
        "target": {"environment": "production", "client_login": "client"},
        "url": client.endpoint("campaigns"),
        "body": client.body("update", params),
        "artifacts": [],
    }
    with patch("scripts.yd_api._http.request_json") as request_json:
        with self.assertRaises(ValueError):
            client.request("campaigns", "update", params, approve=preview_id(legacy))
    request_json.assert_not_called()
```

- [ ] **Step 4: Add a Direct-only root smoke RED test**

Create `tests/test_p0_executable_safety_contract.py`:

```python
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class P0ExecutableSafetyContractTests(unittest.TestCase):
    def test_direct_has_local_v2_kernel(self):
        text = (ROOT / "plugins/yandex-direct/scripts/_safety.py").read_text(encoding="utf-8")
        self.assertIn('APPROVAL_SCHEMA = "yandex-ai-approval/v2"', text)
        self.assertIn("BULK_THRESHOLD = 20", text)
```

- [ ] **Step 5: Run RED**

```bash
(cd plugins/yandex-direct && python -m unittest tests.test_safety tests.test_approval tests.test_yd_api -v)
python -m unittest tests.test_p0_executable_safety_contract -v
```

Expected: missing `_safety.py` and v2 envelope assertions fail. No write transport is called by approval-failure tests.

- [ ] **Step 6: Implement `plugins/yandex-direct/scripts/_safety.py`**

```python
from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Any

APPROVAL_SCHEMA = "yandex-ai-approval/v2"
EXECUTION_SCHEMA = "yandex-ai-execution/v1"
BULK_THRESHOLD = 20


def principal_binding(token: str, *, domain: bytes) -> str:
    return hmac.new(token.encode("utf-8"), domain, hashlib.sha256).hexdigest()


def known_cardinality(items: int, *, artifact_rows: int | None = None) -> dict[str, object]:
    if items < 0:
        raise ValueError("cardinality items must be non-negative")
    result: dict[str, object] = {
        "scale": "KNOWN",
        "items": items,
        "threshold": BULK_THRESHOLD,
        "bulk": items > BULK_THRESHOLD,
    }
    if artifact_rows is not None:
        result["artifact_rows"] = artifact_rows
    return result


def unknown_cardinality(*, artifact_rows: int | None = None) -> dict[str, object]:
    result: dict[str, object] = {
        "scale": "UNKNOWN",
        "items": None,
        "threshold": BULK_THRESHOLD,
        "bulk": True,
    }
    if artifact_rows is not None:
        result["artifact_rows"] = artifact_rows
    return result


def require_bulk_ack(cardinality: dict[str, object], ack_bulk: bool) -> None:
    if cardinality.get("bulk") is True and not ack_bulk:
        raise ValueError(
            "bulk or unknown-scale execution requires --ack-bulk after reviewing the exact preview"
        )


def execution_receipt(
    *,
    preview_id: str,
    plugin: str,
    operation: str,
    target: dict[str, object],
    cardinality: dict[str, object],
    result: Any,
    verification_capability: str,
    verification_state: str,
    rollback_capability: str,
) -> dict[str, object]:
    return {
        "schema": EXECUTION_SCHEMA,
        "execution_id": secrets.token_hex(16),
        "preview_id": preview_id,
        "plugin": plugin,
        "operation": operation,
        "target": target,
        "cardinality": cardinality,
        "execution": {"state": "EXECUTED"},
        "verification": {
            "capability": verification_capability,
            "state": verification_state,
        },
        "rollback": {
            "capability": rollback_capability,
            "snapshot_available": False,
        },
        "result": result,
    }
```

- [ ] **Step 7: Convert Direct `approval_envelope()` to v2**

Add `_safety` import and this conservative cardinality registry:

```python
ENTITY_LIST_KEYS = {
    "campaigns": "Campaigns",
    "adgroups": "AdGroups",
    "ads": "Ads",
    "keywords": "Keywords",
    "bids": "Bids",
    "feeds": "Feeds",
    "creatives": "Creatives",
}


def mutation_cardinality(service: str, params: Mapping[str, Any] | None) -> dict[str, object]:
    key = ENTITY_LIST_KEYS.get(service)
    value = (params or {}).get(key) if key else None
    if isinstance(value, list):
        return _safety.known_cardinality(len(value))
    return _safety.unknown_cardinality()
```

Keep `auth_principal_binding(token)` as a compatibility wrapper but change its domain separator to `b"yandex-direct-auth-principal/v2"` and implement it through `_safety.principal_binding`.

The envelope must contain:

```python
{
    "schema": _safety.APPROVAL_SCHEMA,
    "plugin": "yandex-direct",
    "operation": f"{normalized_service}.{normalized_method}",
    "request": {
        "method": "POST",
        "environment": self.environment,
        "api_version": "v501",
        "url": self.endpoint(service),
        "path": normalized_service,
        "query": {},
        "body": self.body(method, params),
    },
    "target": {
        "client_login": self.client_login,
        "auth_principal_binding": auth_principal_binding(self.token),
    },
    "artifacts": [],
    "cardinality": mutation_cardinality(normalized_service, params),
    "safety": {
        "verification": "RESPONSE_ONLY",
        "rollback": "NOT_AVAILABLE",
        "risk_flags": [],
    },
}
```

- [ ] **Step 8: Run Task 1 GREEN**

```bash
(cd plugins/yandex-direct && python -m unittest discover -s tests -v && python -m compileall -q scripts)
python -m unittest tests.test_p0_executable_safety_contract -v
```

- [ ] **Step 9: Commit**

```bash
git add plugins/yandex-direct/scripts/_safety.py plugins/yandex-direct/scripts/yd_api.py plugins/yandex-direct/tests/test_safety.py plugins/yandex-direct/tests/test_approval.py plugins/yandex-direct/tests/test_yd_api.py tests/test_p0_executable_safety_contract.py
git commit -m "feat(direct): introduce approval v2 safety kernel"
```

---

## Task 2: Direct bulk gate and execution receipt

**Files**
- Modify: `plugins/yandex-direct/scripts/yd_api.py`
- Modify: `plugins/yandex-direct/tests/test_yd_api.py`

**Produces**
- `YandexDirectClient.request(..., ack_bulk: bool = False)`.
- CLI `--ack-bulk`.
- Consequential write receipts; read response shape remains unchanged.

- [ ] **Step 1: Write RED tests**

```python
def test_bulk_write_needs_ack_before_transport(self):
    client = YandexDirectClient("token", client_login="client")
    params = {"Campaigns": [{"Id": i} for i in range(21)]}
    approve = preview_id(client.approval_envelope("campaigns", "update", params))
    with patch("scripts.yd_api._http.request_json") as request_json:
        with self.assertRaisesRegex(ValueError, "ack-bulk"):
            client.request("campaigns", "update", params, approve=approve)
    request_json.assert_not_called()


def test_unknown_scale_needs_ack_before_transport(self):
    client = YandexDirectClient("token")
    params = {"OpaqueMutation": {"Id": 1}}
    approve = preview_id(client.approval_envelope("strategies", "update", params))
    with patch("scripts.yd_api._http.request_json") as request_json:
        with self.assertRaisesRegex(ValueError, "ack-bulk"):
            client.request("strategies", "update", params, approve=approve)
    request_json.assert_not_called()


def test_write_returns_execution_receipt(self):
    client = YandexDirectClient("token", client_login="client")
    params = {"Campaigns": [{"Id": 123}]}
    approve = preview_id(client.approval_envelope("campaigns", "update", params))
    payload = {"result": {"UpdateResults": [{"Id": 123}]}}
    with patch("scripts.yd_api._http.request_json", return_value=(payload, {})):
        receipt = client.request("campaigns", "update", params, approve=approve)
    self.assertEqual(receipt["schema"], "yandex-ai-execution/v1")
    self.assertEqual(receipt["preview_id"], approve)
    self.assertEqual(receipt["execution"]["state"], "EXECUTED")
    self.assertEqual(
        receipt["verification"],
        {"capability": "RESPONSE_ONLY", "state": "UNVERIFIED"},
    )
    self.assertEqual(receipt["rollback"]["capability"], "NOT_AVAILABLE")
```

- [ ] **Step 2: Run RED**

```bash
(cd plugins/yandex-direct && python -m unittest tests.test_yd_api -v)
```

- [ ] **Step 3: Enforce approval then scale acknowledgement before transport**

Change the request signature to include `ack_bulk: bool = False`. For consequential writes execute exactly:

```python
approved_preview = require_approval(envelope, approve)
_safety.require_bulk_ack(envelope["cardinality"], ack_bulk)
```

Only after these two calls invoke `_http.request_json`. Wrap the successful API payload in `_safety.execution_receipt` with `RESPONSE_ONLY`, `UNVERIFIED`, and `NOT_AVAILABLE`.

- [ ] **Step 4: Add CLI `--ack-bulk` and forward it**

```python
parser.add_argument(
    "--ack-bulk",
    action="store_true",
    help="Acknowledge bulk or unknown operation scale after reviewing the exact preview",
)
```

Update CLI mock functions in `test_yd_api.py` to accept and assert `ack_bulk`.

- [ ] **Step 5: Run GREEN and commit**

```bash
(cd plugins/yandex-direct && python -m unittest discover -s tests -v && python -m compileall -q scripts)
git add plugins/yandex-direct/scripts/yd_api.py plugins/yandex-direct/tests/test_yd_api.py
git commit -m "feat(direct): enforce bulk acknowledgement and receipts"
```

---

## Task 3: Metrika v2 parity for Management, Logs, and imports

**Files**
- Create: `plugins/yandex-metrika/scripts/_safety.py`
- Create: `plugins/yandex-metrika/tests/test_safety.py`
- Modify: `plugins/yandex-metrika/tests/test_approval.py`
- Modify: `plugins/yandex-metrika/scripts/ym_api.py`
- Modify: `plugins/yandex-metrika/scripts/ym_logs.py`
- Modify: `plugins/yandex-metrika/scripts/ym_import.py`
- Modify: `plugins/yandex-metrika/tests/test_ym_api.py`
- Modify: `plugins/yandex-metrika/tests/test_ym_logs.py`
- Modify: `plugins/yandex-metrika/tests/test_ym_import.py`

**Produces**
- Local v2 safety kernel with the exact interface from File map.
- Management generic mutations: `UNKNOWN` scale, bulk acknowledgement required.
- Logs `create`/`clean`: `KNOWN items=1`.
- Import upload: `KNOWN items=1`, plus approval-bound `artifact_rows`.

- [ ] **Step 1: Create explicit Metrika kernel RED tests**

Create `test_safety.py` with the same four behaviours expressed directly for Metrika:

```python
import unittest
from scripts import _safety


class SafetyKernelTests(unittest.TestCase):
    def test_exact_contract_and_cardinality(self):
        self.assertEqual(_safety.APPROVAL_SCHEMA, "yandex-ai-approval/v2")
        self.assertEqual(_safety.EXECUTION_SCHEMA, "yandex-ai-execution/v1")
        self.assertEqual(_safety.BULK_THRESHOLD, 20)
        self.assertEqual(
            _safety.known_cardinality(1, artifact_rows=37),
            {"scale": "KNOWN", "items": 1, "threshold": 20, "bulk": False, "artifact_rows": 37},
        )
        self.assertEqual(
            _safety.unknown_cardinality(),
            {"scale": "UNKNOWN", "items": None, "threshold": 20, "bulk": True},
        )

    def test_bulk_ack_and_principal_binding(self):
        with self.assertRaisesRegex(ValueError, "ack-bulk"):
            _safety.require_bulk_ack(_safety.unknown_cardinality(), False)
        _safety.require_bulk_ack(_safety.unknown_cardinality(), True)
        first = _safety.principal_binding("token-a", domain=b"yandex-metrika-auth-principal/v2")
        changed = _safety.principal_binding("token-b", domain=b"yandex-metrika-auth-principal/v2")
        self.assertNotEqual(first, changed)
        self.assertNotIn("token-a", first)
```

- [ ] **Step 2: Update Metrika approval canonicalizer tests to v2 sample schema**

Replace sample v1 schema literals in `test_approval.py` with v2 and preserve all digest non-leak assertions.

- [ ] **Step 3: Write Management RED tests**

Add tests proving:
- `prepare_request(... token="token-a")` emits `approval_schema == "yandex-ai-approval/v2"` and `UNKNOWN` cardinality.
- replay under `token-b` fails before `request_json`, even with `ack_bulk=True`.
- exact approval without `ack_bulk` fails before transport.
- exact approval plus `ack_bulk=True` returns a receipt with `RESPONSE_ONLY/UNVERIFIED/NOT_AVAILABLE`.

Use this principal replay assertion:

```python
preview = prepare_request(
    method="POST",
    path="counter/123/goals",
    token="token-a",
    body={"goal": {"name": "Lead"}},
)
with patch("scripts.ym_api.request_json") as request_json:
    with self.assertRaises(ValueError):
        run_request(
            method="POST",
            path="counter/123/goals",
            token="token-b",
            body={"goal": {"name": "Lead"}},
            execute=True,
            approve=preview["preview_id"],
            ack_bulk=True,
        )
request_json.assert_not_called()
```

- [ ] **Step 4: Write Logs RED tests**

For consequential `create` and `clean`, assert `cardinality == {"scale":"KNOWN","items":1,"threshold":20,"bulk":False}`. Build preview with `token-a`, execute under `token-b`, and prove the transport is not called. Exact single-operation approval must not require `ack_bulk` and successful execution must return a receipt.

- [ ] **Step 5: Write import RED tests**

Extend the existing exact-byte tests with:

```python
preview = prepare_import("offline-conversions", 123, path, "secret")
self.assertEqual(preview["approval_schema"], "yandex-ai-approval/v2")
self.assertEqual(preview["cardinality"]["scale"], "KNOWN")
self.assertEqual(preview["cardinality"]["items"], 1)
self.assertEqual(preview["cardinality"]["artifact_rows"], 1)
```

Also prove `token-a` preview cannot execute under `token-b` and file mutation after preview still blocks before upload. Existing `DIRECT_DUPLICATION_RISK` and `DIRECT_SOURCE_UNVERIFIED` tests remain mandatory.

- [ ] **Step 6: Run Metrika RED**

```bash
(cd plugins/yandex-metrika && python -m unittest discover -s tests -v)
```

- [ ] **Step 7: Create Metrika `_safety.py` with the exact Task 1 implementation**

Create a service-local file containing the exact constants/functions shown in Task 1 Step 6. This is copied source inside the independently installable plugin, not a cross-plugin import. Use Metrika's domain only at call sites: `b"yandex-metrika-auth-principal/v2"`.

- [ ] **Step 8: Convert all three Metrika envelopes to v2**

Change signatures so an executable envelope always receives the active token:

```text
ym_api.approval_envelope(..., token: str)
ym_logs.logs_approval_envelope(..., token: str)
ym_import.import_approval_envelope(..., token: str)
```

Update every existing test/helper call to these functions to supply the test token. Bind `auth_principal_binding` in `target` via `_safety.principal_binding`.

Use exact scale policy:

```text
Management generic consequential request -> unknown_cardinality()
Logs create/clean                         -> known_cardinality(1)
Import upload                             -> known_cardinality(1, artifact_rows=file_info["rows"])
```

Metrika import `risk_flags` contains the existing Direct-risk warning tokens when present, and those flags are included in the v2 envelope.

- [ ] **Step 9: Enforce bulk and return receipts**

`ym_api.run_request(..., ack_bulk: bool = False)` requires `ack_bulk` for every generic consequential Management mutation. Logs and import remain `items=1`, so their CLI paths do not add an unused `--ack-bulk` flag in P0. Every successful consequential Metrika path returns `yandex-ai-execution/v1` with `RESPONSE_ONLY`, `UNVERIFIED`, `NOT_AVAILABLE`.

- [ ] **Step 10: Add Management CLI `--ack-bulk` and update forwarding tests**

Add the same argparse flag text as Direct and pass it to `run_request`.

- [ ] **Step 11: Run GREEN and commit**

```bash
(cd plugins/yandex-metrika && python -m unittest discover -s tests -v && python -m compileall -q scripts)
git add plugins/yandex-metrika/scripts plugins/yandex-metrika/tests
git commit -m "feat(metrika): converge writes on approval v2"
```

---

## Task 4: Webmaster v2 parity and descriptor-derived scale

**Files**
- Create: `plugins/yandex-webmaster/scripts/_safety.py`
- Create: `plugins/yandex-webmaster/tests/test_safety.py`
- Modify: `plugins/yandex-webmaster/tests/test_approval.py`
- Modify: `plugins/yandex-webmaster/scripts/yw_api.py`
- Modify: `plugins/yandex-webmaster/tests/test_yw_api.py`

**Produces**
- OAuth-principal binding on every consequential v2 envelope.
- Exact batch scale for feed add/remove.
- Known single scale for currently verified specialized single-operation paths.
- Unknown scale for arbitrary generic writes.

- [ ] **Step 1: Create explicit Webmaster kernel RED tests**

Create `test_safety.py`:

```python
import unittest
from scripts import _safety


class SafetyKernelTests(unittest.TestCase):
    def test_exact_contract(self):
        self.assertEqual(_safety.APPROVAL_SCHEMA, "yandex-ai-approval/v2")
        self.assertEqual(_safety.EXECUTION_SCHEMA, "yandex-ai-execution/v1")
        self.assertEqual(_safety.BULK_THRESHOLD, 20)
        self.assertTrue(_safety.known_cardinality(21)["bulk"])
        self.assertEqual(_safety.unknown_cardinality()["scale"], "UNKNOWN")

    def test_ack_and_principal_binding(self):
        with self.assertRaisesRegex(ValueError, "ack-bulk"):
            _safety.require_bulk_ack(_safety.known_cardinality(21), False)
        _safety.require_bulk_ack(_safety.known_cardinality(21), True)
        first = _safety.principal_binding("oauth-a", domain=b"yandex-webmaster-auth-principal/v2")
        changed = _safety.principal_binding("oauth-b", domain=b"yandex-webmaster-auth-principal/v2")
        self.assertNotEqual(first, changed)
        self.assertNotIn("oauth-a", first)
```

- [ ] **Step 2: Update Webmaster approval canonicalizer tests to v2 samples**

Replace sample v1 schema literals in `test_approval.py` with v2 and preserve non-leak checks.

- [ ] **Step 3: Write scale RED tests for exact existing descriptor paths**

Assert `KNOWN items=1` for:

```text
/user/<id>/hosts/<host>/recrawl/queue
/user/<id>/hosts/<host>/user-added-sitemaps
/user/<id>/hosts/<host>/user-added-sitemaps/<sitemap_id>
/user/<id>/hosts/<host>/sitemaps/<sitemap_id>/recrawl
/user/<id>/hosts/<host>/feeds/add/start
/user/<id>/hosts/<host>/indexing/archive
```

Assert `items=len(body["feeds"])` for `/feeds/batch/add` and `items=len(body["urls"])` for `/feeds/batch/remove`. A batch of 21 is bulk.

- [ ] **Step 4: Write principal/secret RED tests**

A preview built with `oauth-secret-a` must fail before transport under `oauth-secret-b`, including operations without embedded feed credentials. Keep the existing assertions that embedded feed basic-auth user/password are redacted from preview and replaced with OAuth-keyed approval binding.

- [ ] **Step 5: Write receipt and bulk-gate RED tests**

Prove a 21-feed batch with exact approval but no `ack_bulk` fails before transport. With `ack_bulk=True`, successful transport returns `yandex-ai-execution/v1`, `RESPONSE_ONLY`, `UNVERIFIED`, `NOT_AVAILABLE`.

- [ ] **Step 6: Run RED**

```bash
(cd plugins/yandex-webmaster && python -m unittest discover -s tests -v)
```

- [ ] **Step 7: Create Webmaster `_safety.py` with the exact Task 1 implementation**

Create a service-local file containing the exact constants/functions from Task 1 Step 6. Webmaster calls `principal_binding` with domain `b"yandex-webmaster-auth-principal/v2"`.

- [ ] **Step 8: Implement exact conservative `webmaster_cardinality`**

```python
def webmaster_cardinality(path: str, body: Any | None) -> dict[str, object]:
    normalized = path.strip("/")
    if normalized.endswith("/feeds/batch/add") and isinstance(body, dict) and isinstance(body.get("feeds"), list):
        return _safety.known_cardinality(len(body["feeds"]))
    if normalized.endswith("/feeds/batch/remove") and isinstance(body, dict) and isinstance(body.get("urls"), list):
        return _safety.known_cardinality(len(body["urls"]))
    if normalized.endswith("/recrawl/queue"):
        return _safety.known_cardinality(1)
    if normalized.endswith("/user-added-sitemaps"):
        return _safety.known_cardinality(1)
    if "/user-added-sitemaps/" in normalized:
        return _safety.known_cardinality(1)
    if normalized.endswith("/recrawl"):
        return _safety.known_cardinality(1)
    if normalized.endswith("/feeds/add/start"):
        return _safety.known_cardinality(1)
    if normalized.endswith("/indexing/archive"):
        return _safety.known_cardinality(1)
    return _safety.unknown_cardinality()
```

Do not modify the specialized descriptor modules in this task; classifier rules adapt to their existing endpoint paths.

- [ ] **Step 9: Convert `yw_api.approval_envelope` to v2**

Require token for consequential envelope construction. Preserve `_approval_url_credentials()` and `_redact_preview_value()`. Add target OAuth principal binding, API version/path/query/body, cardinality, and safety metadata.

- [ ] **Step 10: Enforce approval then bulk ack before transport and return receipt**

Change `run_request` to accept `ack_bulk: bool = False`. For consequential writes call `require_approval` then `_safety.require_bulk_ack`; only then call injected transport or `request_json`. Wrap successful write response in execution receipt. Reads preserve current response shape.

- [ ] **Step 11: Add CLI `--ack-bulk`, run GREEN, commit**

```bash
(cd plugins/yandex-webmaster && python -m unittest discover -s tests -v && python -m compileall -q scripts)
git add plugins/yandex-webmaster/scripts/_safety.py plugins/yandex-webmaster/scripts/yw_api.py plugins/yandex-webmaster/tests/test_safety.py plugins/yandex-webmaster/tests/test_approval.py plugins/yandex-webmaster/tests/test_yw_api.py
git commit -m "feat(webmaster): converge writes on approval v2"
```

---

## Task 5: Repository behavioural convergence and ownership guard

**Files**
- Modify: `tests/test_p0_executable_safety_contract.py`
- Modify: `docs/CONTRACT_MATRIX.json`

**Produces**
- Cross-plugin behavioural proof while preserving independent installability.
- Exact traceability selectors for P0.

- [ ] **Step 1: Expand root test from Direct-only to three isolated plugins**

Add:

```python
import json
import subprocess
import sys

PLUGINS = ("yandex-direct", "yandex-metrika", "yandex-webmaster")


def run_plugin_python(plugin: str, source: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, "-c", source],
        cwd=ROOT / "plugins" / plugin,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)
```

For each plugin execute code that imports `scripts._safety`, serializes `APPROVAL_SCHEMA`, `EXECUTION_SCHEMA`, `BULK_THRESHOLD`, known(20), known(21), and unknown cardinality, then assert exact parity.

- [ ] **Step 2: Add isolated secret-sentinel tests**

Use `P0_SENTINEL_SECRET_6c90b2` as token inside each plugin subprocess. Generate a principal binding and representative receipt and assert the sentinel string is absent from serialized output.

- [ ] **Step 3: Update existing contract-matrix entries**

Keep IDs:

```text
direct.preview-bound-write
metrika.preview-bound-write
webmaster.preview-bound-write
```

Update `helpers` and exact `test_refs` so each references its v2 target/principal test, pre-transport approval/bulk rejection, and receipt test. Add infrastructure entry:

```json
{
  "id": "repository.p0-safety-convergence",
  "plugin": "repository",
  "status": "infrastructure",
  "skills": [],
  "helpers": ["plugins/yandex-direct/scripts/_safety.py", "plugins/yandex-metrika/scripts/_safety.py", "plugins/yandex-webmaster/scripts/_safety.py"],
  "test_refs": ["tests/test_p0_executable_safety_contract.py::P0ExecutableSafetyContractTests::test_local_safety_kernels_converge"],
  "references": [],
  "freshness_controlled_references": []
}
```

Use the exact final method name `test_local_safety_kernels_converge` in the root test.

- [ ] **Step 4: Verify existing cross-service ownership guard**

```bash
python -m unittest tests.test_validate_repo.ValidateRepositoryTests.test_cross_service_transport_is_rejected -v
```

No validator code change is planned: the existing guard is the canonical enforcement unless this exact test fails.

- [ ] **Step 5: Run root GREEN and commit**

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
git add tests/test_p0_executable_safety_contract.py docs/CONTRACT_MATRIX.json
git commit -m "test: enforce P0 write safety convergence"
```

---

## Task 6: Production docs and exact claims

**Files**
- Modify: `tests/test_documentation_ux_contracts.py`
- Modify: `docs/PLUGIN_STANDARD.md`, `docs/PLUGIN_STANDARD.en.md`
- Modify: `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE.en.md`
- Modify: `SECURITY.md`, `SECURITY.en.md`
- Modify: `plugins/yandex-direct/references/safety.md`
- Modify: `plugins/yandex-metrika/references/safety.md`
- Modify: `plugins/yandex-webmaster/references/safety.md`
- Modify: Direct/Metrika/Webmaster `README.md`, `README.en.md`

- [ ] **Step 1: Add documentation RED assertions**

In `tests/test_documentation_ux_contracts.py`, add a test loading both Plugin Standard language files and asserting exact markers:

```python
for marker in (
    "yandex-ai-approval/v2",
    "--ack-bulk",
    "yandex-ai-execution/v1",
    "RESPONSE_ONLY",
    "NOT_AVAILABLE",
):
    self.assertIn(marker, ru)
    self.assertIn(marker, en)
```

Also assert RU and EN each contain a sentence stating that standalone CLI approval does not prove that a human supplied the value in a later conversational turn.

- [ ] **Step 2: Run docs RED**

```bash
python -m unittest tests.test_documentation_ux_contracts tests.test_bilingual_docs tests.test_bilingual_docs_contracts -v
```

- [ ] **Step 3: Update standard, architecture, and security docs**

Canonical distinction must be explicit:

```text
Mechanically enforced by helper:
- exact v2 operation binding
- target/authenticated-principal binding
- scale/bulk gate
- service-owned execution boundary
- structured receipt and truthful capability declaration

Host/operator policy, not proven by standalone CLI:
- the user actually saw the preview
- the user personally supplied approval in a later conversational turn
```

Never call `RESPONSE_ONLY + UNVERIFIED` a verified final state.

- [ ] **Step 4: Update three service safety references and README capability descriptions**

Document `BULK_THRESHOLD=20` as repository safety policy, not Yandex API limit. Direct/Webmaster document `--ack-bulk` for bulk/unknown mutations; Metrika Management documents it for unknown generic writes. Logs/import explain why their API operation cardinality is one and import row count remains separate risk context.

- [ ] **Step 5: Run GREEN and commit**

```bash
python -m unittest tests.test_documentation_ux_contracts tests.test_bilingual_docs tests.test_bilingual_docs_contracts -v
python scripts/validate_repo.py
git add tests/test_documentation_ux_contracts.py docs/PLUGIN_STANDARD.md docs/PLUGIN_STANDARD.en.md docs/ARCHITECTURE.md docs/ARCHITECTURE.en.md SECURITY.md SECURITY.en.md plugins/yandex-direct/README.md plugins/yandex-direct/README.en.md plugins/yandex-direct/references/safety.md plugins/yandex-metrika/README.md plugins/yandex-metrika/README.en.md plugins/yandex-metrika/references/safety.md plugins/yandex-webmaster/README.md plugins/yandex-webmaster/README.en.md plugins/yandex-webmaster/references/safety.md
git commit -m "docs: document executable write safety v2"
```

---

## Task 7: Full pre-release verification

**Files:** no planned file changes.

- [ ] **Step 1: Compile repository and root scripts**

```bash
python -m compileall -q scripts plugins
```

- [ ] **Step 2: Run root validator/tests**

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

- [ ] **Step 3: Run exact CI-equivalent test+compile commands for all seven plugins**

```bash
(cd plugins/yandex-direct && python -m unittest discover -s tests -v && python -m compileall -q scripts)
(cd plugins/yandex-metrika && python -m unittest discover -s tests -v && python -m compileall -q scripts)
(cd plugins/yandex-webmaster && python -m unittest discover -s tests -v && python -m compileall -q scripts)
(cd plugins/yandex-wordstat && python -m unittest discover -s tests -v && python -m compileall -q scripts)
(cd plugins/yandex-search && python -m unittest discover -s tests -v && python -m compileall -q scripts)
(cd plugins/yandex-seo && python -m unittest discover -s tests -v && python -m compileall -q scripts)
(cd plugins/yandex-marketing && python -m unittest discover -s tests -v && python -m compileall -q scripts)
```

- [ ] **Step 4: Inspect exact scope against P0 base**

```bash
git diff --stat d036200564f9f1d66352894b71fd6a8b25a9c51f...HEAD
git diff --name-only d036200564f9f1d66352894b71fd6a8b25a9c51f...HEAD
```

Expected before release staging: Direct/Metrika/Webmaster safety runtime/tests, repository convergence matrix/test, bilingual safety docs, plus the approved spec/plan. No Wordstat/Search runtime change, no SEO/Marketing Yandex transport, no `.yandex-ai/`.

- [ ] **Step 5: Defect rule**

A defect found in verification is fixed only after adding the smallest reproducing regression test and observing it fail. After the fix rerun Steps 1–4. Do not create an empty verification commit.

---

## Task 8: Stage Repository 1.1.0 and three plugin 2.1.0 releases

**Files**
- Create: `tests/test_repository_1_1_0_release_surfaces.py`
- Modify: Direct/Metrika/Webmaster `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: Direct/Metrika/Webmaster `CHANGELOG.md`, `CHANGELOG.en.md`
- Modify: root `README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`
- Create: four release-note files listed in File map
- Modify: `.github/releases/release.json`

**Exact version target**

```text
Repository            1.1.0
Yandex Direct          2.1.0
Yandex Metrika         2.1.0
Yandex Webmaster       2.1.0
Yandex Wordstat        1.1.2 unchanged
Yandex Search          1.0.2 unchanged
Yandex SEO             1.1.2 unchanged
Yandex Marketing       1.1.0 unchanged
```

- [ ] **Step 1: Create intentional release-surface RED test**

`tests/test_repository_1_1_0_release_surfaces.py` must load `.github/releases/release.json`, all marketplace entries, and all seven Claude/Codex manifests. Assert the exact version target above, exact three plugin tags, and existence of all four new notes files. Run it while metadata still declares 1.0.10/old plugin versions and record the expected release-only failures.

- [ ] **Step 2: Bump only Direct/Metrika/Webmaster manifests and marketplace entries**

Set both Claude and Codex plugin manifests to 2.1.0 for these three plugins. Leave other four plugin manifests untouched.

- [ ] **Step 3: Add RU/EN plugin changelog entries**

Each 2.1.0 entry describes:
- approval/v2 target/principal/scale binding;
- `--ack-bulk` where applicable;
- structured execution receipts;
- truthful verification/rollback capability declaration.

- [ ] **Step 4: Create exact release notes**

Create:

```text
.github/releases/1.1.0.md
.github/releases/yandex-direct-2.1.0.md
.github/releases/yandex-metrika-2.1.0.md
.github/releases/yandex-webmaster-2.1.0.md
```

Repository note summarizes the P0 generation and explicitly states Wordstat/Search/SEO/Marketing SemVer is unchanged. Each plugin note describes only that plugin's behaviour change.

- [ ] **Step 5: Replace release manifest with the exact accepted schema**

```json
{
  "schema_version": 1,
  "repository": {
    "version": "1.1.0",
    "tag": "1.1.0",
    "title": "Repository 1.1.0",
    "notes_file": ".github/releases/1.1.0.md"
  },
  "plugins": [
    {
      "plugin": "yandex-direct",
      "version": "2.1.0",
      "tag": "yandex-direct-v2.1.0",
      "title": "Yandex Direct 2.1.0",
      "notes_file": ".github/releases/yandex-direct-2.1.0.md"
    },
    {
      "plugin": "yandex-metrika",
      "version": "2.1.0",
      "tag": "yandex-metrika-v2.1.0",
      "title": "Yandex Metrika 2.1.0",
      "notes_file": ".github/releases/yandex-metrika-2.1.0.md"
    },
    {
      "plugin": "yandex-webmaster",
      "version": "2.1.0",
      "tag": "yandex-webmaster-v2.1.0",
      "title": "Yandex Webmaster 2.1.0",
      "notes_file": ".github/releases/yandex-webmaster-2.1.0.md"
    }
  ]
}
```

- [ ] **Step 6: Update repository RU/EN release surfaces**

README current-release marker becomes `release-1.1.0`; root changelogs prepend `## [1.1.0]`. State exact three plugin bumps and unchanged versions of the other four.

- [ ] **Step 7: Run release GREEN**

```bash
python scripts/release_manifest.py validate
python scripts/validate_repo.py
python -m unittest tests.test_repository_1_1_0_release_surfaces -v
python -m unittest discover -s tests -v
python -m compileall -q scripts plugins
```

- [ ] **Step 8: Commit release staging**

```bash
git add .claude-plugin/marketplace.json .github/releases/release.json .github/releases/1.1.0.md .github/releases/yandex-direct-2.1.0.md .github/releases/yandex-metrika-2.1.0.md .github/releases/yandex-webmaster-2.1.0.md README.md README.en.md CHANGELOG.md CHANGELOG.en.md plugins/yandex-direct plugins/yandex-metrika plugins/yandex-webmaster tests/test_repository_1_1_0_release_surfaces.py
git diff --cached --name-only
git commit -m "release: stage executable safety 1.1.0"
```

The staged-name review must show no historical release-note edits and no changes under Wordstat/Search/SEO/Marketing.

---

## Task 9: PR, exact-head CI, merge, exact-main CI, immutable publish

**Files:** no planned implementation changes.

- [ ] **Step 1: Open one PR from the implementation branch**

PR body records exact base SHA, final head SHA, RED/GREEN evidence, local verification commands, scope, human-approval boundary limitation, verification/rollback limitations, intended versions/tags, and independent-review evidence or explicit absence of it.

- [ ] **Step 2: Require exact-head CI before merge**

All ten expected CI jobs must be successful on the current PR head: root Python 3.10, root Python 3.13, detect, and seven plugin jobs. Any head change invalidates previous CI evidence.

- [ ] **Step 3: Inspect PR review state without inventing review evidence**

Fetch reviews, review threads, and comments. Empty review state is reported as absence of independent review, not as a clean independent review.

- [ ] **Step 4: Merge with expected-head guard**

Use squash merge and pass the exact verified PR head SHA.

- [ ] **Step 5: Require successful exact-main CI**

Post-merge CI must be completed/successful and its `head_sha` must equal the current `main` SHA.

- [ ] **Step 6: Let the repository-native generic publisher publish the declared set**

The publisher is triggered from successful main CI. Do not manually create or move tags/releases.

- [ ] **Step 7: Verify exact immutable set**

All four tags must resolve to the same merge/main SHA:

```text
1.1.0
yandex-direct-v2.1.0
yandex-metrika-v2.1.0
yandex-webmaster-v2.1.0
```

For all four GitHub releases verify `draft=false`, `prerelease=false`, `immutable=true`, and exact target SHA. Verify Repository 1.0.10 and the previous plugin releases remain unchanged. Verify no Wordstat/Search/SEO/Marketing tag points to the new P0 SHA.

- [ ] **Step 8: Record final evidence on the PR**

Record exact merge/main SHA, post-merge CI run ID, publisher run ID, release IDs, tag SHAs, historical immutability result, and review-evidence status.

---

## Self-review mapping

- Spec §§6–8: Tasks 1, 3, 4 implement v2 envelope and target/principal binding.
- Spec §9: Tasks 1–4 implement known/unknown scale and `--ack-bulk`; Task 5 proves convergence.
- Spec §§10–14: Tasks 1–4 expose receipt/capability semantics without unsupported `READ_BACK` or rollback claims.
- Spec §15: Task 6 documents the human-approval boundary without overclaiming standalone CLI proof.
- Spec §16: Tasks 2–4 preserve `--execute --approve` and add the scale acknowledgement at execution surfaces that can require it.
- Spec §17: Tasks 1–4 test fail-closed pre-transport approval/scale failures.
- Spec §18: Task 5 owns behavioural convergence and exact contract-matrix traceability.
- Spec §19: execution order is Direct, Metrika, Webmaster, convergence, docs, verification, release.
- Spec §§20–21: Tasks 7–9 enforce green-before-version, exact-head merge, exact-main publisher, and immutable releases.
- Spec §22: no P1 project-memory surface is created.
