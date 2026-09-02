# Release Review Remediation 1.0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remediate confirmed independent-review defects in the first-release plugin set, add adversarial regression coverage for missing/unknown context, bump affected plugin versions to `1.0.1`, and merge the verified bugfix release into `main`.

**Architecture:** Preserve all first-release plugin boundaries. Service plugins continue to own Yandex transport and mutations; cross-service plugins remain pure-data orchestration. Fixes must be conservative-by-default: unknown Direct methods preview rather than execute, unknown temporal/geographic/KPI context reduces confidence/compatibility, and credentials/unsafe download URLs never leak through previews.

**Tech Stack:** Python 3.13 standard library, JSON plugin manifests, GitHub Actions.

**Spec:** `docs/REVIEW_FIRST_RELEASE.md` plus the independent Opus 5 review supplied on 2026-09-02; approved first-release specs remain authoritative where review suggestions conflict with architecture.

## Global Constraints

- No Phase 7 / backlog feature work.
- No new runtime dependency.
- Consequential service writes remain `read → analyze → preview → explicit approval → write → verify`.
- Cross-service plugins remain credential-free and transport-free.
- Official current Yandex documentation overrides donor/reviewer assumptions.
- Unknown/missing metadata must never be treated as stronger evidence than known compatible metadata.
- Every behavioral fix starts with a failing regression test.
- All seven affected plugins ship version `1.0.1` in this remediation release.

---

### Task 1: Direct safe-by-default writes and report metadata

**Files:**
- Modify: `plugins/yandex-direct/scripts/yd_api.py`
- Modify: `plugins/yandex-direct/scripts/yd_report.py`
- Modify: `plugins/yandex-direct/tests/test_yd_api.py`
- Modify: `plugins/yandex-direct/tests/test_yd_report.py`
- Modify: `plugins/yandex-direct/.codex-plugin/plugin.json`
- Modify: `plugins/yandex-direct/.claude-plugin/plugin.json`
- Modify: `plugins/yandex-direct/CHANGELOG.md`

**Interfaces:**
- Produce `is_read_method(method: str) -> bool` where only explicit read methods execute without `--execute`.
- `build_report_body(..., goals=None, attribution_models=None)` includes explicit conversion context when supplied.
- Report CLI writes metadata sidecar for file output containing date range, VAT basis, goals, attribution models, and currency provenance.

- [ ] Add tests proving `set`, unknown methods, and mixed case default to preview while known reads execute normally.
- [ ] Run Direct tests and confirm RED on current denylist logic.
- [ ] Replace write denylist with normalized read allowlist and keep `--execute` required for everything else.
- [ ] Add tests for report goals/attribution metadata and first HTTP 500 retry.
- [ ] Run Direct tests and confirm RED for missing report context/retry behavior.
- [ ] Add explicit conversion context, metadata sidecar, one retry for first HTTP 500, and remove obsolete `IncludeDiscount`.
- [ ] Run full Direct suite/compile GREEN.

### Task 2: Metrika expense/import, attribution, quality, and Logs fixes

**Files:**
- Modify: `plugins/yandex-metrika/scripts/ym_import.py`
- Modify: `plugins/yandex-metrika/scripts/ym_report.py`
- Modify: `plugins/yandex-metrika/scripts/ym_logs.py`
- Modify corresponding Metrika tests/references/skill docs.
- Bump plugin manifests/changelog to `1.0.1`.

**Interfaces:**
- Expense import detects Direct-like provider labels after separator-insensitive normalization and emits/blocks a content-based `DIRECT_DUPLICATION_RISK` unless explicitly overridden.
- Reporting preserves an explicitly supplied attribution model, but omission stays omitted/unknown and is recorded as provenance without changing the request.
- Logs date validation rejects periods beyond one calendar year; `evaluate` and `create` use the same explicit attribution context when one is supplied.

- [ ] Add negative-space tests for `Директ`, `yandex-direct`, `yandexdirect`, `ya.direct`, risky CSV rows, unsampled `data_lag`, explicit/omitted attribution provenance, Logs anniversary boundary, and evaluate/create attribution parity.
- [ ] Verify RED.
- [ ] Implement minimal fixes without claiming UTM fields are infallible Direct identifiers and without inventing an attribution model when omitted.
- [ ] Verify Metrika GREEN + compile.

### Task 3: Webmaster feed body, URL redaction, and safe downloads

**Files:**
- Modify: `plugins/yandex-webmaster/scripts/yw_feeds.py`
- Modify: `plugins/yandex-webmaster/scripts/yw_export.py`
- Modify: `plugins/yandex-webmaster/scripts/yw_indexing.py`
- Modify relevant tests/references.
- Bump plugin manifests/changelog to `1.0.1`.

**Interfaces:**
- `batch_add_request(...)["body"] == {"feeds": [...]}`.
- Preview-safe URL helper redacts embedded userinfo/password.
- Download helpers reject non-HTTPS artifact URLs before `urlopen`.

- [ ] Add tests for batch body wrapper, 1/50 boundaries, embedded credential redaction, and rejection of `file://`/`http://` download targets.
- [ ] Verify RED.
- [ ] Implement fixes.
- [ ] Verify Webmaster GREEN + compile.

