# Fable Documentation UX & Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans` (or `subagent-driven-development` when available) and implement this plan task-by-task. Checkboxes are the execution record.

**Goal:** Turn the marketplace documentation into a human-first onboarding and governance surface while preserving the existing technical contracts, then publish a repository-only immutable `1.0.5` release with all plugin versions unchanged.

**Architecture:** Keep the root README as Level 1 landing content. Move detailed ownership/evidence/safety explanations into bilingual Level 2/3 documents. Reuse plugin-local verified references for volatile credentials/API facts instead of duplicating them. Keep the current release machinery unchanged except for adding the minimal `1.0.5` publisher in the proven `1.0.4` pattern; release-infrastructure simplification is PR B.

**Tech Stack:** Markdown RU/EN, Python 3.10/3.13, `unittest`, repository validators, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-04-fable-docs-ux-governance-design.md`

## Global constraints

- Base is `main` `4112edefbbcd0618e8bc81f535bf7ca3a90f79b7` / repository `1.0.4`.
- Target is repository-only `1.0.5`.
- Plugin versions stay exactly: Direct `2.0.1`, Metrika `2.0.0`, Webmaster `2.0.0`, Wordstat `1.1.2`, Search `1.0.2`, SEO `1.1.2`, Marketing `1.1.0`.
- Do not mutate/delete/retarget historical releases, tags, changelog history, or legacy publisher workflows.
- Do not change plugin runtime behavior.
- Do not invent runtime installation commands, OAuth scopes, or API facts. Verify current runtime-specific installation instructions from official sources before documenting them; otherwise use runtime-neutral wording.
- Keep RU as the primary user-facing language and EN as structural mirror.
- New bilingual docs must have reciprocal language links, matching H2-H6 level sequence, and matching SemVer token sets so `scripts/bilingual_docs.py` remains strict.
- Preserve exact machine identifiers (`preview_id`, evidence classes, reason codes) while making surrounding prose human-readable.
- Every mechanical contract change uses RED → GREEN evidence.

---

### Task 1: Define the documentation UX contract (RED)

**Files:**
- Create: `tests/test_documentation_ux_contracts.py`
- Modify: `tests/test_bilingual_docs.py`

**Contract:** the repository mechanically requires the new docs, onboarding anchors, governance rules, current release state, clarified Wordstat wording, and unchanged plugin versions.

- [ ] **Step 1: Add failing documentation UX tests**
  Create tests that require:
  - `docs/GETTING_STARTED.md` / `.en.md`;
  - `docs/ARCHITECTURE.md` / `.en.md`;
  - `docs/GLOSSARY.md` / `.en.md`;
  - `docs/RELEASE_POLICY.md` / `.en.md`;
  - `CONTRIBUTING.md`;
  - root RU/EN README links to Getting Started, Architecture, Release Policy, Service Matrix and plugin paths;
  - root RU/EN README badge/current repository version `1.0.5`;
  - Getting Started contains Python `3.10+`, both marketplace metadata paths, credential links into owning plugins, a read-only-first example, `preview_id`, and `--execute --approve`;
  - release policy states one repository SemVer line, independent plugin SemVer, AI audit as advisory input, CI as mechanical evidence, independent review as a distinct gate, and human release authorization;
  - Wordstat RU/EN README uses “Wordstat API в составе Yandex Search API v2” / “Wordstat API within Yandex Search API v2”;
  - every plugin manifest and both marketplace manifests retain the exact current matrix.
  Avoid subjective prose/word-count tests.
- [ ] **Step 2: Register new key docs in the existing bilingual test list**
  Extend `KEY_DOCS` in `tests/test_bilingual_docs.py` with `GETTING_STARTED`, `ARCHITECTURE`, `GLOSSARY`, `RELEASE_POLICY`.
- [ ] **Step 3: Commit RED**
  Commit message: `test: define documentation UX governance contract`.
- [ ] **Step 4: Observe RED CI**
  Open a draft PR if needed to obtain CI. Expected failures must be limited to missing docs/links/release state/Wordstat wording, not unrelated baseline regressions.

### Task 2: Build Level 2/3 bilingual documentation and validator coverage (GREEN for new-doc existence)

**Files:**
- Modify: `scripts/bilingual_docs.py`
- Create: `docs/GETTING_STARTED.md`
- Create: `docs/GETTING_STARTED.en.md`
- Create: `docs/ARCHITECTURE.md`
- Create: `docs/ARCHITECTURE.en.md`
- Create: `docs/GLOSSARY.md`
- Create: `docs/GLOSSARY.en.md`
- Create: `docs/RELEASE_POLICY.md`
- Create: `docs/RELEASE_POLICY.en.md`
- Create: `CONTRIBUTING.md`

**Interfaces:**
- `scripts.bilingual_docs.KEY_DOC_NAMES` becomes the canonical key-doc inventory.
- User onboarding links to service-owned references rather than copying volatile facts.

- [ ] **Step 1: Extend validator key-doc inventory**
  Add the four new bilingual doc names to `KEY_DOC_NAMES` in `scripts/bilingual_docs.py`.
- [ ] **Step 2: Verify runtime installation facts before exact instructions**
  Check current official OpenAI/Codex marketplace-import documentation and, if exact Claude Code installation syntax is to be named, current official Anthropic documentation. Only include exact UI/CLI steps that are verified. Otherwise describe the repository metadata paths and instruct users to use their runtime's marketplace import/registration flow.
- [ ] **Step 3: Write Getting Started RU/EN**
  Use the same heading-depth sequence and SemVer set in both files. Cover:
  1. requirements (`Python 3.10+` for bundled helpers);
  2. marketplace import/registration via `.agents/plugins/marketplace.json` and `.claude-plugin/marketplace.json`;
  3. task→plugin selection table;
  4. credential table linking to service-local authoritative references / `.env.example` without duplicating volatile scopes;
  5. canonical Direct read-only first result using the existing `campaigns get` command;
  6. cross-service note (SEO/Marketing own no credentials/transport);
  7. Direct write preview → later-turn approval → `--execute --approve <preview_id>` example;
  8. verification/troubleshooting commands.
- [ ] **Step 4: Write Architecture RU/EN**
  Move Level-3 details from root README: service vs cross-service ownership, transport-free SEO/Marketing, evidence/provenance classes, SEO and Marketing orchestration, progressive disclosure (`SKILL.md` vs `references/`), shared-code behavioral-contract policy, and safety ownership boundary. Keep exact invariants accessible without making this doc a changelog dump.
- [ ] **Step 5: Write Glossary RU/EN**
  Define recurring terms and exact tokens, including `preview_id`, `OBSERVED`, `DERIVED`, `HYPOTHESIS`, `METHODOLOGY`, `SERP_VALIDATION_MISSING`, `canonical`, `reconciliation_only`, `enrichment`, fail-closed, provenance, delegated preview, service plugin and cross-service plugin.
- [ ] **Step 6: Write Release Policy RU/EN**
  Define repository SemVer as the only future repository version line, independent plugin SemVer, historical OPUS/PHASE/DOCS/FABLE labels as codenames/history, immutable history, batching guidance, and release gates: AI audit advisory → tests/CI mechanical → independent review → human authorization → merge/main CI → publisher.
- [ ] **Step 7: Write CONTRIBUTING**
  Concise contributor entrypoint linking to Plugin Standard, Getting Started, Architecture, Release Policy, Review guide, tests and design/plan workflow. Do not create a second normative safety contract.
- [ ] **Step 8: Run focused GREEN checks**
  Expected commands: `python -m unittest tests.test_bilingual_docs tests.test_bilingual_docs_contracts tests.test_documentation_ux_contracts -v` and `python scripts/validate_repo.py`. Fix only structural/parity issues exposed by these checks.
- [ ] **Step 9: Commit**
  `docs: add human onboarding architecture and governance guides`.

### Task 3: Rewrite root README RU/EN as human-first Level 1 landing

**Files:**
- Modify: `README.md`
- Modify: `README.en.md`

**Contract:** root docs remain version-canonical and bilingual, but no longer carry PR-level implementation detail.

- [ ] **Step 1: Preserve required machine surfaces**
  Keep language-specific hero assets, reciprocal language links, current plugin table with exact versions, `## Версии` / `## Versions` exact version block, verification command `python -m compileall -q scripts`, and links required by existing tests.
