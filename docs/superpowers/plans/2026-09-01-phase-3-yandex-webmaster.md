# Yandex Webmaster Phase 3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `plugins/yandex-webmaster/` version `1.0.0` as the third production plugin in the Yandex AI marketplace, with eleven specialized skills, dependency-free helpers, mixed v4/v4.1 endpoint routing, offline tests/evals and monorepo integration.

**Architecture:** The plugin is workflow-first: skills own SEO reasoning and safety while Python helpers own execution details. A shared HTTP layer handles OAuth/redaction; endpoint-aware helpers handle query analytics, indexing/archive lifecycles, recrawl quotas, sitemaps, feeds and exports. Root marketplace/CI discover Webmaster independently without changing Direct or Metrika runtime behavior.

**Tech Stack:** Agent Skills Markdown, OpenAI/Codex plugin JSON, Claude plugin JSON, Python 3.13 standard library (`urllib`, `json`, `argparse`, `datetime`, `pathlib`), `unittest`, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-01-yandex-webmaster-plugin-design.md`

## Global Constraints

- Plugin version is exactly `1.0.0`.
- Python helpers have no runtime dependency outside the standard library.
- Tests are offline and use fake transports/fixtures.
- Every skill frontmatter description starts with `Use when`.
- No runtime-specific absolute paths such as `~/.claude/`, `~/.codex/` or `~/.openclaw/`.
- Consequential writes follow `read → analyze → preview → explicit approval → write → verify`.
- `YANDEX_WEBMASTER_TOKEN` is the only bundled-helper token environment variable and previews redact it as `OAuth ***`.
- API version routing is endpoint-aware: standard resources use `/v4/`; priority Sitemap recrawl uses `/v4.1/`.
- Recrawl submission validates URL ownership and quota/queue state; `URL_ALREADY_ADDED` is non-fatal.
- Query top-N endpoints must not be represented as complete query coverage.
- Delete host/sitemap/feed operations require exact-target approval.
- Large export/download output is written to files instead of printed into agent context.
- Phase 3 is stacked on `phase-2-yandex-metrika` and must not functionally modify Direct or Metrika.

---

### Task 1: Plugin package, manifests, skills and eval discovery

**Files:**
- Create: `plugins/yandex-webmaster/.codex-plugin/plugin.json`
- Create: `plugins/yandex-webmaster/.claude-plugin/plugin.json`
- Create: `plugins/yandex-webmaster/.env.example`
- Create: `plugins/yandex-webmaster/README.md`
- Create: `plugins/yandex-webmaster/CHANGELOG.md`
- Create: `plugins/yandex-webmaster/THIRD_PARTY_NOTICES.md`
- Create: `plugins/yandex-webmaster/evals/scenarios.json`
- Create: eleven `plugins/yandex-webmaster/skills/*/SKILL.md`
- Test: `plugins/yandex-webmaster/tests/test_plugin_layout.py`

**Interfaces:**
- Produces plugin manifest with `skills: "./skills/"` and version `1.0.0`.
- Produces exactly eleven discoverable skills named by the approved spec.
- Produces eval JSON with `version: 1` and safe write modes accepted by repository validator.

- [ ] **Step 1: Write failing layout tests**

```python
EXPECTED = {
    "yandex-webmaster",
    "yandex-webmaster-audit",
    "yandex-webmaster-site-management",
    "yandex-webmaster-search-queries",
    "yandex-webmaster-indexing",
    "yandex-webmaster-recrawl",
    "yandex-webmaster-sitemaps",
    "yandex-webmaster-links",
    "yandex-webmaster-feeds",
    "yandex-webmaster-exports",
    "yandex-webmaster-api",
}
```

Assert manifest version/skills path, exact skill set, required package directories and `Use when` descriptions.

- [ ] **Step 2: Run layout test and verify RED**

Run: `cd plugins/yandex-webmaster && python -m unittest tests.test_plugin_layout -v`
Expected: FAIL because package files do not yet exist.

- [ ] **Step 3: Add minimal package and skills**

Each skill contains frontmatter, purpose, workflow, stop conditions, execution fallback and reference links. Router maps broad tasks to specialized skills.

- [ ] **Step 4: Run layout test and verify GREEN**

Run: `cd plugins/yandex-webmaster && python -m unittest tests.test_plugin_layout -v`
Expected: PASS.

---

### Task 2: Shared HTTP layer and generic Webmaster API helper

**Files:**
- Create: `plugins/yandex-webmaster/scripts/__init__.py`
- Create: `plugins/yandex-webmaster/scripts/_http.py`
- Create: `plugins/yandex-webmaster/scripts/yw_api.py`
- Test: `plugins/yandex-webmaster/tests/test_yw_api.py`

**Interfaces:**
- `_http.auth_headers(token: str) -> dict[str, str]`
- `_http.redact_headers(headers: dict[str, str]) -> dict[str, str]`
- `_http.request_json(method, url, headers, body=None, transport=None) -> object`
- `yw_api.api_url(path: str, version: str = "v4") -> str`
- `yw_api.build_request(method, path, *, token, params=None, body=None, version="v4") -> dict`
- write requests preview unless explicitly executed.

- [ ] **Step 1: Write RED tests for OAuth, redaction, URL construction and preview-before-write**

Tests assert `Authorization: OAuth token`, preview `OAuth ***`, `https://api.webmaster.yandex.net/v4/...`, and no transport invocation for a POST preview.

- [ ] **Step 2: Verify RED**

Run: `cd plugins/yandex-webmaster && python -m unittest tests.test_yw_api -v`
Expected: FAIL due to missing modules.

- [ ] **Step 3: Implement minimal helpers**

Use `urllib.request` and JSON only. Normalize non-2xx failures into a small `WebmasterAPIError` carrying status/code/message when JSON error data is available.

- [ ] **Step 4: Verify GREEN**

Run the same unittest command; expect PASS.

---

### Task 3: Endpoint version resolver, search-query and indexing helpers

**Files:**
- Create: `plugins/yandex-webmaster/scripts/yw_queries.py`
- Create: `plugins/yandex-webmaster/scripts/yw_indexing.py`
- Test: `plugins/yandex-webmaster/tests/test_yw_queries.py`
- Test: `plugins/yandex-webmaster/tests/test_yw_indexing.py`

**Interfaces:**
- `yw_queries.popular_request(user_id, host_id, *, order_by=None, offset=0, limit=500) -> dict`
- `yw_queries.history_request(user_id, host_id, *, date_from, date_to, query_ids=None) -> dict`
- `yw_queries.analytics_request(user_id, host_id, payload: dict) -> dict`
- `yw_queries.coverage_note(kind: str, returned: int, limit: int | None) -> str`
- `yw_indexing.in_search_request(...) -> dict`
- `yw_indexing.search_events_request(...) -> dict`
- `yw_indexing.indexing_history_request(...) -> dict`
- `yw_indexing.archive_start_request(...) -> dict`
- `yw_indexing.archive_status_request(...) -> dict`
- `yw_indexing.archive_download_url(response: dict) -> str | None`

- [ ] **Step 1: Write RED tests**

Tests verify popular query default limit <= 500, coverage note says top-N rather than complete coverage, analytics uses POST body, archive lifecycle exposes `task_id`/status/download URL without writing files yet.

- [ ] **Step 2: Verify RED**

Run query and indexing test modules; expect missing implementation failures.

- [ ] **Step 3: Implement request builders and archive response parsing**

No live network in these helpers unless a CLI execution path calls shared transport.

- [ ] **Step 4: Verify GREEN**

Run both modules; expect PASS.

---

### Task 4: Recrawl and Sitemap safety/lifecycle

**Files:**
- Create: `plugins/yandex-webmaster/scripts/yw_recrawl.py`
- Create: `plugins/yandex-webmaster/scripts/yw_sitemaps.py`
- Test: `plugins/yandex-webmaster/tests/test_yw_recrawl.py`
- Test: `plugins/yandex-webmaster/tests/test_yw_sitemaps.py`

**Interfaces:**
- `yw_recrawl.validate_url_for_host(url: str, host_url: str) -> None`
- `yw_recrawl.quota_request(user_id, host_id) -> dict`
- `yw_recrawl.queue_request(user_id, host_id) -> dict`
- `yw_recrawl.submit_request(user_id, host_id, url, *, host_url) -> dict`
- `yw_recrawl.normalize_submit_error(status: int, code: str | None) -> dict | None`
- `yw_sitemaps.endpoint_version(operation: str) -> str`
- `yw_sitemaps.list_request(...) -> dict`
- `yw_sitemaps.add_request(...) -> dict`
- `yw_sitemaps.delete_request(...) -> dict`
- `yw_sitemaps.priority_recrawl_request(...) -> dict`

- [ ] **Step 1: Write RED tests**

Cover same-host URL acceptance, cross-host rejection, quota request path, `409/URL_ALREADY_ADDED` normalization, sitemap add/delete preview shape and `priority_recrawl -> v4.1` while normal sitemap endpoints remain `v4`.

- [ ] **Step 2: Verify RED**

Run both test modules; expect FAIL.

- [ ] **Step 3: Implement minimal quota/version/safety logic**

Use `urllib.parse.urlsplit`; compare normalized hostname and scheme/port where relevant. Never allow arbitrary version override for priority recrawl.

- [ ] **Step 4: Verify GREEN**

Run both modules; expect PASS.

---

### Task 5: Feeds and export lifecycle helpers

**Files:**
- Create: `plugins/yandex-webmaster/scripts/yw_feeds.py`
- Create: `plugins/yandex-webmaster/scripts/yw_export.py`
- Test: `plugins/yandex-webmaster/tests/test_yw_feeds.py`
- Test: `plugins/yandex-webmaster/tests/test_yw_export.py`

**Interfaces:**
- `yw_feeds.validate_host_https(host_url: str) -> None`
- `yw_feeds.list_request(...) -> dict`
- `yw_feeds.start_request(...) -> dict`
- `yw_feeds.status_request(...) -> dict`
- `yw_feeds.delete_request(...) -> dict`
- `yw_export.start_request(...) -> dict`
- `yw_export.status_request(...) -> dict`
- `yw_export.download_to_file(url: str, output: Path, *, transport=None) -> Path`

- [ ] **Step 1: Write RED tests**

Cover HTTP host rejection for feed mutation, preview shapes for feed start/delete, async export task status, and writing binary/text payload to a requested file path without stdout dumping.

- [ ] **Step 2: Verify RED**

Run both modules; expect FAIL.

- [ ] **Step 3: Implement helpers**

Keep file download transport injectable; create parent directories explicitly and return the final path.

- [ ] **Step 4: Verify GREEN**

Run both modules; expect PASS.

---

### Task 6: Current references and agent workflows

**Files:**
- Create all `plugins/yandex-webmaster/references/*.md` files listed by spec.
- Expand all eleven skills from Task 1 to production workflow content.

**Interfaces:**
- References document API facts verified on `2026-09-01`, endpoint version map, OAuth permissions, query top-N limits, recrawl semantics, priority sitemap recrawl, feeds, exports and safety.
- Skills link only to relative plugin references and bundled helper names; no runtime-specific absolute paths.

- [ ] **Step 1: Add/extend tests that scan workflow requirements**

Layout test asserts key phrases/relative references exist in router, recrawl, sitemap, export and site-management skills.

- [ ] **Step 2: Verify RED where production content is missing**

Run layout test.

- [ ] **Step 3: Write references and complete workflow skills**

Donor acknowledgement goes in `THIRD_PARTY_NOTICES.md`; official docs remain source of truth.

- [ ] **Step 4: Verify GREEN**

Run plugin layout tests and `python ../.. /scripts/validate_repo.py` from repository root using the actual relative command `python scripts/validate_repo.py`.

---

### Task 7: Marketplace, docs and path-aware CI integration

**Files:**
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md`
- Modify: `docs/SERVICE_MATRIX.md`
- Modify: `docs/ROADMAP.md`
- Modify: `tests/test_marketplace_layout.py`

**Interfaces:**
- Marketplace adds local plugin path `./plugins/yandex-webmaster` version `1.0.0`.
- CI `changes` job exposes `webmaster`; Webmaster job runs plugin tests and compiles all eight helpers.

- [ ] **Step 1: Add RED root tests**

Assert Webmaster marketplace entry, service-matrix availability and CI job/output exist.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL until root integration is added.

- [ ] **Step 3: Integrate root metadata/docs/CI**

Keep Direct and Metrika jobs intact. Add Webmaster detection for `plugins/yandex-webmaster/` plus shared-contract paths.

- [ ] **Step 4: Verify GREEN**

Run root tests and repository validator.

---

### Task 8: Full regression and remote diff gate

**Files:** none unless failures reveal a Phase 3 defect.

- [ ] **Step 1: Run root suite**

`python -m unittest discover -s tests -v`

- [ ] **Step 2: Run Direct regression in its plugin directory**

`cd plugins/yandex-direct && python -m unittest discover -s tests -v`

- [ ] **Step 3: Run Metrika regression in its plugin directory**

`cd plugins/yandex-metrika && python -m unittest discover -s tests -v`

- [ ] **Step 4: Run Webmaster regression**

`cd plugins/yandex-webmaster && python -m unittest discover -s tests -v`

- [ ] **Step 5: Compile helpers**

`python -m py_compile scripts/_http.py scripts/yw_api.py scripts/yw_queries.py scripts/yw_indexing.py scripts/yw_recrawl.py scripts/yw_sitemaps.py scripts/yw_feeds.py scripts/yw_export.py`

- [ ] **Step 6: Validate JSON and repository contract**

Parse all plugin manifests/evals and run `python scripts/validate_repo.py` from repository root.

- [ ] **Step 7: Compare Phase 2 → Phase 3**

Remote diff must contain no files under `plugins/yandex-direct/` or `plugins/yandex-metrika/`.

- [ ] **Step 8: Open stacked PR #3**

Base: `phase-2-yandex-metrika`. Head: `phase-3-yandex-webmaster`. Include exact verification counts and note that it should be retargeted after preceding PRs merge.
