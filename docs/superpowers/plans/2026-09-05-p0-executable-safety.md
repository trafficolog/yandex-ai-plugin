# P0 Executable Safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the three write-capable service plugins' heterogeneous `yandex-ai-approval/v1` flows with one mechanically convergent `yandex-ai-approval/v2` contract that binds target/principal/scale/risk, adds `--ack-bulk`, and returns structured execution receipts without introducing a root runtime dependency.

**Architecture:** Direct is the reference implementation. Each owning service plugin keeps local `_approval.py` plus a small local `_safety.py`; repository-level tests verify behaviour rather than byte-identical source. Generic writes are safe by default: if cardinality cannot be proven, scale is `UNKNOWN` and execution requires `--ack-bulk`; verification is never advertised stronger than implemented, and the first P0 milestone uses `RESPONSE_ONLY` or `NOT_AVAILABLE` unless an operation has an explicit tested read-back adapter.

**Tech Stack:** Python 3.10/3.13 stdlib only, `unittest`, existing argparse CLIs, repository validator/contract matrix, existing immutable generic release publisher.

**Spec:** `docs/superpowers/specs/2026-09-05-p0-executable-safety-design.md`

## Global Constraints

- Approval schema is exactly `yandex-ai-approval/v2`; execution receipt schema is exactly `yandex-ai-execution/v1`.
- `BULK_THRESHOLD = 20`; scale is `KNOWN` or `UNKNOWN`; unknown scale uses `items: null`, `bulk: true`.
- Bulk/unknown execution requires both exact `--approve <preview_id>` and explicit `--ack-bulk`.
- Old `yandex-ai-approval/v1` preview IDs MUST NOT authorize v2 execution.
- Raw OAuth/API credentials MUST NOT appear in previews, receipts, errors, fixtures, or committed docs.
- Read-only operations remain approval-free.
- No root/shared runtime package is added; Direct, Metrika, and Webmaster remain independently installable.
- SEO/Marketing remain transport/credential-free and cannot execute owning-service writes.
- P0 does not create `.yandex-ai/`, `decisions.jsonl`, durable rollback storage, Electron/UI, or new Yandex plugins.
- Rollback is never automatic. A rollback/compensating write, if later implemented, is a fresh consequential operation with its own preview and approval.
- Until a tested operation-specific restore/read-back adapter exists, advertise `rollback=NOT_AVAILABLE`; do not infer rollback from HTTP symmetry.
- A successful mutation and successful verification are separate states; verification failure must not be represented as clean success.
- Repository CI remains green on Python 3.10 and 3.13 and all seven plugin jobs.
- Runtime/docs/release surfaces are not version-staged until the implementation is green.

---

## File map

### Local safety kernels

Create the same public interface independently in:

- `plugins/yandex-direct/scripts/_safety.py`
- `plugins/yandex-metrika/scripts/_safety.py`
- `plugins/yandex-webmaster/scripts/_safety.py`

Each file owns only common local mechanics:

```python
APPROVAL_SCHEMA = "yandex-ai-approval/v2"
EXECUTION_SCHEMA = "yandex-ai-execution/v1"
BULK_THRESHOLD = 20


def principal_binding(token: str, *, domain: bytes) -> str: ...
def known_cardinality(items: int, *, artifact_rows: int | None = None) -> dict[str, object]: ...
def unknown_cardinality(*, artifact_rows: int | None = None) -> dict[str, object]: ...
def require_bulk_ack(cardinality: dict[str, object], ack_bulk: bool) -> None: ...
def execution_receipt(*, preview_id: str, plugin: str, operation: str, target: dict[str, object], cardinality: dict[str, object], result: object, verification_capability: str, verification_state: str, rollback_capability: str) -> dict[str, object]: ...
```

Service-specific target extraction, artifact semantics, mutation cardinality rules, and verification capability selection stay in `yd_api.py`, `ym_api.py` / `ym_logs.py` / `ym_import.py`, and `yw_api.py` respectively.

### Existing runtime files modified

- `plugins/yandex-direct/scripts/_approval.py`
- `plugins/yandex-direct/scripts/yd_api.py`
- `plugins/yandex-metrika/scripts/_approval.py`
- `plugins/yandex-metrika/scripts/ym_api.py`
- `plugins/yandex-metrika/scripts/ym_logs.py`
- `plugins/yandex-metrika/scripts/ym_import.py`
- `plugins/yandex-webmaster/scripts/_approval.py`
- `plugins/yandex-webmaster/scripts/yw_api.py`

Specialized Webmaster descriptor files remain request-description owners; their payload shapes are consumed by `yw_api.py`. Only touch them if a failing test proves descriptor metadata is insufficient to derive safe cardinality.

### Tests

- Modify: `plugins/yandex-direct/tests/test_approval.py`
- Modify: `plugins/yandex-direct/tests/test_yd_api.py`
- Create: `plugins/yandex-direct/tests/test_safety.py`
- Modify: `plugins/yandex-metrika/tests/test_approval.py`
- Modify: `plugins/yandex-metrika/tests/test_ym_api.py`
- Modify: `plugins/yandex-metrika/tests/test_ym_logs.py`
- Modify: `plugins/yandex-metrika/tests/test_ym_import.py`
- Create: `plugins/yandex-metrika/tests/test_safety.py`
- Modify: `plugins/yandex-webmaster/tests/test_approval.py`
- Modify: `plugins/yandex-webmaster/tests/test_yw_api.py`
- Create: `plugins/yandex-webmaster/tests/test_safety.py`
- Create: `tests/test_p0_executable_safety_contract.py`
- Modify: `docs/CONTRACT_MATRIX.json`

