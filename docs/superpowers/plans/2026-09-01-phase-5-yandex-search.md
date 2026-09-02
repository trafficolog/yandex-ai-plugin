# Yandex Search 1.0.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship Yandex Search 1.0.0 as a standalone SEO-first plugin with classic Web Search retrieval, resumable deferred batches, reproducible SERP snapshots, ranking/competitor analysis and real URL-overlap clustering.

**Architecture:** Keep API transport/request building separate from parsing and SERP analytics. XML is canonical for structured SEO workflows; deferred operations are explicit resumable state, and clustering operates only on normalized FLAT SERP snapshots with a caller-supplied threshold.

**Tech Stack:** Python 3.13 standard library, JSON manifests, Markdown skills/references, `unittest`, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-01-yandex-search-plugin-design.md`

## Global Constraints

- Plugin version is `1.0.0` and installation boundary is `plugins/yandex-search/`.
- No third-party Python dependencies.
- Official Yandex documentation is source of truth; API baseline date is 2026-09-01.
- Classic Web Search only in 1.0.0; no image/generative/infocontext implementation.
- XML is canonical structured format; HTML is raw artifact only.
- Ranking/clustering requires `GROUP_MODE_FLAT` and `docsInGroup=1`.
- Clustering requires explicit `min_shared_urls`; no universal hidden threshold.
- Never label SERP presence as market share.
- Cost estimates are dated planning metadata, not billing guarantees.
- Direct, Metrika, Webmaster and Wordstat runtime trees are unchanged.

---

### Task 1: Package contract

**Files:** create manifests, docs, evals and ten `skills/*/SKILL.md`; test `plugins/yandex-search/tests/test_plugin_layout.py`.

**Produces:** discoverable `yandex-search` 1.0.0 package with exact skill set and env variables `YANDEX_SEARCH_API_KEY`, `YANDEX_SEARCH_IAM_TOKEN`, `YANDEX_SEARCH_FOLDER_ID`.

- [ ] Write a layout test asserting manifest/version/skills/docs/evals.
- [ ] Run it and confirm RED because the package is absent.
- [ ] Add the minimal package and skill frontmatter.
- [ ] Run the layout test and confirm GREEN.

### Task 2: Auth, limits, request model and cost planning

**Files:** create `scripts/_http.py`, `scripts/ys_api.py`, `scripts/ys_request.py`; test `test_ys_api.py`, `test_ys_request.py`.

**Produces:** `auth_headers()`, `validate_query_text()`, `estimate_cost()`, `recommend_mode()`, `build_search_request()`, `config_fingerprint()`.

- [ ] Tests cover mutually exclusive API key/IAM token, redaction, 400-char/40-word limits, current quotas/prices and mode recommendation.
- [ ] Confirm RED.
- [ ] Implement standard-library helpers and sync/async endpoints.
- [ ] Confirm GREEN.

### Task 3: XML parser and SERP snapshots

**Files:** create `scripts/ys_parse.py`, `scripts/ys_serp.py`; test `test_ys_parse.py`, `test_ys_serp.py`.

**Produces:** `decode_raw_data()`, `parse_xml_results()`, `normalize_url()`, `build_snapshot()`.

- [ ] Tests cover Base64 XML, missing optional fields, rank ordering, default-port/fragment/query sorting and stable config fingerprint.
- [ ] Confirm RED.
- [ ] Implement tolerant ElementTree parser and snapshot builder.
- [ ] Confirm GREEN.

### Task 4: Deferred lifecycle and batch planning

**Files:** create `scripts/ys_async.py`, `scripts/ys_batch.py`; test `test_ys_async.py`, `test_ys_batch.py`.

**Produces:** operation manifest normalization, submit/status/collect request builders, retention-age metadata, batch cost preview and explicit sync/deferred recommendation.

- [ ] Tests enforce no endless polling primitive and preserve operation IDs/timestamps.
- [ ] Confirm RED.
- [ ] Implement explicit lifecycle helpers.
- [ ] Confirm GREEN.

### Task 5: SERP overlap clustering

**Files:** create `scripts/ys_overlap.py`; test `test_ys_overlap.py`.

**Produces:** `pairwise_overlap()`, `cluster_queries()` with explicit `top_k` and required `min_shared_urls`, Jaccard and bridge-risk diagnostics.

- [ ] Tests cover identical/disjoint/partial SERPs and A↔B↔C bridge chaining.
- [ ] Confirm RED.
- [ ] Implement deterministic connected components plus weakest-pair/bridge-risk reporting.
- [ ] Confirm GREEN.

### Task 6: Ranking and competitor analytics

**Files:** create `scripts/ys_compare.py`; test `test_ys_compare.py`.

**Produces:** `compare_rankings()` and `competitor_presence()`.

- [ ] Tests reject incompatible fingerprints and calculate rank delta, query presence, top-3/top-10 presence and median rank when present.
- [ ] Confirm RED.
- [ ] Implement analytics without “market share” terminology.
- [ ] Confirm GREEN.

### Task 7: Production skills and references

**Files:** replace minimal skill bodies; create references `api-2026.md`, `auth.md`, `request-model.md`, `serp.md`, `async.md`, `clustering.md`, `rankings.md`, `operators.md`, `quota-pricing.md`, `safety.md`, `sources.md`; extend layout tests.

**Produces:** actionable workflows with current API constraints, cost preview, FLAT clustering requirements, Wordstat region-resolution contract and donor attribution.

- [ ] Add failing production-contract assertions.
- [ ] Confirm RED.
- [ ] Write production skills/references.
- [ ] Confirm GREEN.

### Task 8: Monorepo integration and full verification

**Files:** modify `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json`, `.github/workflows/ci.yml`, `README.md`, `docs/SERVICE_MATRIX.md`, `docs/ROADMAP.md`, `tests/test_marketplace_layout.py`.

**Produces:** fifth marketplace plugin and independent Search CI job.

- [ ] Add failing root assertions for Search marketplace/CI/service matrix/roadmap.
- [ ] Confirm RED.
- [ ] Integrate Search and mark Phase 5 implemented / Phase 6 cross-service next.
- [ ] Run root + all five plugin suites, validator, compile and JSON parse checks.
- [ ] Verify previous four plugin directory hashes match Phase 4 baseline.