- [ ] **Step 2: Rewrite top-level narrative**
  Use matching heading levels in RU/EN for:
  - what the project is / who it is for;
  - plugin catalog;
  - 3-minute quick start;
  - short end-to-end example;
  - compact safety lifecycle;
  - simplified SEO/Marketing orchestration diagrams;
  - limitations / what is not claimed;
  - documentation map;
  - versions / license.
- [ ] **Step 3: Move detail, do not delete contract knowledge**
  Remove landing-page-level prose about cluster ingress validation, rootless `BRIDGE`, evaluated-empty `null`/`[]`, individual transport adapter/error semantics and other release-review details. Ensure Architecture/Plugin Standard/plugin docs remain the linked home for those contracts.
- [ ] **Step 4: Stage repository version**
  Change the static release badge and explicit current repository state from `1.0.4` to `1.0.5`; do not change plugin version mentions.
- [ ] **Step 5: Verify root contracts**
  Run documentation UX tests, version mention tests, bilingual tests and repository validator.
- [ ] **Step 6: Commit**
  `docs: make marketplace readme human-first`.

### Task 4: Align governance sources and clarify Wordstat naming

**Files:**
- Modify: `docs/PLUGIN_STANDARD.md`
- Modify: `docs/PLUGIN_STANDARD.en.md`
- Modify: `docs/REVIEW_FIRST_RELEASE.md`
- Modify: `docs/REVIEW_FIRST_RELEASE.en.md`
- Modify: `plugins/yandex-wordstat/README.md`
- Modify: `plugins/yandex-wordstat/README.en.md`

