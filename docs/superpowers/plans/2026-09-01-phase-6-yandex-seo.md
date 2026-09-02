# Yandex SEO Cross-Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `yandex-seo` 1.0.0 as a read-only cross-service plugin that combines Wordstat, Search, Webmaster, and Metrika evidence into reproducible SEO findings and delegated action previews.

**Architecture:** The plugin consumes structured JSON/artifacts produced by existing service plugins, normalizes them into a versioned SEO Evidence Bundle, aligns time/geography/quality context, and derives transparent findings. It contains no Yandex HTTP clients and performs no live writes; consequential actions are delegated back to the owning service plugin as previews.

**Tech Stack:** Python 3.13 standard library only, JSON fixtures, repository plugin manifests/skills/evals, unittest, existing repository validator and GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-01-yandex-seo-plugin-design.md`

## Global Constraints

- Target plugin version is `1.0.0`.
- No direct Yandex API calls, credentials, OAuth, HTTP clients, or duplicated volatile endpoint knowledge.
- `scripts/` must be pure data transformation/analysis code using Python standard library only.
- Read/analyze/recommend/preview only; no live writes.
- Preserve source provenance and classify evidence as `OBSERVED`, `DERIVED`, or `HYPOTHESIS`.
- Wordstat demand and Webmaster demand remain distinct metrics.
- Temporal alignment must be `EXACT`, `APPROXIMATE`, or `MISMATCHED`; `MISMATCHED` blocks cross-source causal/trend claims.
- Default query normalization is Unicode normalization + trim + case fold + whitespace collapse only.
- Default URL normalization is conservative and must not remove query parameters.
- Inherit source quality limitations such as Metrika sampling, Webmaster top-N coverage, and Search clustering `bridge_risk`.
- No opaque universal SEO score or universal CTR/conversion benchmark.
- Delegated actions identify owning plugin/skill/target and `requires_approval`, but do not execute.

---

### Task 1: Plugin package and discovery contract

**Files:**
- Create: `plugins/yandex-seo/.codex-plugin/plugin.json`
- Create: `plugins/yandex-seo/.claude-plugin/plugin.json`
- Create: `plugins/yandex-seo/README.md`
- Create: `plugins/yandex-seo/CHANGELOG.md`
- Create: `plugins/yandex-seo/THIRD_PARTY_NOTICES.md`
- Create: `plugins/yandex-seo/evals/scenarios.json`
- Create: `plugins/yandex-seo/skills/*/SKILL.md`
- Test: `plugins/yandex-seo/tests/test_plugin_layout.py`

**Interfaces:**
- Produces ten discoverable skills: `yandex-seo`, `yandex-seo-audit`, `yandex-seo-opportunities`, `yandex-seo-clusters`, `yandex-seo-content-gaps`, `yandex-seo-cannibalization`, `yandex-seo-ctr`, `yandex-seo-conversions`, `yandex-seo-technical`, `yandex-seo-prioritize`.

- [ ] Write layout tests asserting manifests, version `1.0.0`, all ten skills, evals, references/scripts/tests directories, and explicit absence of credential/env requirements.
- [ ] Run `python -m unittest tests.test_plugin_layout -v` from `plugins/yandex-seo`; expect failure because package files do not exist.
- [ ] Add the minimal package/manifests/skill stubs/evals structure needed for discovery.
- [ ] Re-run the layout test; expect pass.
- [ ] Commit as `feat: scaffold Yandex SEO cross-service plugin`.

### Task 2: Context, normalization, and Evidence Bundle

**Files:**
- Create: `plugins/yandex-seo/scripts/seo_context.py`
- Create: `plugins/yandex-seo/scripts/seo_bundle.py`
- Test: `plugins/yandex-seo/tests/test_seo_context.py`
- Test: `plugins/yandex-seo/tests/test_seo_bundle.py`

**Interfaces:**
- Produces `normalize_query(text: str) -> str`.
- Produces `normalize_url(url: str) -> str`.
- Produces `classify_period_alignment(items: list[dict]) -> str` returning `EXACT|APPROXIMATE|MISMATCHED`.
- Produces `new_bundle(context: dict, coverage: dict) -> dict` and `add_evidence(bundle: dict, evidence: dict) -> dict`.

- [ ] Write failing tests for Unicode/case/whitespace query normalization, conservative URL normalization, period alignment, bundle version/coverage, evidence provenance, and distinct Wordstat/Webmaster demand fields.
- [ ] Run the two test modules and verify RED.
- [ ] Implement only deterministic normalization/alignment/bundle primitives; reject unknown evidence kinds and silently merged demand metrics.
- [ ] Re-run and verify GREEN.
- [ ] Commit as `feat: add SEO evidence bundle primitives`.

### Task 3: Join and quality propagation layer

**Files:**
- Create: `plugins/yandex-seo/scripts/seo_join.py`
- Create: `plugins/yandex-seo/scripts/seo_quality.py`
- Test: `plugins/yandex-seo/tests/test_seo_join.py`
- Test: `plugins/yandex-seo/tests/test_seo_quality.py`

**Interfaces:**
- Produces `join_queries(records: list[dict]) -> dict[str, list[dict]]` using only `normalize_query`.
- Produces `join_pages(records: list[dict]) -> dict[str, list[dict]]` using only conservative URL keys.
- Produces `propagate_limitations(source_records: list[dict]) -> list[dict]`.
- Produces `capability_mode(coverage: dict) -> str` returning `DISCOVERY|VISIBILITY|PERFORMANCE|FULL|PARTIAL`.

- [ ] Write failing tests proving no stemming/fuzzy query merge, no query-parameter deletion, propagation of Metrika sampling/Webmaster top-N/Search bridge-risk limitations, and correct partial capability modes.
- [ ] Run tests and verify RED.
- [ ] Implement joins and quality propagation without source-specific HTTP/API assumptions.
- [ ] Re-run and verify GREEN.
- [ ] Commit as `feat: join SEO evidence with quality context`.

### Task 4: Findings — opportunities, content gaps, cannibalization, technical impact

**Files:**
- Create: `plugins/yandex-seo/scripts/seo_opportunities.py`
- Create: `plugins/yandex-seo/scripts/seo_cannibalization.py`
- Test: `plugins/yandex-seo/tests/test_seo_opportunities.py`
- Test: `plugins/yandex-seo/tests/test_seo_cannibalization.py`

**Interfaces:**
- Produces `find_content_gaps(bundle: dict) -> list[dict]`.
- Produces `find_ctr_opportunities(bundle: dict) -> list[dict]` using own-site evidence only.
- Produces `find_conversion_opportunities(bundle: dict) -> list[dict]`.
- Produces `find_technical_blockers(bundle: dict) -> list[dict]`.
- Produces `find_cannibalization(bundle: dict) -> list[dict]`.

- [ ] Write failing tests distinguishing `DISCOVERY_CANDIDATE` from validated `CONTENT_GAP`, requiring multi-source evidence for cannibalization, preventing universal CTR thresholds, classifying landing/intent mismatch as `HYPOTHESIS`, and correlating technical blockers without asserting causality.
- [ ] Run tests and verify RED.
- [ ] Implement evidence-rule functions with explicit evidence kind/confidence/limitations fields.
- [ ] Re-run and verify GREEN.
- [ ] Commit as `feat: derive cross-service SEO findings`.

### Task 5: Transparent prioritization and delegated actions

**Files:**
- Create: `plugins/yandex-seo/scripts/seo_prioritize.py`
- Test: `plugins/yandex-seo/tests/test_seo_prioritize.py`

**Interfaces:**
- Produces `prioritize(findings: list[dict], priority_order: list[str] | None = None) -> list[dict]`.
- Produces `delegate_action(finding: dict) -> dict | None` with `service`, `skill`, `target`, `reason`, `requires_approval`.

- [ ] Write failing tests proving default prioritization is categorical/evidence-based rather than a hidden numeric score; user-provided ordering is explicit; recrawl/sitemap actions delegate to Webmaster with `requires_approval=true`; unsupported actions return no executable delegation.
- [ ] Run tests and verify RED.
- [ ] Implement deterministic transparent sorting and preview-only delegated actions.
- [ ] Re-run and verify GREEN.
- [ ] Commit as `feat: prioritize SEO findings and delegate previews`.

### Task 6: Production skills, references, and agent evals

**Files:**
- Replace: `plugins/yandex-seo/skills/*/SKILL.md`
- Create: `plugins/yandex-seo/references/evidence-bundle.md`
- Create: `plugins/yandex-seo/references/alignment.md`
- Create: `plugins/yandex-seo/references/findings.md`
- Create: `plugins/yandex-seo/references/quality.md`
- Create: `plugins/yandex-seo/references/safety.md`
- Create: `plugins/yandex-seo/references/sources.md`
- Modify: `plugins/yandex-seo/evals/scenarios.json`
- Test: `plugins/yandex-seo/tests/test_agent_contract.py`

**Interfaces:**
- Skills orchestrate capabilities, never hard-code tool names or API endpoints.
- Evals cover full/partial coverage, demand distinction, mismatched periods, content gaps, cannibalization, CTR/conversion hypotheses, technical blockers, prioritization, and delegated write previews.

- [ ] Write failing agent-contract tests for meaningful workflows, stop conditions, limitation disclosure, read-only boundary, no endpoint/credential strings, and valid eval schema.
- [ ] Run and verify RED.
- [ ] Write production skill/reference content implementing the approved spec.
- [ ] Run and verify GREEN.
- [ ] Commit as `docs: define Yandex SEO orchestration workflows`.

### Task 7: Marketplace, roadmap, and path-aware CI integration

**Files:**
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md`
- Modify: `docs/SERVICE_MATRIX.md`
- Modify: `docs/ROADMAP.md`
- Modify: `tests/test_marketplace_layout.py`

**Interfaces:**
- Marketplace exposes `./plugins/yandex-seo` independently at `1.0.0`.
- CI runs SEO tests/compile only for SEO/shared changes.
- Roadmap marks Phase 6A implemented and Phase 6B `yandex-marketing` next.

- [ ] Add failing root tests for marketplace entry, service matrix, Phase 6A roadmap state, and SEO CI job.
- [ ] Run root tests and verify RED.
- [ ] Update marketplace/docs/CI with no functional changes to prior plugin directories.
- [ ] Run root tests and repository validator; verify GREEN.
- [ ] Run fresh full regression: root + Direct + Metrika + Webmaster + Wordstat + Search + SEO, compile SEO helpers, parse all JSON, scan forbidden runtime paths, and hash prior plugin directories against the Phase 5 baseline.
- [ ] Publish only after the full gate is green, compare `phase-5-yandex-search...phase-6-yandex-seo`, and open stacked PR #6 targeting `phase-5-yandex-search`.