### Production documentation/release surfaces

- `docs/PLUGIN_STANDARD.md`, `docs/PLUGIN_STANDARD.en.md`
- `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE.en.md`
- `SECURITY.md`, `SECURITY.en.md`
- Direct/Metrika/Webmaster `references/safety.md`
- Direct/Metrika/Webmaster `README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`
- Direct/Metrika/Webmaster `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- root `README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`
- `.github/releases/1.1.0.md`
- `.github/releases/release.json`
- release-surface regression tests created/updated only in the final staging task.

---

### Task 1: Direct approval/v2 kernel and reference envelope

**Files:**
- Create: `plugins/yandex-direct/scripts/_safety.py`
- Modify: `plugins/yandex-direct/scripts/_approval.py`
- Modify: `plugins/yandex-direct/scripts/yd_api.py`
- Create: `plugins/yandex-direct/tests/test_safety.py`
- Modify: `plugins/yandex-direct/tests/test_approval.py`
- Modify: `plugins/yandex-direct/tests/test_yd_api.py`
- Create: `tests/test_p0_executable_safety_contract.py`

**Interfaces:**
- Consumes: existing `preview_id(envelope)` / `require_approval(envelope, supplied)` SHA-256 canonicalization.
- Produces: `_safety.APPROVAL_SCHEMA`, `_safety.EXECUTION_SCHEMA`, `_safety.BULK_THRESHOLD`, `principal_binding`, `known_cardinality`, `unknown_cardinality`, `require_bulk_ack`, `execution_receipt`; `YandexDirectClient.approval_envelope()` returns v2.

- [ ] **Step 1: Add Direct RED tests for the local kernel**

Create `plugins/yandex-direct/tests/test_safety.py` with exact contract tests:

```python
import unittest

from scripts import _safety


class SafetyKernelTests(unittest.TestCase):
    def test_constants_are_exact(self):
        self.assertEqual(_safety.APPROVAL_SCHEMA, "yandex-ai-approval/v2")
        self.assertEqual(_safety.EXECUTION_SCHEMA, "yandex-ai-execution/v1")
        self.assertEqual(_safety.BULK_THRESHOLD, 20)

    def test_known_and_unknown_cardinality(self):
        self.assertEqual(
            _safety.known_cardinality(3),
            {"scale": "KNOWN", "items": 3, "threshold": 20, "bulk": False},
        )
        self.assertEqual(
            _safety.unknown_cardinality(),
            {"scale": "UNKNOWN", "items": None, "threshold": 20, "bulk": True},
        )

    def test_bulk_ack_is_required_for_bulk_and_unknown(self):
        with self.assertRaisesRegex(ValueError, "ack-bulk"):
            _safety.require_bulk_ack(_safety.known_cardinality(21), False)
        with self.assertRaisesRegex(ValueError, "ack-bulk"):
            _safety.require_bulk_ack(_safety.unknown_cardinality(), False)
        _safety.require_bulk_ack(_safety.known_cardinality(20), False)
        _safety.require_bulk_ack(_safety.known_cardinality(21), True)

    def test_principal_binding_is_stable_secret_free_and_token_sensitive(self):
        a = _safety.principal_binding("secret-a", domain=b"direct/v2")
        b = _safety.principal_binding("secret-a", domain=b"direct/v2")
        c = _safety.principal_binding("secret-b", domain=b"direct/v2")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotIn("secret", a)
```

- [ ] **Step 2: Add Direct RED tests for the v2 envelope and v1 invalidation**

Append to `TestYandexDirectClient`:

```python
def test_v2_envelope_binds_principal_target_and_scale(self):
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

- [ ] **Step 3: Add repository RED smoke test for the three required v2 local kernels**

Create `tests/test_p0_executable_safety_contract.py` with a static existence/schema check that is expected to fail until all three plugins migrate:

```python
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ("yandex-direct", "yandex-metrika", "yandex-webmaster")


class P0ExecutableSafetyContractTests(unittest.TestCase):
    def test_each_write_plugin_has_local_v2_safety_kernel(self):
        for plugin in PLUGINS:
            with self.subTest(plugin=plugin):
                text = (ROOT / "plugins" / plugin / "scripts" / "_safety.py").read_text(encoding="utf-8")
                self.assertIn('APPROVAL_SCHEMA = "yandex-ai-approval/v2"', text)
                self.assertIn("BULK_THRESHOLD = 20", text)
```

- [ ] **Step 4: Run RED tests**

Run:

```bash
python -m unittest \
  plugins/yandex-direct/tests/test_safety.py \
  plugins/yandex-direct/tests/test_approval.py \
  plugins/yandex-direct/tests/test_yd_api.py \
  tests/test_p0_executable_safety_contract.py -v
```