**Contract:** current normative docs describe one future repository SemVer line and distinguish AI/CI/review/human responsibilities; Wordstat terminology is unambiguous without changing API/runtime behavior.

- [ ] **Step 1: Update Plugin Standard Section 8**
  Keep independent plugin SemVer. Replace the recommendation that new repository milestones may use `opus-*`/`docs-*` as competing version tags with a link/rule to `RELEASE_POLICY`: future repository releases use normal repository SemVer; historical labels remain historical.
- [ ] **Step 2: Align Review guide**
  Add a concise link to Release Policy and explicitly state that AI audit findings are review input, green CI is mechanical evidence, independent review is a separate check, and human approval authorizes merge/release. Keep RU/EN heading-depth/SemVer parity.
- [ ] **Step 3: Clarify Wordstat wording**
  Change only the human-facing product phrase to “Wordstat API в составе Yandex Search API v2” / “Wordstat API within Yandex Search API v2”. Preserve version `1.1.2` and all behavior claims.
- [ ] **Step 4: Verify GREEN**
  Run `python scripts/validate_repo.py`, documentation UX tests, bilingual tests, and Wordstat plugin tests/compileall (the plugin is affected by README change in path-aware CI even though runtime is unchanged).
- [ ] **Step 5: Commit**
  `docs: align release governance and Wordstat terminology`.

### Task 5: Stage repository-only 1.0.5 and publisher contract (RED → GREEN)

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `CHANGELOG.en.md`
- Create: `tests/test_docs_1_0_5_publisher.py`
- Create: `.github/workflows/publish-docs-1.0.5.yml`

**Contract:** only tag/release `1.0.5` is new; publication is gated on successful exact-main CI and verified immutable; plugin versions remain unchanged.

- [ ] **Step 1: Add `1.0.5` changelog entries RU/EN**
  Add the same release marker/date and matching heading structure/SemVer set. Summarize human-first README, Getting Started/Architecture/Glossary/Release Policy, contributor governance, Wordstat naming clarity, and unchanged plugin matrix. Do not rewrite historical entries.
- [ ] **Step 2: Write publisher tests first (RED)**
  Model `tests/test_fable_audit3_publisher.py`, but require `.github/workflows/publish-docs-1.0.5.yml`, exactly one `publish_one "1.0.5"`, no plugin tags, exact successful-main-CI guards, fail-closed/idempotent release state, unchanged manifest matrix, exact-target repository docs, and root tests/validator.
- [ ] **Step 3: Commit/observe publisher RED**
  Expected failure is missing `1.0.5` workflow only (plus any not-yet-staged release-state requirement). Capture CI run.
- [ ] **Step 4: Create minimal current-pattern publisher**
  Copy the proven `publish-fable-audit3-maintenance.yml` control shape and change only release-specific identifiers/verification/notes for `1.0.5`. Retain exact SHA checkout, stale-main guard, draft recovery, immutable verification, rollback cleanup, detached-worktree validation and complete-state idempotency. Do not edit historical publishers.
- [ ] **Step 5: Verify publisher GREEN**
  Run the focused publisher tests, then `python scripts/validate_repo.py` and all root tests.
- [ ] **Step 6: Commit**
  `release: prepare repository 1.0.5 docs governance`.

### Task 6: Final PR gate, review, merge and immutable release

**Files:** none unless review exposes a defect.

- [ ] **Step 1: Full exact-head branch CI**
  Require both root validation jobs (Python 3.10 and 3.13) plus all path-affected plugin jobs to succeed. Record final branch SHA and CI run ID.
- [ ] **Step 2: Independent exact-head review**
  Request `@codex review` on the final exact head. If review quota is unavailable, record the external limitation explicitly; do not misrepresent quota failure as a clean review. Any actual finding gets a focused RED→GREEN fix and a new exact-head CI/review attempt.
- [ ] **Step 3: Resolve review threads and confirm mergeability**
  Require no unresolved actionable threads and confirm PR head has not changed after the final CI/review evidence.
- [ ] **Step 4: Squash merge with expected-head guard**
  Squash into `main`; record merge SHA.
- [ ] **Step 5: Post-merge exact-main CI**
  Require full success on the merge SHA before treating publication as complete.
- [ ] **Step 6: Verify automatic `1.0.5` publisher**
  Confirm the new workflow starts via `workflow_run` from the successful main CI, succeeds, and creates only repository release/tag `1.0.5`.
- [ ] **Step 7: Verify immutable state**
  Confirm release `1.0.5` is non-draft, non-prerelease, immutable; tag resolves exactly to merge SHA; historical `1.0.4` and plugin releases remain unchanged.
- [ ] **Step 8: Final report**
  Report PR, final branch SHA, review status, CI IDs, merge SHA, post-merge CI, publisher run, release ID/tag/immutability, and unchanged plugin matrix. Note PR B remains a separate follow-up for release-infrastructure simplification.
