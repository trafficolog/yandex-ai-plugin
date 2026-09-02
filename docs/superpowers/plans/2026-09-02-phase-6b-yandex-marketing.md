# Yandex Marketing Cross-Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `yandex-marketing` 1.0.0 as a read-only paid-acquisition cross-service plugin that combines Direct, Metrika, Wordstat and optional Search evidence without double counting or bypassing owning-plugin safety contracts.

**Architecture:** The plugin consumes structured JSON/artifacts from existing service plugins, normalizes them into a versioned Marketing Evidence Bundle, validates KPI/attribution/money context, reconciles overlapping Direct/Metrika metrics, derives evidence-based findings, and emits preview-only delegated actions. It contains no Yandex HTTP clients, credentials, API endpoint knowledge, or live mutation code.

**Tech Stack:** Python 3.13 standard library only, JSON fixtures, repository plugin manifests/skills/evals, `unittest`, existing repository validator and GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-02-yandex-marketing-plugin-design.md`

## Global Constraints

- Target plugin version is `1.0.0`.
- Direct evidence is mandatory for paid-acquisition analysis; without Direct, route to the relevant source plugin instead of fabricating marketing analysis.
- Metrika and Wordstat are primary enrichments; Search is optional context and never determines paid efficiency.
- No direct Yandex API calls, credentials, OAuth, API keys, HTTP clients, or duplicated volatile endpoint knowledge.
- `scripts/` must contain pure data transformation/analysis code using Python standard library only.
- Read/analyze/reconcile/recommend/preview only; no live campaign, budget, bid, keyword, negative, strategy, goal, counter, or other writes.
- Preserve source provenance and classify evidence as `OBSERVED`, `DERIVED`, or `HYPOTHESIS`.
- Direct and Metrika overlapping clicks, cost, conversions, and revenue are compared/reconciled, never summed.
- KPI fingerprint compatibility is required before CPA/ROAS/revenue comparisons.
- Money context preserves currency, VAT basis, period and date basis when known.
- Conversion reconciliation returns only `ALIGNED`, `EXPLAINABLE_DIFFERENCE`, `REVIEW`, or `INCOMPARABLE`.
- Maturity returns `MATURE`, `IMMATURE`, or `MATURITY_UNKNOWN`; no universal “ignore last N days” rule.
- Query normalization is Unicode normalization + trim + case fold + whitespace collapse only.
- URL normalization is conservative and must not remove query parameters.
- Wordstat demand is external demand evidence, not guaranteed ad inventory or missed traffic.
- No universal CPA/ROAS/CTR/CR/CPC/click thresholds and no opaque Marketing Score.
- Delegated actions identify owning plugin/skill/target and `requires_approval`, but do not execute.

---

### Task 1: Plugin package and discovery contract

**Files:**
- Create: `plugins/yandex-marketing/.codex-plugin/plugin.json`
- Create: `plugins/yandex-marketing/.claude-plugin/plugin.json`
- Create: `plugins/yandex-marketing/README.md`
- Create: `plugins/yandex-marketing/CHANGELOG.md`
- Create: `plugins/yandex-marketing/THIRD_PARTY_NOTICES.md`
- Create: `plugins/yandex-marketing/evals/scenarios.json`
- Create: `plugins/yandex-marketing/skills/*/SKILL.md`
- Test: `plugins/yandex-marketing/tests/test_plugin_layout.py`

**Interfaces:**
- Produces eleven discoverable skills: `yandex-marketing`, `yandex-marketing-audit`, `yandex-marketing-performance`, `yandex-marketing-demand`, `yandex-marketing-queries`, `yandex-marketing-landings`, `yandex-marketing-conversions`, `yandex-marketing-attribution`, `yandex-marketing-budget`, `yandex-marketing-opportunities`, `yandex-marketing-prioritize`.

- [ ] **Step 1: Write the failing package-layout test.** Assert both manifests exist, version is `1.0.0`, all eleven skill directories exist, evals/references/scripts/tests directories exist, and no `.env.example` or credential requirement is present.
- [ ] **Step 2: Run the test and verify RED.** Run `python -m unittest tests.test_plugin_layout -v` from `plugins/yandex-marketing`; expected failure is missing package files/directories.
- [ ] **Step 3: Add the minimal package.** Create manifests, README/changelog/notices, eleven skill stubs with valid `Use when...` frontmatter, eval skeleton, references/scripts/tests directories.
- [ ] **Step 4: Re-run and verify GREEN.** The layout test must pass without adding analytical behavior.
- [ ] **Step 5: Commit.** `feat: scaffold Yandex Marketing cross-service plugin`.

### Task 2: Context, KPI fingerprint, normalization, and Marketing Evidence Bundle

**Files:**
- Create: `plugins/yandex-marketing/scripts/marketing_context.py`
- Create: `plugins/yandex-marketing/scripts/marketing_bundle.py`
- Test: `plugins/yandex-marketing/tests/test_marketing_context.py`
- Test: `plugins/yandex-marketing/tests/test_marketing_bundle.py`

**Interfaces:**
- Produces `normalize_query(text: str) -> str`.
- Produces `normalize_url(url: str) -> str`.
- Produces `kpi_fingerprint(data: dict) -> dict`.
- Produces `compare_kpi_fingerprints(left: dict, right: dict) -> dict` returning `compatible: bool` plus mismatched fields.
- Produces `classify_period_alignment(items: list[dict]) -> str` returning `EXACT|APPROXIMATE|MISMATCHED`.
- Produces `classify_maturity(evidence: dict) -> str` returning `MATURE|IMMATURE|MATURITY_UNKNOWN`.
- Produces `new_bundle(context: dict, coverage: dict) -> dict` and `add_evidence(bundle: dict, evidence: dict) -> dict`.

- [ ] **Step 1: Write failing tests.** Cover Unicode/case/whitespace query normalization; conservative URL normalization preserving query parameters; KPI mismatches for goal, attribution, metric basis, currency and VAT; exact/approximate/mismatched periods; three maturity states; Direct-required coverage; observed/derived/hypothesis validation.
- [ ] **Step 2: Verify RED.** Run both new test modules and confirm failures are due to missing functions.
- [ ] **Step 3: Implement minimal deterministic primitives.** Reject unknown evidence kinds, unknown maturity/alignment states, ambiguous missing Direct coverage for paid-acquisition mode, and monetary comparisons with incompatible currency unless explicitly marked incomparable.
- [ ] **Step 4: Verify GREEN.** Re-run both modules.
- [ ] **Step 5: Commit.** `feat: add marketing bundle and KPI context primitives`.

### Task 3: Entity joins, source ownership, reconciliation, and quality propagation

**Files:**
- Create: `plugins/yandex-marketing/scripts/marketing_join.py`
- Create: `plugins/yandex-marketing/scripts/marketing_quality.py`
- Test: `plugins/yandex-marketing/tests/test_marketing_join.py`
- Test: `plugins/yandex-marketing/tests/test_marketing_quality.py`

**Interfaces:**
- Produces `join_campaigns(records: list[dict]) -> dict[str, list[dict]]` keyed by campaign ID.
- Produces `join_goals(records: list[dict]) -> dict[str, list[dict]]` keyed by goal ID.
- Produces `join_queries(records: list[dict]) -> dict[str, list[dict]]` using only normalized query keys.
- Produces `join_landings(records: list[dict]) -> dict[str, list[dict]]` using conservative URL keys.
- Produces `canonical_metric(metric: str, records: list[dict]) -> dict | None` according to source-of-truth rules.
- Produces `reconcile_metric(metric: str, records: list[dict], context: dict) -> dict` with `ALIGNED|EXPLAINABLE_DIFFERENCE|REVIEW|INCOMPARABLE`.
- Produces `propagate_limitations(source_records: list[dict]) -> list[dict]`.
- Produces `capability_mode(coverage: dict) -> str` returning `DIRECT_ONLY|PAID_PERFORMANCE|DEMAND_PLANNING|QUERY_INTELLIGENCE|FULL_ACQUISITION|COMPETITIVE_CONTEXT`.

- [ ] **Step 1: Write failing tests.** Prove campaign/name collisions do not join; goal names do not replace IDs; fuzzy/stemmed queries remain separate; URL parameters remain part of landing identity; Direct cost/clicks remain canonical; Direct and Metrika conversions are never added; incompatible KPI contexts return `INCOMPARABLE`; sampling/data-lag/maturity limitations propagate.
- [ ] **Step 2: Verify RED.** Run the two modules.
- [ ] **Step 3: Implement joins/reconciliation.** Use explicit source roles; never compute totals across overlapping Direct/Metrika observations.
- [ ] **Step 4: Verify GREEN.** Re-run and inspect reconciliation payloads for source provenance.
- [ ] **Step 5: Commit.** `feat: reconcile paid acquisition evidence safely`.

### Task 4: Paid performance, derived metrics, and conversion reconciliation

**Files:**
- Create: `plugins/yandex-marketing/scripts/marketing_performance.py`
- Test: `plugins/yandex-marketing/tests/test_marketing_performance.py`

**Interfaces:**
- Produces `derive_performance(record: dict, kpi: dict) -> dict`.
- Produces `compare_performance(left: dict, right: dict) -> dict`.
- Produces `reconcile_conversions(direct: dict, metrika: dict, context: dict) -> dict`.

- [ ] **Step 1: Write failing tests.** Verify CPC/CPA/CR/ROAS are calculated only when inputs are present and compatible; revenue absence blocks ROAS/DRR; different goals block CPA ranking; VAT/currency mismatch blocks monetary comparison; maturity marks findings as limited; Direct/Metrika conversion differences can be `EXPLAINABLE_DIFFERENCE` without being tracking defects.
- [ ] **Step 2: Verify RED.** Run the module.
- [ ] **Step 3: Implement minimal arithmetic and compatibility checks.** Do not infer revenue, target CPA, conversion lag, or business goal semantics.
- [ ] **Step 4: Verify GREEN.** Re-run.
- [ ] **Step 5: Commit.** `feat: derive compatible paid performance metrics`.

### Task 5: Demand/query/landing opportunity findings

**Files:**
- Create: `plugins/yandex-marketing/scripts/marketing_demand.py`
- Create: `plugins/yandex-marketing/scripts/marketing_opportunities.py`
- Test: `plugins/yandex-marketing/tests/test_marketing_demand.py`
- Test: `plugins/yandex-marketing/tests/test_marketing_opportunities.py`

**Interfaces:**
- Produces `find_demand_candidates(bundle: dict) -> list[dict]`.
- Produces `find_query_candidates(bundle: dict) -> list[dict]`.
- Produces `find_landing_hypotheses(bundle: dict) -> list[dict]`.
- Produces `find_budget_candidates(bundle: dict) -> list[dict]`.
- Produces `find_measurement_risks(bundle: dict) -> list[dict]`.

- [ ] **Step 1: Write failing tests.** High Wordstat demand + weak Direct coverage yields `DEMAND_EXPANSION_CANDIDATE`, never numerical missed traffic; zero-conversion search term alone never yields an automatic exclusion; exclusion review requires business/KPI context plus sufficiency/maturity evidence; landing mismatch remains `HYPOTHESIS`; Search context may enrich intent but never change CPA/ROAS; budget candidates require comparable KPIs and sufficient mature evidence.
- [ ] **Step 2: Verify RED.** Run both modules.
- [ ] **Step 3: Implement evidence-rule functions.** Include `kind`, `confidence`, `evidence`, `limitations`, and `next_step` in every finding.
- [ ] **Step 4: Verify GREEN.** Re-run.
- [ ] **Step 5: Commit.** `feat: derive paid acquisition opportunities`.

### Task 6: Transparent prioritization and delegated action previews

**Files:**
- Create: `plugins/yandex-marketing/scripts/marketing_prioritize.py`
- Test: `plugins/yandex-marketing/tests/test_marketing_prioritize.py`

**Interfaces:**
- Produces `prioritize(findings: list[dict], priority_order: list[str] | None = None) -> list[dict]`.
- Produces `delegate_action(finding: dict) -> dict | None` containing `service`, `skill`, `target`, `reason`, `requires_approval` and preview metadata.

- [ ] **Step 1: Write failing tests.** Default ordering is deterministic and categorical, not an opaque score; user-provided order is explicit; budget changes delegate to `yandex-direct-budget`; query/negative changes delegate to `yandex-direct-keywords`; strategy/targeting changes delegate to `yandex-direct-optimize`; campaign creation delegates to `yandex-direct-create`; goal changes delegate to `yandex-metrika-goals`; all consequential delegations set `requires_approval=true`; unsupported findings produce no executable action.
- [ ] **Step 2: Verify RED.** Run the module.
- [ ] **Step 3: Implement preview-only delegation.** No API calls, credential access, or mutation functions.
- [ ] **Step 4: Verify GREEN.** Re-run.
- [ ] **Step 5: Commit.** `feat: prioritize marketing findings and delegate previews`.

### Task 7: Production skills, references, and eval contract

**Files:**
- Replace: `plugins/yandex-marketing/skills/*/SKILL.md`
- Create: `plugins/yandex-marketing/references/evidence-bundle.md`
- Create: `plugins/yandex-marketing/references/kpi-context.md`
- Create: `plugins/yandex-marketing/references/reconciliation.md`
- Create: `plugins/yandex-marketing/references/findings.md`
- Create: `plugins/yandex-marketing/references/quality.md`
- Create: `plugins/yandex-marketing/references/safety.md`
- Create: `plugins/yandex-marketing/references/sources.md`
- Modify: `plugins/yandex-marketing/evals/scenarios.json`
- Test: `plugins/yandex-marketing/tests/test_agent_contract.py`

**Interfaces:**
- Skills orchestrate service capabilities without hard-coded API endpoints or runtime-specific paths.
- Evals cover Direct-required routing, Direct/Metrika reconciliation, KPI mismatch, demand expansion, query review, landing hypotheses, attribution/maturity, budget preview and delegated writes.

- [ ] **Step 1: Write failing agent-contract tests.** Require meaningful workflows/stop conditions, explicit double-count prevention, KPI fingerprint disclosure, Search optionality, no universal thresholds, read-only boundary, no endpoint/credential strings, and valid eval schema.
- [ ] **Step 2: Verify RED.** Run the agent-contract module.
- [ ] **Step 3: Write production skill/reference content.** Keep volatile API facts in source plugins; document only cross-service contracts and provenance rules here.
- [ ] **Step 4: Verify GREEN.** Re-run all marketing plugin tests.
- [ ] **Step 5: Commit.** `docs: define Yandex Marketing orchestration workflows`.

### Task 8: Marketplace, roadmap, service matrix, and path-aware CI integration

**Files:**
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/SERVICE_MATRIX.md`
- Modify: `tests/test_marketplace_layout.py`