Expected: new `_safety`/v2 assertions fail; pre-existing v1 tests may also fail once updated. No transport mock should be called by a failing authorization test.

- [ ] **Step 5: Implement the minimal Direct local kernel**

`plugins/yandex-direct/scripts/_safety.py`:

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
        "scale": "KNOWN", "items": items, "threshold": BULK_THRESHOLD, "bulk": items > BULK_THRESHOLD
    }
    if artifact_rows is not None:
        result["artifact_rows"] = artifact_rows
    return result


def unknown_cardinality(*, artifact_rows: int | None = None) -> dict[str, object]:
    result: dict[str, object] = {
        "scale": "UNKNOWN", "items": None, "threshold": BULK_THRESHOLD, "bulk": True
    }
    if artifact_rows is not None:
        result["artifact_rows"] = artifact_rows
    return result


def require_bulk_ack(cardinality: dict[str, object], ack_bulk: bool) -> None:
    if cardinality.get("bulk") is True and not ack_bulk:
        raise ValueError("bulk or unknown-scale execution requires --ack-bulk after reviewing the exact preview")


def execution_receipt(*, preview_id: str, plugin: str, operation: str, target: dict[str, object], cardinality: dict[str, object], result: Any, verification_capability: str, verification_state: str, rollback_capability: str) -> dict[str, object]:
    return {
        "schema": EXECUTION_SCHEMA,
        "execution_id": secrets.token_hex(16),
        "preview_id": preview_id,
        "plugin": plugin,
        "operation": operation,
        "target": target,
        "cardinality": cardinality,
        "execution": {"state": "EXECUTED"},
        "verification": {"capability": verification_capability, "state": verification_state},
        "rollback": {"capability": rollback_capability, "snapshot_available": False},
        "result": result,
    }
```

- [ ] **Step 6: Convert Direct `approval_envelope()` to v2 and keep generic unknown-scale fail-closed**

In `yd_api.py`, import `_safety` and add a deliberately small cardinality registry:

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

Use `_safety.APPROVAL_SCHEMA`, `_safety.principal_binding(..., domain=b"yandex-direct-auth-principal/v2")`, nested `request`, `target`, `artifacts`, `cardinality`, and safety declaration:

```python
"safety": {
    "verification": "RESPONSE_ONLY",
    "rollback": "NOT_AVAILABLE",
    "risk_flags": [],
}
```

Do not claim `READ_BACK` in this task.

- [ ] **Step 7: Run Direct tests to GREEN**

```bash
python -m unittest discover -s plugins/yandex-direct/tests -p 'test_*.py' -v
```

Expected: all Direct tests pass, including v2 envelope determinism and v1 rejection.

- [ ] **Step 8: Commit Task 1**

```bash
git add plugins/yandex-direct/scripts plugins/yandex-direct/tests tests/test_p0_executable_safety_contract.py
git commit -m "feat(direct): introduce approval v2 safety kernel"
```

---

### Task 2: Direct bulk gate and execution receipt

**Files:**
- Modify: `plugins/yandex-direct/scripts/yd_api.py`
- Modify: `plugins/yandex-direct/tests/test_yd_api.py`

**Interfaces:**
- Consumes: Task 1 `_safety.require_bulk_ack()` and `execution_receipt()`.
- Produces: `YandexDirectClient.request(..., ack_bulk: bool = False)`; CLI `--ack-bulk`; consequential writes return receipt, reads preserve current raw read shape.

- [ ] **Step 1: Write RED tests for scale gate and receipt**

Add:

```python
def test_bulk_write_needs_ack_after_exact_approval(self):
    client = YandexDirectClient("token", client_login="client")
    params = {"Campaigns": [{"Id": i} for i in range(21)]}
    approve = preview_id(client.approval_envelope("campaigns", "update", params))
    with patch("scripts.yd_api._http.request_json") as request_json:
        with self.assertRaisesRegex(ValueError, "ack-bulk"):
            client.request("campaigns", "update", params, approve=approve)
    request_json.assert_not_called()


def test_unknown_scale_needs_ack(self):
    client = YandexDirectClient("token")
    params = {"SomeOpaqueMutation": {"Id": 1}}
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
    self.assertEqual(receipt["verification"], {"capability": "RESPONSE_ONLY", "state": "UNVERIFIED"})
    self.assertEqual(receipt["rollback"]["capability"], "NOT_AVAILABLE")
