# Yandex Metrika Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `plugins/yandex-metrika/` version `1.0.0` as the second production plugin in the Yandex AI marketplace, with ten specialized skills, dependency-free API/report/log/import helpers, offline tests/evals, current references and monorepo integration.

**Architecture:** The plugin is workflow-first: skills encode analysis/safety behavior while local Python helpers provide backend-independent execution when available. Reporting, Logs and imports remain separate adapters with shared HTTP primitives; root marketplace/CI stay generic and discover both Direct and Metrika independently.

**Tech Stack:** Agent Skills Markdown, OpenAI/Codex plugin JSON, Claude plugin JSON, Python 3.13 standard library (`urllib`, `json`, `csv`, `argparse`, `datetime`), `unittest`, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-01-yandex-metrika-plugin-design.md`

## Global Constraints

- Plugin version is exactly `1.0.0` for Phase 2.
- No runtime dependency outside the Python standard library.
- Tests never contact Yandex services and never require real OAuth tokens.
- Every skill frontmatter description starts with `Use when`.
- No runtime-specific absolute paths such as `~/.claude/`, `~/.codex/` or `~/.openclaw/`.
- Consequential writes follow `read → analyze → preview → explicit approval → write → verify`.
- OAuth secrets are read only from environment/app credentials and are redacted from preview output.
- Current attribution models are `cross_device_first`, `last`, `cross_device_last_significant`, `automatic`.
- Reporting exposes sampling/data-quality metadata instead of silently presenting sampled values as exact.
- Logs request periods are limited to at most one year.
- Expense import rejects a source explicitly identified as Yandex Direct to prevent cost duplication.
- CRM/visitor-parameter imports are documented in skills/references, but executable Phase 2 CSV upload support is intentionally limited to offline conversions, calls and expenses.
- Phase 2 branch is stacked on `phase-1-marketplace-foundation` until PR #1 lands.

---

### Task 1: Metrika plugin package and discovery contract

**Files:**
- Create: `plugins/yandex-metrika/tests/test_plugin_layout.py`
- Create: `plugins/yandex-metrika/.codex-plugin/plugin.json`
- Create: `plugins/yandex-metrika/.claude-plugin/plugin.json`
- Create: `plugins/yandex-metrika/.env.example`
- Create: `plugins/yandex-metrika/evals/scenarios.json`
- Create: ten `plugins/yandex-metrika/skills/*/SKILL.md`
- Create: `plugins/yandex-metrika/README.md`
- Create: `plugins/yandex-metrika/CHANGELOG.md`
- Create: `plugins/yandex-metrika/THIRD_PARTY_NOTICES.md`

**Interfaces:**
- Consumes: root `docs/PLUGIN_STANDARD.md` and repository validator.
- Produces: plugin manifest name `yandex-metrika`, version `1.0.0`, skills path `./skills/`, and exactly ten discoverable skill names from the approved spec.

- [ ] **Step 1: Write the failing layout test**

Create `test_plugin_layout.py` with tests that assert:

```python
EXPECTED_SKILLS = {
    "yandex-metrika",
    "yandex-metrika-audit",
    "yandex-metrika-reporting",
    "yandex-metrika-conversions",
    "yandex-metrika-ecommerce",
    "yandex-metrika-attribution",
    "yandex-metrika-goals",
    "yandex-metrika-logs",
    "yandex-metrika-imports",
    "yandex-metrika-api",
}
```

The tests must require manifest version `1.0.0`, `skills == "./skills/"`, `.env.example` containing `YANDEX_METRIKA_TOKEN=`, an eval file with one or more scenarios, all ten `SKILL.md` files, and the three top-level docs.

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
python -m unittest plugins/yandex-metrika/tests/test_plugin_layout.py -v
```

Expected: FAIL because the plugin package does not exist.

- [ ] **Step 3: Add minimal manifests, skill files, evals and package docs**

Manifest contract:

```json
{
  "name": "yandex-metrika",
  "version": "1.0.0",
  "skills": "./skills/"
}
```

The actual manifest also includes description/license/keywords/interface metadata consistent with Direct. Each skill contains valid frontmatter and its approved responsibility; router mentions all nine specialized skills. Eval scenarios use only `false`, `preview-first`, or `approval-required` for `write`.

- [ ] **Step 4: Run the layout test and repository validator**

```bash
python -m unittest plugins/yandex-metrika/tests/test_plugin_layout.py -v
python scripts/validate_repo.py
```

Expected: the plugin layout test passes; repository validation will still fail until the root marketplace lists Metrika in Task 6, so record that expected marketplace-discovery failure rather than weakening validation.

- [ ] **Step 5: Commit**

```bash
git add plugins/yandex-metrika
 git commit -m "feat(metrika): add plugin package and skills"
```

---

### Task 2: Shared HTTP primitives and Management API helper

**Files:**
- Create: `plugins/yandex-metrika/scripts/__init__.py`
- Create: `plugins/yandex-metrika/scripts/_http.py`
- Create: `plugins/yandex-metrika/scripts/ym_api.py`
- Create: `plugins/yandex-metrika/tests/test_ym_api.py`

**Interfaces:**
- Produces `_http.oauth_headers(token) -> dict[str, str]`, `_http.redact_headers(headers) -> dict[str, str]`, `_http.request_json(...) -> tuple[int, dict | list | str]`.
- Produces `ym_api.build_management_url(path, query=None) -> str`, `ym_api.is_consequential(method) -> bool`, and `ym_api.prepare_request(...) -> dict` for dry-run previews.

- [ ] **Step 1: Write failing tests**

Tests require:

```python
self.assertEqual(oauth_headers("secret")["Authorization"], "OAuth secret")
self.assertEqual(redact_headers({"Authorization": "OAuth secret"})["Authorization"], "OAuth ***")
self.assertEqual(
    build_management_url("counters", {"per_page": 10}),
    "https://api-metrika.yandex.net/management/v1/counters?per_page=10",
)
self.assertFalse(is_consequential("GET"))
self.assertTrue(is_consequential("POST"))
self.assertTrue(is_consequential("PUT"))
self.assertTrue(is_consequential("DELETE"))
```

A write preview must contain redacted headers and must not invoke a network transport.

- [ ] **Step 2: Verify RED**

```bash
python -m unittest plugins/yandex-metrika/tests/test_ym_api.py -v
```

Expected: import/function failures because helpers do not exist.

- [ ] **Step 3: Implement standard-library HTTP and API helper**

`_http.py` uses `urllib.request.Request`/`urlopen`, JSON encoding and `urllib.error.HTTPError`; errors include HTTP status plus a bounded response body. `ym_api.py` defaults POST/PUT/DELETE to preview unless `--execute` is provided, while GET executes normally. CLI token comes from `YANDEX_METRIKA_TOKEN` unless a test injects a token directly.

- [ ] **Step 4: Verify GREEN and compile**

```bash
python -m unittest plugins/yandex-metrika/tests/test_ym_api.py -v
python -m py_compile plugins/yandex-metrika/scripts/_http.py plugins/yandex-metrika/scripts/ym_api.py
```

Expected: PASS and exit 0.

- [ ] **Step 5: Commit**

```bash
git add plugins/yandex-metrika/scripts plugins/yandex-metrika/tests/test_ym_api.py
 git commit -m "feat(metrika): add safe Management API helper"
```

---

### Task 3: Reporting API helper and attribution/data-quality contract

**Files:**
- Create: `plugins/yandex-metrika/scripts/ym_report.py`
- Create: `plugins/yandex-metrika/tests/test_ym_report.py`
- Create: `plugins/yandex-metrika/references/reporting.md`
- Create: `plugins/yandex-metrika/references/attribution.md`

**Interfaces:**
- Produces `REPORT_PATHS` for `table`, `bytime`, `comparison`, `drilldown`, `comparison-drilldown`.
- Produces `CURRENT_ATTRIBUTION_MODELS` set.
- Produces `build_report_url(mode, params) -> str`.
- Produces `extract_quality_metadata(payload) -> dict[str, object]` returning only known quality fields when present.

- [ ] **Step 1: Write failing reporting tests**

Tests require exact endpoint suffixes and current attribution values:

```python
CURRENT_ATTRIBUTION_MODELS == {
    "cross_device_first",
    "last",
    "cross_device_last_significant",
    "automatic",
}
```

Quality extraction from a fixture must preserve:

```python
{
    "sampled": True,
    "sample_share": 0.25,
    "sample_size": 250,
    "sample_space": 1000,
    "data_lag": 90,
    "contains_sensitive_data": True,
    "total_rows_rounded": True,
}
```

Unknown attribution values raise `ValueError` before network access.

- [ ] **Step 2: Verify RED**

```bash
python -m unittest plugins/yandex-metrika/tests/test_ym_report.py -v
```

- [ ] **Step 3: Implement report builder/parser and references**

The helper sends OAuth-authenticated GET requests only. Parameters with list values are serialized as comma-separated values where the Reporting API expects CSV-style lists. It never interprets the values as statistically exact; CLI output includes a `quality` object next to returned data.

- [ ] **Step 4: Verify GREEN**

```bash
python -m unittest plugins/yandex-metrika/tests/test_ym_report.py -v
python -m py_compile plugins/yandex-metrika/scripts/ym_report.py
```

- [ ] **Step 5: Commit**

```bash
git add plugins/yandex-metrika/scripts/ym_report.py plugins/yandex-metrika/tests/test_ym_report.py plugins/yandex-metrika/references/reporting.md plugins/yandex-metrika/references/attribution.md
 git commit -m "feat(metrika): add quality-aware Reporting API helper"
```

---

### Task 4: Logs lifecycle helper

**Files:**
- Create: `plugins/yandex-metrika/scripts/ym_logs.py`
- Create: `plugins/yandex-metrika/tests/test_ym_logs.py`
- Create: `plugins/yandex-metrika/references/logs.md`

**Interfaces:**
- Produces `validate_period(date1, date2) -> tuple[date, date]` rejecting inverted ranges and ranges longer than 1 year.
- Produces `logs_endpoint(counter_id, action, request_id=None, part_number=None) -> str` for `evaluate`, `create`, `status`, `download`, `clean`.
- `create` and `clean` are preview-only unless `--execute`; evaluate/status/download are reads.

- [ ] **Step 1: Write failing lifecycle tests**

Tests cover:

```text
evaluate -> /logrequests/evaluate
create   -> /logrequests
status   -> /logrequest/{requestId}
download -> /logrequest/{requestId}/part/{partNumber}/download
clean    -> /logrequest/{requestId}/clean
```

A 366+ day period raises `ValueError`; a valid one-year-or-shorter period passes. Clean preview redacts OAuth.

- [ ] **Step 2: Verify RED**

```bash
python -m unittest plugins/yandex-metrika/tests/test_ym_logs.py -v
```

- [ ] **Step 3: Implement lifecycle helper and reference**

Create requests use form/query parameters required by Logs API and preserve the server-provided `request_id`. Download returns bytes to an explicitly supplied output path rather than printing raw log contents to stdout.

- [ ] **Step 4: Verify GREEN**

```bash
python -m unittest plugins/yandex-metrika/tests/test_ym_logs.py -v
python -m py_compile plugins/yandex-metrika/scripts/ym_logs.py
```

- [ ] **Step 5: Commit**

```bash
git add plugins/yandex-metrika/scripts/ym_logs.py plugins/yandex-metrika/tests/test_ym_logs.py plugins/yandex-metrika/references/logs.md
 git commit -m "feat(metrika): add Logs API lifecycle helper"
```

---

### Task 5: Data import validation and preview helper

**Files:**
- Create: `plugins/yandex-metrika/scripts/ym_import.py`
- Create: `plugins/yandex-metrika/tests/test_ym_import.py`
- Create: `plugins/yandex-metrika/references/imports.md`

**Interfaces:**
- Produces `IMPORT_PATHS` for `offline-conversions`, `calls`, `expenses`.
- Produces `inspect_csv(path) -> dict` with `rows`, `columns`, `size_bytes`, `encoding`.
- Produces `guard_expense_source(source) -> None` rejecting normalized values identifying Yandex Direct.
- Produces `prepare_import(kind, counter_id, file_path, token, **query) -> dict` with redacted preview.

- [ ] **Step 1: Write failing import tests**

Tests create temporary UTF-8 CSV files and require row/column inspection. They assert these values are rejected by the expense guard (case/spacing normalized): `Yandex Direct`, `Яндекс Директ`, `direct` when explicitly used as the source argument. Unknown import kind, missing file and non-UTF-8 CSV raise clear errors.

- [ ] **Step 2: Verify RED**

```bash
python -m unittest plugins/yandex-metrika/tests/test_ym_import.py -v
```

- [ ] **Step 3: Implement import preview/execution**

Upload endpoints:

```text
offline-conversions -> /management/v1/counter/{id}/offline_conversions/upload
calls               -> /management/v1/counter/{id}/offline_conversions/upload_calls
expenses            -> /management/v1/counter/{id}/expense/upload
```

If the current official expense multipart endpoint resolves to a different exact path during implementation, use the documented path and encode it in a regression test before completing the task. Multipart upload is implemented with the standard library; preview includes file metadata, URL/query and redacted headers but not full file contents.

- [ ] **Step 4: Verify GREEN**

```bash
python -m unittest plugins/yandex-metrika/tests/test_ym_import.py -v
python -m py_compile plugins/yandex-metrika/scripts/ym_import.py
```

- [ ] **Step 5: Commit**

```bash
git add plugins/yandex-metrika/scripts/ym_import.py plugins/yandex-metrika/tests/test_ym_import.py plugins/yandex-metrika/references/imports.md
 git commit -m "feat(metrika): add safe data import helper"
```

---

### Task 6: References, root marketplace, CI and service status

**Files:**
- Create: `plugins/yandex-metrika/references/api-2026.md`
- Create: `plugins/yandex-metrika/references/audit-framework.md`
- Create: `plugins/yandex-metrika/references/safety.md`
- Create: `plugins/yandex-metrika/references/sources.md`
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/SERVICE_MATRIX.md`
- Modify: `docs/ROADMAP.md`
- Modify: `README.md`
- Modify: `tests/test_marketplace_layout.py`

**Interfaces:**
- Marketplace gains independent `yandex-metrika` entry pointing to `./plugins/yandex-metrika`.
- CI `changes` job exposes both `direct` and `metrika` outputs and a new Metrika job runs its tests plus compile checks.
- Root service matrix marks Metrika `available`/`stable` at version `1.0.0` only after full verification.

- [ ] **Step 1: Extend root tests first**

Add failing root assertions that marketplace plugin paths equal:

```python
{
    "./plugins/yandex-direct",
    "./plugins/yandex-metrika",
}
```

and that CI contains both `plugins/yandex-direct` and `plugins/yandex-metrika` jobs/paths.

- [ ] **Step 2: Verify RED**

```bash
python -m unittest discover -s tests -v
python scripts/validate_repo.py
```

Expected: failure because Metrika is not yet listed at root.

- [ ] **Step 3: Add current references and root integration**

`api-2026.md` records verification date `2026-09-01`, OAuth model, API families and canonical URLs. `sources.md` attributes the two MIT donors and makes official docs authoritative. CI compiles `_http.py`, `ym_api.py`, `ym_report.py`, `ym_logs.py`, `ym_import.py` after Metrika tests.

- [ ] **Step 4: Run the complete verification set**

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/yandex-direct/tests -v
python -m unittest discover -s plugins/yandex-metrika/tests -v
python scripts/validate_repo.py
python -m py_compile \
  plugins/yandex-direct/scripts/yd_api.py \
  plugins/yandex-direct/scripts/yd_report.py \
  plugins/yandex-metrika/scripts/_http.py \
  plugins/yandex-metrika/scripts/ym_api.py \
  plugins/yandex-metrika/scripts/ym_report.py \
  plugins/yandex-metrika/scripts/ym_logs.py \
  plugins/yandex-metrika/scripts/ym_import.py
```

Also parse every `*.json` under `.agents`, `.claude-plugin`, `plugins/yandex-direct`, and `plugins/yandex-metrika` with `json.load`.

Expected: all commands exit 0.

- [ ] **Step 5: Commit**

```bash
git add .agents .claude-plugin .github README.md docs tests plugins/yandex-metrika/references
 git commit -m "feat(metrika): integrate plugin into Yandex AI marketplace"
```

---

### Task 7: Final diff review and stacked PR

**Files:** No production files unless verification discovers a defect.

**Interfaces:** Phase 2 PR targets `phase-1-marketplace-foundation` while PR #1 is open; after PR #1 merges, retarget Phase 2 to `main`.

- [ ] **Step 1: Re-run full verification from Task 6**

No completion claim is allowed from an earlier test run.

- [ ] **Step 2: Inspect the branch diff**

Confirm no Direct functional code changed and no secrets/cache/generated analytics data are included.

- [ ] **Step 3: Create stacked PR**

Title:

```text
feat: add Yandex Metrika 1.0.0 plugin
```

Body must summarize the ten skills, four execution helpers, safety behavior, current API verification, donor attribution and test counts. Base branch: `phase-1-marketplace-foundation`.