**Interfaces:**
- Root marketplace exposes `yandex-marketing` 1.0.0.
- CI detects `plugins/yandex-marketing/**` and runs marketing tests/compile checks without functionally changing existing plugins.

- [ ] **Step 1: Write failing root tests.** Assert marketing marketplace entries, roadmap Phase 6B implementation state, service-matrix entry, README listing, and dedicated path-aware CI job.
- [ ] **Step 2: Verify RED.** Run root tests against the Phase 6A base plus new test expectations.
- [ ] **Step 3: Integrate the plugin.** Update the two marketplaces, roadmap, service matrix, README, change detector and marketing CI job. Compile exactly the eight marketing helpers.
- [ ] **Step 4: Run full verification.** Run root tests, repository validator, all marketing tests, `py_compile` on eight helpers, JSON parse checks, forbidden endpoint/credential/runtime-path scan, and regression tests for existing plugins through GitHub Actions after PR publication.
- [ ] **Step 5: Verify remote diff.** Phase 6A → Phase 6B must contain only marketing/root/spec/plan files and no changes inside Direct, Metrika, Webmaster, Wordstat, Search or SEO plugin directories.
- [ ] **Step 6: Commit.** `feat: integrate Yandex Marketing into marketplace`.
- [ ] **Step 7: Open stacked PR.** Head `phase-6b-yandex-marketing`, base `phase-6-yandex-seo`; report local verification separately from GitHub CI and do not merge without explicit user instruction.

## Final verification contract

Before completion, run fresh checks after the last functional change:

```bash
python -m unittest discover -s plugins/yandex-marketing/tests -v
python -m py_compile \
  plugins/yandex-marketing/scripts/marketing_context.py \
  plugins/yandex-marketing/scripts/marketing_bundle.py \
  plugins/yandex-marketing/scripts/marketing_join.py \
  plugins/yandex-marketing/scripts/marketing_quality.py \
  plugins/yandex-marketing/scripts/marketing_performance.py \
  plugins/yandex-marketing/scripts/marketing_demand.py \
  plugins/yandex-marketing/scripts/marketing_opportunities.py \
  plugins/yandex-marketing/scripts/marketing_prioritize.py
```

The published PR must then pass repository/root validation and all path-triggered regression jobs in GitHub Actions. Do not claim server CI success until the actual workflow run reports `completed / success`.