```

- [ ] **Step 2: Run RED test selection**

```bash
python -m unittest plugins/yandex-direct/tests/test_yd_api.py -v
```

Expected: failures for missing `ack_bulk` and receipt shape.

- [ ] **Step 3: Gate writes after exact approval and before transport**

Change signature:

```python
def request(..., dry_run: bool = False, approve: str | None = None, ack_bulk: bool = False) -> dict[str, Any]:
```

For consequential writes:

```python
approved_preview = require_approval(envelope, approve)
_safety.require_bulk_ack(envelope["cardinality"], ack_bulk)
```

Then wrap the successful API result with `_safety.execution_receipt(...)`. Use `verification_capability="RESPONSE_ONLY"`, `verification_state="UNVERIFIED"`, `rollback_capability="NOT_AVAILABLE"` until a tested operation-specific adapter exists.

- [ ] **Step 4: Add CLI `--ack-bulk` and forward it**

```python
parser.add_argument(
    "--ack-bulk",
    action="store_true",
    help="Acknowledge bulk or unknown operation scale after reviewing the exact preview",
)
```

Update CLI mock tests so `ack_bulk` is forwarded explicitly.

- [ ] **Step 5: Run Direct suite GREEN and compile**

```bash
python -m unittest discover -s plugins/yandex-direct/tests -p 'test_*.py' -v
python -m compileall -q plugins/yandex-direct/scripts
```

- [ ] **Step 6: Commit Task 2**

```bash
git add plugins/yandex-direct/scripts/yd_api.py plugins/yandex-direct/tests/test_yd_api.py
git commit -m "feat(direct): enforce bulk acknowledgement and receipts"
```

---

### Task 3: Metrika parity across Management, Logs, and imports

**Files:**
- Create: `plugins/yandex-metrika/scripts/_safety.py`
- Modify: `plugins/yandex-metrika/scripts/_approval.py`
- Modify: `plugins/yandex-metrika/scripts/ym_api.py`
- Modify: `plugins/yandex-metrika/scripts/ym_logs.py`
- Modify: `plugins/yandex-metrika/scripts/ym_import.py`
- Create: `plugins/yandex-metrika/tests/test_safety.py`
- Modify: `plugins/yandex-metrika/tests/test_approval.py`
- Modify: `plugins/yandex-metrika/tests/test_ym_api.py`
- Modify: `plugins/yandex-metrika/tests/test_ym_logs.py`
- Modify: `plugins/yandex-metrika/tests/test_ym_import.py`

**Interfaces:**
- Consumes: Task 1 local-kernel semantics, copied locally rather than imported cross-plugin.
- Produces: all Metrika consequential surfaces use v2 principal binding, scale gate, and receipt; import file SHA/risk semantics remain intact.

- [ ] **Step 1: Copy the Direct kernel interface into Metrika and add parity tests**

`test_safety.py` uses the same constants/cardinality/bulk/principal assertions as Direct but domain-sensitive test input is `b"yandex-metrika-auth-principal/v2"`.

- [ ] **Step 2: Write RED Management tests for token/principal invalidation and counter cardinality**

```python
def test_token_change_invalidates_management_approval(self):
    body = {"goal": {"name": "Lead"}}
    preview = prepare_request(method="POST", path="counter/123/goals", token="token-a", body=body)
    with patch("scripts.ym_api.request_json") as request_json:
        with self.assertRaises(ValueError):
            run_request(method="POST", path="counter/123/goals", token="token-b", body=body, execute=True, approve=preview["preview_id"], ack_bulk=True)
    request_json.assert_not_called()


def test_management_preview_is_v2_and_unknown_scale_is_bulk(self):
    preview = prepare_request(method="POST", path="counter/123/goals", token="secret", body={"goal": {"name": "Lead"}})
    self.assertEqual(preview["approval_schema"], "yandex-ai-approval/v2")
    self.assertEqual(preview["cardinality"]["scale"], "UNKNOWN")
    self.assertTrue(preview["cardinality"]["bulk"])