### Task 4: Wordstat documented daily dynamics and secret-safe request objects

**Files:**
- Modify: `plugins/yandex-wordstat/scripts/ywstat_dynamics.py`
- Modify: `plugins/yandex-wordstat/scripts/ywstat_api.py`
- Modify tests/references.
- Bump plugin manifests/changelog to `1.0.1`.

**Interfaces:**
- `PERIOD_DAILY` is supported and permits all documented Wordstat operators.
- Weekly/monthly remain restricted to `+`.
- Request-builder return values must not expose raw Authorization headers outside an explicitly internal execution field.

- [ ] Add daily/operator and secret-redaction regression tests.
- [ ] Verify RED.
- [ ] Implement.
- [ ] Verify Wordstat GREEN + compile.

### Task 5: Search absolute ranking and request validation/readability

**Files:**
- Modify: `plugins/yandex-search/scripts/ys_request.py`
- Modify: `plugins/yandex-search/scripts/ys_parse.py`
- Modify: `plugins/yandex-search/scripts/ys_serp.py`
- Modify relevant tests.
- Bump plugin manifests/changelog to `1.0.1`.

**Interfaces:**
- Snapshots expose absolute rank `page * groups_on_page + position_on_page` for top-N/competitor metrics.
- `fix_typo_mode` validates against documented enum values.
- Touched helpers are reformatted to normal multi-line Python without semantic change beyond tested fixes.

- [ ] Add page>0 rank and invalid-fix-typo tests.
- [ ] Verify RED.
- [ ] Implement and refactor touched Search helpers after GREEN.
- [ ] Verify Search GREEN + compile.

### Task 6: SEO unknown context, top-N-safe gaps, quality propagation, and geo alignment

**Files:**
- Modify: `plugins/yandex-seo/scripts/seo_context.py`
- Modify: `plugins/yandex-seo/scripts/seo_quality.py`
- Modify: `plugins/yandex-seo/scripts/seo_opportunities.py`
- Modify: `plugins/yandex-seo/scripts/seo_bundle.py`
- Modify relevant tests/references/skills.
- Bump plugin manifests/changelog to `1.0.1`.

**Interfaces:**
- Period alignment adds `UNKNOWN`; empty/missing periods never yield `EXACT`.
- Geo alignment returns `EXACT|APPROXIMATE|MISMATCHED|UNKNOWN` and preserves distinct visitor/SERP/Wordstat contexts.
- `webmaster_impressions is None` is unknown, never measured zero.
- `WEBMASTER_TOP_N` lowers content-gap certainty.
- Metrika `data_lag` propagates independently of sampling; missing quality produces the repository-wide `QUALITY_METADATA_MISSING` limitation marker.

- [ ] Add adversarial tests for all missing-context cases.
- [ ] Verify RED.
- [ ] Implement minimal conservative semantics.
- [ ] Verify SEO GREEN + compile.

### Task 7: Marketing money/KPI compatibility and dead-path cleanup

**Files:**
- Modify: `plugins/yandex-marketing/scripts/marketing_context.py`
- Modify: `plugins/yandex-marketing/scripts/marketing_performance.py`
- Modify relevant tests/references/skills.
- Bump plugin manifests/changelog to `1.0.1`.

**Interfaces:**
- Missing material KPI fields are not considered compatible merely because both sides are `None`.
- Monetary derived metrics require explicit compatible currency and VAT basis; otherwise emit `MONEY_CONTEXT_UNKNOWN` and suppress ROAS/DRR.
- Remove or document unreachable delegated-action paths rather than retaining dead branches.

- [ ] Add tests for `None==None` incompatibility and missing monetary context.
- [ ] Verify RED.
- [ ] Implement.
- [ ] Verify Marketing GREEN + compile.

### Task 8: Marketplace consistency, versions, changelog, and release gate

**Files:**
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `scripts/validate_repo.py`
- Modify: `tests/test_validate_repo.py`
- Modify: `tests/test_marketplace_layout.py`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/REVIEW_FIRST_RELEASE.md`
- Modify: `docs/SERVICE_MATRIX.md`

**Interfaces:**
- Both marketplace manifests expose the same plugin names and `1.0.1` versions.
- The `.agents` schema uses supported authentication values only; credential-free `yandex-seo`/`yandex-marketing` use `authentication: ON_USE` rather than install-time `ON_INSTALL`, and still expose no `.env.example` or transport client.
- Root validator checks manifest-set/version consistency, supported authentication values, and the `ON_USE` requirement for cross-service plugins.

- [ ] Add root regression tests for marketplace consistency and schema-valid cross-service `ON_USE` metadata.
- [ ] Verify RED.
- [ ] Update manifests/validator/docs/version table and root `1.0.1` changelog entry.
- [ ] Run repository validator and root tests GREEN.
- [ ] Open PR to `main`, require complete path-aware GitHub Actions success for all seven plugins.
- [ ] Merge only with exact-head green CI and mergeable PR.
- [ ] Verify post-merge `main` exact HEAD and push CI success.