```

Generic Management mutations intentionally default to unknown scale because `ym_api.py` accepts arbitrary paths/bodies and cannot safely infer entity cardinality.

- [ ] **Step 3: Write RED Logs tests for known single-operation cardinality and principal binding**

For `create` and `clean`, cardinality is one server operation:

```python
preview = prepare_logs_request(123, "create", token="secret", query=query)
self.assertEqual(preview["cardinality"]["items"], 1)
self.assertFalse(preview["cardinality"]["bulk"])
```

Token change must invalidate the exact approval before `request_json`.

- [ ] **Step 4: Write RED import tests for artifact row context, principal binding, and exact bytes**

Extend existing import expectations:

```python
preview = prepare_import("offline-conversions", 123, path, "secret")
self.assertEqual(preview["cardinality"]["scale"], "KNOWN")
self.assertEqual(preview["cardinality"]["items"], 1)
self.assertEqual(preview["cardinality"]["artifact_rows"], 1)
self.assertEqual(preview["approval_schema"], "yandex-ai-approval/v2")
```

For import uploads, `items=1` means one upload operation. `artifact_rows` is risk context and is bound separately; do not pretend each CSV row is independently reversible.

- [ ] **Step 5: Run Metrika RED suite**

```bash
python -m unittest discover -s plugins/yandex-metrika/tests -p 'test_*.py' -v
```

Expected: new v2/principal/bulk/receipt assertions fail.

- [ ] **Step 6: Implement Metrika principal binding and v2 envelopes**

Use `_safety.principal_binding(token, domain=b"yandex-metrika-auth-principal/v2")` in:

- `ym_api.approval_envelope(..., token: str)`;
- `ym_logs.logs_approval_envelope(..., token: str)`;
- `ym_import.import_approval_envelope(..., token: str)`.

This is a signature change. Every preview and execute caller must pass the same active token; tests must never build an executable v2 envelope without the token.

- [ ] **Step 7: Implement scale policy per Metrika surface**

Use exact rules:

```text
Management generic write -> UNKNOWN, bulk=true
Logs create/clean         -> KNOWN items=1
Import upload             -> KNOWN items=1 + artifact_rows=<CSV row count>
```

The existing expense `DIRECT_DUPLICATION_RISK` / `DIRECT_SOURCE_UNVERIFIED` state remains in `risk_flags` and remains approval-bound.

- [ ] **Step 8: Add `ack_bulk` only where required and return receipts**

- `ym_api.run_request(..., ack_bulk=False)` must require ack for every generic consequential Management write because scale is unknown.
- Logs create/clean do not need bulk ack at `items=1`.
- Import upload does not need bulk ack solely because the CSV has >20 rows; row count is artifact risk context, not API operation cardinality. Existing Direct-expense risk override remains separate.
- All successful consequential paths return `yandex-ai-execution/v1` receipts with `RESPONSE_ONLY` / `UNVERIFIED` / `NOT_AVAILABLE` unless an existing response contract supplies a stronger explicitly tested state.

- [ ] **Step 9: Add CLI flags and update mock-forwarding tests**

Add `--ack-bulk` to `ym_api.py`; add it to Logs/import CLIs only if their computed operation cardinality can become bulk/unknown. Under the exact policy above, Logs/import CLIs do not need the flag yet.

- [ ] **Step 10: Run Metrika GREEN + compile**

```bash
python -m unittest discover -s plugins/yandex-metrika/tests -p 'test_*.py' -v
python -m compileall -q plugins/yandex-metrika/scripts
```

- [ ] **Step 11: Commit Task 3**

```bash
git add plugins/yandex-metrika/scripts plugins/yandex-metrika/tests
git commit -m "feat(metrika): converge writes on approval v2"
```

---

### Task 4: Webmaster parity and descriptor-derived cardinality

**Files:**
- Create: `plugins/yandex-webmaster/scripts/_safety.py`
- Modify: `plugins/yandex-webmaster/scripts/_approval.py`
- Modify: `plugins/yandex-webmaster/scripts/yw_api.py`
- Modify only if required by a failing cardinality test: `plugins/yandex-webmaster/scripts/yw_feeds.py`
- Create: `plugins/yandex-webmaster/tests/test_safety.py`
- Modify: `plugins/yandex-webmaster/tests/test_approval.py`
- Modify: `plugins/yandex-webmaster/tests/test_yw_api.py`

**Interfaces:**
- Consumes: existing URL credential redaction/HMAC behaviour in `yw_api.py`.
- Produces: OAuth principal binding in every consequential v2 envelope; cardinality derived conservatively from path/body; `--ack-bulk`; receipts.

- [ ] **Step 1: Add local kernel parity tests and copy the local implementation**

Use the same kernel contract as Direct/Metrika with Webmaster's domain `b"yandex-webmaster-auth-principal/v2"`.

- [ ] **Step 2: Write RED tests that ordinary single writes are known scale**

Cases that must be `KNOWN items=1`:

```python
(
    yw_recrawl.submit_request(1, "h", "https://example.com/a", host_url="https://example.com"),
    yw_sitemaps.add_request(1, "h", "https://example.com/sitemap.xml"),
    yw_sitemaps.delete_request(1, "h", "s1"),
    yw_sitemaps.priority_recrawl_request(1, "h", "s1"),
    yw_feeds.start_request(1, "h", host_url="https://example.com", feed_url="https://example.com/feed.yml", feed_type="YML"),
)
```

- [ ] **Step 3: Write RED tests that feed batch cardinality follows payload**

```python
descriptor = yw_feeds.batch_add_request(
    1, "h", host_url="https://example.com",
    feeds=[{"url": f"https://example.com/{i}.yml", "type": "YML"} for i in range(21)],
)
preview = yw_api.prepare_request(token="secret", **descriptor)
self.assertEqual(preview["cardinality"]["items"], 21)
self.assertTrue(preview["cardinality"]["bulk"])
```

Do the same for `feeds/batch/remove` using `body["urls"]`.

- [ ] **Step 4: Write RED tests for OAuth principal invalidation and embedded credential safety**

A preview built with `oauth-secret-a` must fail under `oauth-secret-b` even when no embedded feed credentials exist. Existing tests proving embedded basic-auth is OAuth-keyed and secret-free stay green.

- [ ] **Step 5: Run Webmaster RED suite**

```bash
python -m unittest discover -s plugins/yandex-webmaster/tests -p 'test_*.py' -v
```

- [ ] **Step 6: Implement `webmaster_cardinality(path, body)` conservatively**

In `yw_api.py`:

```python
def webmaster_cardinality(path: str, body: Any | None) -> dict[str, object]:
    normalized = path.strip("/")
    if normalized.endswith("/feeds/batch/add") and isinstance(body, dict) and isinstance(body.get("feeds"), list):
        return _safety.known_cardinality(len(body["feeds"]))
    if normalized.endswith("/feeds/batch/remove") and isinstance(body, dict) and isinstance(body.get("urls"), list):
        return _safety.known_cardinality(len(body["urls"]))
    known_single_suffixes = (
        "/recrawl/queue",
        "/user-added-sitemaps",
        "/recrawl",
        "/feeds/add/start",
        "/indexing/history/start",
    )
    if any(normalized.endswith(suffix) for suffix in known_single_suffixes) or "/user-added-sitemaps/" in normalized:
        return _safety.known_cardinality(1)
    return _safety.unknown_cardinality()
```

If an existing descriptor path differs from one of the constants, change the rule to the exact existing path proved by its descriptor test; do not alter a working Yandex endpoint merely to satisfy this classifier.

- [ ] **Step 7: Convert Webmaster envelope to v2 and add OAuth principal binding**

Keep the existing `_approval_url_credentials()` secret-safe transformation. Add a separate target field:

```python
"auth_principal_binding": _safety.principal_binding(
    token, domain=b"yandex-webmaster-auth-principal/v2"
)
```

Bind API version, path/query/body, `cardinality`, and safety metadata.

- [ ] **Step 8: Enforce exact approval then bulk ack before transport and return receipt**

Change:

```python
def run_request(..., approve: str | None = None, ack_bulk: bool = False, transport: Callable[..., Any] | None = None) -> Any:
```

For consequential operations, order is strictly:

```python
approved = require_approval(envelope, approve)
_safety.require_bulk_ack(envelope["cardinality"], ack_bulk)
# only now invoke transport/request_json
```

Return receipt with `RESPONSE_ONLY`, `UNVERIFIED`, `NOT_AVAILABLE` unless a specialized response adapter is explicitly tested.

- [ ] **Step 9: Add CLI `--ack-bulk`**

Forward it to `run_request()`.

- [ ] **Step 10: Run Webmaster GREEN + compile**

```bash
python -m unittest discover -s plugins/yandex-webmaster/tests -p 'test_*.py' -v
python -m compileall -q plugins/yandex-webmaster/scripts
```

- [ ] **Step 11: Commit Task 4**

```bash
git add plugins/yandex-webmaster/scripts plugins/yandex-webmaster/tests
git commit -m "feat(webmaster): converge writes on approval v2"
```

---

### Task 5: Repository behavioural convergence and service-ownership guard

**Files:**
- Modify: `tests/test_p0_executable_safety_contract.py`
- Modify: `docs/CONTRACT_MATRIX.json`
- Modify only if a new guard is necessary: `scripts/validate_repo.py`
- Modify only to add regression for that guard: `tests/test_validate_repo.py`

**Interfaces:**
- Consumes: all three local v2 implementations.
- Produces: repository-owned proof that high-risk safety properties cannot silently drift.

- [ ] **Step 1: Expand the root RED test from static presence to behavioural subprocess tests**

Use each plugin as its own import root instead of importing cross-plugin packages in one interpreter. Add a helper:

```python
import json
import subprocess
import sys


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

For each plugin, run a tiny source program importing its local `_safety` and assert the exact constants/cardinality/bulk-gate behaviour. This proves independent installability and avoids accidental module-name collisions from three `scripts` packages.

- [ ] **Step 2: Add root secret-leak fixture tests**

Each plugin program must generate a representative preview/receipt using a sentinel token such as `P0_SENTINEL_SECRET_6c90b2` and return serialized structures. Root test asserts the sentinel is absent.

- [ ] **Step 3: Add matrix traceability entries/selectors**

Update the existing entries rather than adding redundant near-duplicates:

```text
direct.preview-bound-write
metrika.preview-bound-write
webmaster.preview-bound-write
```

Point `test_refs` at exact new tests covering:

- v2 exact target/principal binding;
- missing/mismatched approval blocked before transport;
- bulk acknowledgement blocked before transport;
- execution receipt distinction.

Add a repository infrastructure entry `repository.p0-safety-convergence` pointing to the root behavioural test.

- [ ] **Step 4: Preserve SEO/Marketing no-transport enforcement**

Run the existing exact regression:

```bash
python -m unittest tests.test_validate_repo.ValidateRepositoryTests.test_cross_service_transport_is_rejected -v
```

Only modify validator code if this existing guard does not cover the current SEO/Marketing surfaces. Do not create a second overlapping guard if the existing one is sufficient.

- [ ] **Step 5: Run repository validator and root tests GREEN**

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 6: Commit Task 5**

```bash
git add tests/test_p0_executable_safety_contract.py docs/CONTRACT_MATRIX.json scripts/validate_repo.py tests/test_validate_repo.py
git commit -m "test: enforce P0 write safety convergence"
```

If `scripts/validate_repo.py` / `tests/test_validate_repo.py` were unchanged, omit them from `git add`.

---

### Task 6: Production docs and exact safety claims

**Files:**
- Modify: `docs/PLUGIN_STANDARD.md`, `docs/PLUGIN_STANDARD.en.md`
- Modify: `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE.en.md`
- Modify: `SECURITY.md`, `SECURITY.en.md`
- Modify: `plugins/yandex-direct/references/safety.md`
- Modify: `plugins/yandex-metrika/references/safety.md`
- Modify: `plugins/yandex-webmaster/references/safety.md`
- Modify: Direct/Metrika/Webmaster `README.md`, `README.en.md`
- Modify relevant bilingual documentation regression tests if exact release/safety markers are contractually asserted.

**Interfaces:**
- Consumes: actual implemented behaviour from Tasks 1–5.
- Produces: canonical production explanation of what is mechanically enforced vs host/operator policy.

- [ ] **Step 1: Write doc RED assertions before changing prose**

Add/extend a root documentation test so both `docs/PLUGIN_STANDARD.md` and `.en.md` contain exact machine vocabulary:

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

Also assert both languages explicitly state that the CLI does not prove conversational authorship/human later-turn provenance.

- [ ] **Step 2: Run documentation test RED**

Run the exact changed documentation test module plus bilingual checks.

- [ ] **Step 3: Update standard/architecture/security claims**

Required semantic statements:

```text
Mechanically enforced:
- exact v2 envelope binding
- credential/principal binding
- bulk/unknown-scale acknowledgement
- service-owned execution gate
- structured receipt and declared verification/rollback capability

Host/operator policy, not mechanically proven by standalone CLI:
- a human saw the preview
- a human supplied approval in a later chat turn
```

Do not say `verified` when capability/state is `RESPONSE_ONLY` + `UNVERIFIED`.

- [ ] **Step 4: Update three plugin safety references and capability matrices**

Document `--execute --approve <preview_id>` and `--ack-bulk` only where the helper can require it. Describe `BULK_THRESHOLD=20` as repository policy, not a Yandex limit.

- [ ] **Step 5: Run bilingual/docs/validator GREEN**

```bash
python -m unittest tests.test_bilingual_docs tests.test_bilingual_docs_contracts tests.test_documentation_ux_contracts -v
python scripts/validate_repo.py
```

- [ ] **Step 6: Commit Task 6**

```bash
git add docs SECURITY.md SECURITY.en.md plugins/yandex-direct/README* plugins/yandex-direct/references/safety.md plugins/yandex-metrika/README* plugins/yandex-metrika/references/safety.md plugins/yandex-webmaster/README* plugins/yandex-webmaster/references/safety.md tests
git commit -m "docs: document executable write safety v2"
```

Review the staged list before committing; do not include unrelated test changes.

---

### Task 7: Full implementation verification before version staging

**Files:** none expected unless verification exposes a defect.

**Interfaces:**
- Consumes: Tasks 1–6.
- Produces: evidence that runtime implementation is complete before SemVer/release files change.

- [ ] **Step 1: Compile all scripts**

```bash
python -m compileall -q scripts plugins
```

- [ ] **Step 2: Run all root tests**

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] **Step 3: Run all seven plugin suites using the repository-supported runner**

Run each plugin from its own directory or with the same commands used by `.github/workflows/ci.yml`. At minimum, execute Direct/Metrika/Webmaster full suites locally and rely on CI matrix for all seven before merge.

- [ ] **Step 4: Run repository validator**

```bash
python scripts/validate_repo.py
```

- [ ] **Step 5: Inspect diff scope against the P0 base**

```bash
git diff --stat d036200564f9f1d66352894b71fd6a8b25a9c51f...HEAD
git diff --name-only d036200564f9f1d66352894b71fd6a8b25a9c51f...HEAD
```

Expected runtime scope: Direct/Metrika/Webmaster safety runtime/tests, repository convergence contract, and bilingual safety docs. No Wordstat/Search runtime changes; no SEO/Marketing transport additions; no `.yandex-ai/`.

- [ ] **Step 6: Fix only observed failures with a new RED regression first**

For any defect found here: add a minimal reproducing test, run it RED, patch the smallest owning implementation, run GREEN, then rerun Steps 1–5.

- [ ] **Step 7: Commit verification fixes if any**

Use a scope-specific commit message; do not create an empty commit.

---

### Task 8: Stage Repository 1.1.0 + three plugin 2.1.0 releases only after GREEN

**Files:**
- Modify: `plugins/yandex-direct/.claude-plugin/plugin.json`
- Modify: `plugins/yandex-direct/.codex-plugin/plugin.json`
- Modify: `plugins/yandex-metrika/.claude-plugin/plugin.json`
- Modify: `plugins/yandex-metrika/.codex-plugin/plugin.json`
- Modify: `plugins/yandex-webmaster/.claude-plugin/plugin.json`
- Modify: `plugins/yandex-webmaster/.codex-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: Direct/Metrika/Webmaster `CHANGELOG.md`, `CHANGELOG.en.md`
- Modify: root `README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`
- Create: `.github/releases/1.1.0.md`
- Modify: `.github/releases/release.json`
- Create: `tests/test_repository_1_1_0_release_surfaces.py`
- Add/update plugin release-surface tests following existing version-test patterns.

**Interfaces:**
- Consumes: fully green implementation HEAD from Task 7.
- Produces: one coherent release declaration for Repository `1.1.0` and tags `yandex-direct-v2.1.0`, `yandex-metrika-v2.1.0`, `yandex-webmaster-v2.1.0`.

- [ ] **Step 1: Create intentional RED release-surface tests**

Assert exact desired versions while production metadata is still old:

```python
self.assertEqual(repository_release["version"], "1.1.0")
self.assertEqual(plugin_versions["yandex-direct-suite"], "2.1.0")
self.assertEqual(plugin_versions["yandex-metrika"], "2.1.0")
self.assertEqual(plugin_versions["yandex-webmaster"], "2.1.0")
```

Also assert Wordstat/Search/SEO/Marketing versions stay unchanged.

- [ ] **Step 2: Run release tests RED and confirm failures are only unstaged release surfaces**

Do not proceed if runtime/safety tests are failing.

- [ ] **Step 3: Bump only the three owning plugin versions**

Exact targets:

```text
yandex-direct-suite  2.1.0
yandex-metrika       2.1.0
yandex-webmaster     2.1.0
```

Update both Claude/Codex plugin manifests and marketplace entries.

- [ ] **Step 4: Add bilingual plugin changelog entries**

Release notes must describe behaviour, not just governance:

```text
approval/v2 exact target/principal/scale binding
bulk/unknown-scale --ack-bulk gate
structured execution receipts
truthful verification/rollback capability declarations
```

- [ ] **Step 5: Stage repository `1.1.0` release declaration**

Set `.github/releases/release.json` to:

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
    {"name": "yandex-direct", "version": "2.1.0", "tag": "yandex-direct-v2.1.0"},
    {"name": "yandex-metrika", "version": "2.1.0", "tag": "yandex-metrika-v2.1.0"},
    {"name": "yandex-webmaster", "version": "2.1.0", "tag": "yandex-webmaster-v2.1.0"}
  ]
}
```

Before committing, compare this shape with the validator/publisher's currently accepted plugin-entry schema and use the exact existing key names if the publisher schema differs; the semantic target above is fixed.

- [ ] **Step 6: Update root RU/EN release surfaces**

README current-release marker -> `1.1.0`; changelogs prepend `1.1.0`; describe the three plugin bumps and explicitly state the other four plugin versions are unchanged.

- [ ] **Step 7: Run release tests and full validation GREEN**

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -p 'test_*.py' -v
python -m compileall -q scripts plugins
```

- [ ] **Step 8: Commit release staging**

```bash
git add .claude-plugin .github/releases README.md README.en.md CHANGELOG.md CHANGELOG.en.md plugins/yandex-direct plugins/yandex-metrika plugins/yandex-webmaster tests
git commit -m "release: stage executable safety 1.1.0"
```

Review `git diff --cached --name-only` first; no historical release notes/tags are modified.

---

### Task 9: PR, exact-head CI, merge, exact-main CI, immutable publish

**Files:** no new implementation files expected.

**Interfaces:**
- Consumes: final staged branch.
- Produces: immutable repository/plugin releases at one exact main SHA.

- [ ] **Step 1: Open one PR for the P0 milestone**

PR body must record:

```text
base SHA
final head SHA
TDD RED commits/runs
local/root verification commands
scope statement
human-approval-boundary limitation
rollback/verification capability limitations
release versions/tags
independent-review evidence or explicit absence
```

- [ ] **Step 2: Require exact-head CI success before merge**

All CI jobs must be green on the current PR head. If the head changes, previous green CI is stale and must not authorize merge.

- [ ] **Step 3: Review PR diff and review threads**

Do not report "clean review" if there is no independent reviewer. Record `reviews=[]` / no review threads as absence of review evidence, not approval.

- [ ] **Step 4: Merge with expected-head guard**

Use squash merge with the exact verified PR head SHA.

- [ ] **Step 5: Verify exact-main CI after merge**

The successful post-merge CI run must have `head_sha == current main SHA`.

- [ ] **Step 6: Run the existing generic publisher for the current declared release**

Do not create tags/releases manually if the repository-native publisher supports the declaration.

- [ ] **Step 7: Verify immutable release set**

Required exact checks:

```text
refs/tags/1.1.0                         -> merge/main SHA
yandex-direct-v2.1.0                   -> merge/main SHA
yandex-metrika-v2.1.0                  -> merge/main SHA
yandex-webmaster-v2.1.0                -> merge/main SHA
release draft=false
release prerelease=false
release immutable=true
historical 1.0.10 and old plugin releases unchanged
```

- [ ] **Step 8: Record final evidence in the PR**

Include exact main SHA, post-merge CI run ID, publisher run ID, release IDs/tags, and the fact that Wordstat/Search/SEO/Marketing tags were not moved.

---

## Plan self-review checklist

Before execution starts, verify these mappings:

- Spec §§6–8 (v2 envelope/target/principal) -> Tasks 1, 3, 4.
- Spec §9 (bulk/unknown scale) -> Tasks 1–4 and root convergence Task 5.
- Spec §§10–14 (capability/receipt/verification) -> Tasks 1–4; no unsupported `READ_BACK` or rollback claim is introduced.
- Spec §15 (human approval boundary) -> Task 6 docs; standalone CLI does not overclaim conversational proof.
- Spec §16 (CLI compatibility) -> Tasks 2–4 preserve `--execute --approve` and add `--ack-bulk` only where needed.
- Spec §17 (fail-closed errors) -> local kernel and pre-transport tests in Tasks 1–4.
- Spec §18 (behavioural convergence) -> Task 5.
- Spec §19 (TDD order) -> Direct first, then Metrika, then Webmaster, then root convergence/docs/release.
- Spec §§20–21 (release/acceptance) -> Tasks 7–9.
- Spec §22 (P1 boundary) -> no `.yandex-ai/` or `decisions.jsonl` file in this plan.
