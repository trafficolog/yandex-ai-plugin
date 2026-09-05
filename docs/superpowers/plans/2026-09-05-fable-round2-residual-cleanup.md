# Fable Round 2 Residual Cleanup — Repository 1.0.8 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close every actionable residual from Fable 5.1 Round 2 without changing plugin runtime behavior or plugin SemVer, then publish immutable repository release `1.0.8`.

**Architecture:** Keep runtime plugins untouched. Harden repository-owned documentation/governance contracts through focused regression tests, make `ARCHITECTURE` the canonical ON_USE explanation, align Wordstat naming and ROADMAP semantics, complete community governance metadata, and stage a repository-only declarative release.

**Tech Stack:** Markdown, JSON, Python 3.10+/3.13 repository validators/tests, GitHub Actions, declarative release manifest.

**Spec:** `docs/superpowers/specs/2026-09-05-fable-round2-residual-cleanup-design.md`

## Global Constraints

- Base is `3d25004f32be1b544d0c12f2f82452ed4e26e5d4` (`main`, repository `1.0.7`).
- Repository version becomes `1.0.8`; `.github/releases/release.json` keeps `plugins: []`.
- Plugin versions remain Direct `2.0.1`, Metrika `2.0.0`, Webmaster `2.0.0`, Wordstat `1.1.2`, Search `1.0.2`, SEO `1.1.2`, Marketing `1.1.0`.
- No plugin helper/runtime code, plugin manifests, plugin changelogs, plugin eval schema/fixtures, or marketplace manifests may change.
- `docs/superpowers/` is historical implementation context only, never a production normative source.
- Current Wordstat product naming is RU `Wordstat API в составе Yandex Search API v2`, EN `Wordstat API within Yandex Search API v2`.
- Existing 17 requirement IDs retain meaning; add exactly `REQ-SKILL-CONTENT`.
- Model semantic eval execution remains backlog, not a claimed `1.0.8` capability.
- All implementation groups use strict RED → GREEN evidence before final exact-head CI.

---

### Task 1: Remove stale normative source and Wordstat naming drift

**Files:**
- Create: `tests/test_fable_round2_doc_contracts.py`
- Modify: `plugins/yandex-marketing/README.md`
- Modify: `plugins/yandex-marketing/README.en.md`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/ROADMAP.en.md`
- Modify: `docs/SERVICE_MATRIX.md`
- Modify: `docs/SERVICE_MATRIX.en.md`

**Interfaces:**
- Consumes: repository production docs on the branch.
- Produces: regression contract `FableRound2DocContractTests` preventing normative `docs/superpowers/` links from plugin READMEs and stale `Cloud Wordstat v2` naming.

- [ ] **Step 1: Write failing tests**

Create `tests/test_fable_round2_doc_contracts.py` with tests that:

```python
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class FableRound2DocContractTests(unittest.TestCase):
    def test_plugin_readmes_do_not_depend_on_superpowers_specs(self):
        for path in sorted((ROOT / "plugins").glob("*/README*.md")):
            with self.subTest(path=path):
                self.assertNotIn("docs/superpowers/", path.read_text(encoding="utf-8"))

    def test_current_wordstat_naming_is_canonical(self):
        pairs = (
            (ROOT / "docs/ROADMAP.md", "Wordstat API в составе Yandex Search API v2"),
            (ROOT / "docs/ROADMAP.en.md", "Wordstat API within Yandex Search API v2"),
            (ROOT / "docs/SERVICE_MATRIX.md", "Wordstat API в составе Yandex Search API v2"),
            (ROOT / "docs/SERVICE_MATRIX.en.md", "Wordstat API within Yandex Search API v2"),
        )
        for path, phrase in pairs:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn(phrase, text)
                self.assertNotIn("Cloud Wordstat v2", text)
```

- [ ] **Step 2: Verify RED in GitHub Actions**

Commit tests only. Open/refresh draft PR. Expected root-suite failures: Marketing README normative link and four stale Wordstat naming assertions; repository validator may remain green.

- [ ] **Step 3: Implement minimal documentation fixes**

Marketing RU/EN must replace the normative `docs/superpowers/specs/...` sentence with a statement that executable taxonomy is owned by current Marketing scripts/tests and repository production contracts; historical design specs may be consulted only as non-normative context.

ROADMAP and SERVICE_MATRIX RU/EN must replace `Cloud Wordstat v2` with the canonical phrase from Global Constraints without changing authentication/runtime semantics.

- [ ] **Step 4: Verify Task 1 GREEN**

Expected: `tests/test_fable_round2_doc_contracts.py` passes on Python 3.10 and 3.13; no plugin runtime/version file changed.

- [ ] **Step 5: Commit**

Commit message: `docs: close Fable normative-source and Wordstat naming drift`.

---

### Task 2: Align PLUGIN_STANDARD with the real SKILL contract

**Files:**
- Create: `tests/test_skill_standard_contract.py`
- Modify: `docs/PLUGIN_STANDARD.md`
- Modify: `docs/PLUGIN_STANDARD.en.md`

**Interfaces:**
- Consumes constants `MIN_SKILL_DESCRIPTION_CHARS = 32`, `MAX_SKILL_DESCRIPTION_CHARS = 500`, `MAX_SKILL_BYTES = 15 * 1024`, and existing write safety markers from `scripts/validate_repo.py`.
- Produces: stable requirement ID `REQ-SKILL-CONTENT` and documented mechanical/review split for SKILL bodies.

- [ ] **Step 1: Write failing tests**

Create `tests/test_skill_standard_contract.py` that imports the validator constants and asserts RU/EN standard contains:

```python
EXPECTED_ID = "REQ-SKILL-CONTENT"
EXPECTED_LIMIT_TEXT = "15 KiB"
EXPECTED_DESCRIPTION_RANGE = "32–500"
```

The tests must assert both languages include the same new ID and the documented numeric values match imported constants `32`, `500`, and `15 * 1024`. Also assert §5 contains concepts for progressive disclosure, non-ownership/delegation, limitation propagation, exact-preview metadata, and untrusted-data metadata.

- [ ] **Step 2: Verify RED**

Commit test only. Expected failures are absence of `REQ-SKILL-CONTENT` and incomplete §5 text; existing validator tests remain green.

- [ ] **Step 3: Update PLUGIN_STANDARD RU/EN**

Add exactly one requirement-table row:

`REQ-SKILL-CONTENT | SKILL.md keeps bounded discoverable metadata/content, progressive disclosure, explicit ownership/delegation boundaries and limitation propagation; write-capable skills preserve repository safety metadata. | validator + CI + review | scripts/validate_repo.py, this standard, ARCHITECTURE`

Rewrite §5 to state exact mechanical bounds and review-level body semantics. Do not add brittle heading-name grep validation and do not rewrite plugin SKILL files.

- [ ] **Step 4: Verify Task 2 GREEN**

Expected: new standard tests and existing governance requirement tests pass with 18 total stable requirement IDs.

- [ ] **Step 5: Commit**

Commit message: `docs: specify the repository SKILL content contract`.

---

### Task 3: Canonicalize ON_USE, ROADMAP semantics, community governance, and eval backlog

**Files:**
- Create: `tests/test_fable_round2_governance_baseline.py`
- Create: `CODE_OF_CONDUCT.md`
- Create: `CODE_OF_CONDUCT.en.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`
- Create: `.github/pull_request_template.md`
- Create: `docs/reviews/2026-09-05-fable-round2-closure.md`
- Create: `docs/reviews/2026-09-05-fable-round2-closure.en.md`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/ARCHITECTURE.en.md`
- Modify: `docs/PLUGIN_STANDARD.md`
- Modify: `docs/PLUGIN_STANDARD.en.md`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/ROADMAP.en.md`
- Modify: `docs/SERVICE_MATRIX.md`
- Modify: `docs/SERVICE_MATRIX.en.md`
- Modify: `plugins/yandex-seo/README.md`
- Modify: `plugins/yandex-seo/README.en.md`
- Modify: `plugins/yandex-marketing/README.md`
- Modify: `plugins/yandex-marketing/README.en.md`
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `scripts/bilingual_docs.py`

**Interfaces:**
- Consumes: existing ARCHITECTURE ownership model, SECURITY policy, CONTRIBUTING and review index.
- Produces: one canonical long-form ON_USE explanation, explicit model-eval backlog acceptance, corrected ROADMAP history/language, complete community-governance baseline, bilingual closure evidence.

- [ ] **Step 1: Write failing tests**

Create `tests/test_fable_round2_governance_baseline.py` with assertions that:

1. phrase `schema-compatible deferred-auth metadata` appears exactly once across the canonical/current RU production documentation set and its EN equivalent exactly once, both in `docs/ARCHITECTURE*`;
2. ROADMAP uses `Изначально выпущен` / `Initially shipped`, says Phase 4 had `девять initial workflow skills` / `nine initial workflow skills`, and RU no longer contains the two full English SEO/Marketing sentences;
3. ROADMAP RU/EN contains a `Model eval runner / judge` backlog item including semantic `outcome`, `must_convey`, `must_not_claim`, runtime/model/version/timestamp evidence and paired backend-equivalence preserving exact-preview + later-turn approval;
4. community files exist; bug template routes security-sensitive reports to `SECURITY.md`; PR template mentions scope, tests/CI, documentation, plugin SemVer, secrets/safety and review evidence;
5. root README RU/EN link `SECURITY`, `CONTRIBUTING`, `CODE_OF_CONDUCT`, and `docs/reviews/README`;
6. closure artifacts exist and distinguish `closed`, `closed as explicit backlog`, and `previously closed` without fake final SHA/run/release identifiers.

- [ ] **Step 2: Verify RED**

Commit tests only. Expected failures: duplicated ON_USE phrase, ROADMAP historical/language/backlog gaps, missing community files, missing closure artifact and missing README governance links.

- [ ] **Step 3: Make ARCHITECTURE the ON_USE owner**

Add the complete explanation to `docs/ARCHITECTURE.md` and `.en.md`. Replace duplicated long-form prose in PLUGIN_STANDARD, SERVICE_MATRIX and SEO/Marketing READMEs with concise statements linking to ARCHITECTURE; do not weaken transport/credential ownership semantics.

- [ ] **Step 4: Fix ROADMAP semantics and add eval backlog**

Change Phase 2–6 historical wording to explicit initial-release language, Phase 4 to nine initial workflow skills, translate the known RU English prose, and add a Future backlog subsection `Model eval runner / judge` with the exact acceptance criteria from the spec. Add RU-primary policy sentence allowing product names/code/technical terms but not ordinary EN prose sentences in RU primary docs unless quoted.

- [ ] **Step 5: Add community-governance files**

Create bilingual Code of Conduct with behavioral expectations, scope, reporting/escalation via repository-maintainer channels without inventing private contact details or SLA. Create GitHub bug/feature templates and PR template. Security-sensitive bug template text must direct users to `SECURITY.md` and avoid requesting public exploit details.

- [ ] **Step 6: Extend bilingual validation**

Add `SECURITY` and `CODE_OF_CONDUCT` as root policy pairs checked by `scripts/bilingual_docs.py`; preserve existing key docs/plugin pair validation.

- [ ] **Step 7: Add Fable Round 2 closure artifact**

RU/EN dated artifact maps each original Round 2 finding to one of `closed`, `closed as explicit backlog`, `previously closed`, and names mechanical versus semantic evidence. It may cite PR number once known, but must state final exact-head/post-merge/release evidence lives in PR/release records and must not fabricate future IDs.

- [ ] **Step 8: Verify Task 3 GREEN**

Expected: new governance baseline tests, bilingual validation and full existing root tests pass.

- [ ] **Step 9: Commit**

Commit message: `docs: complete Fable Round 2 governance baseline`.

---

### Task 4: Stage repository-only release 1.0.8

**Files:**
- Create: `tests/test_repository_1_0_8_release_surfaces.py`
- Create: `.github/releases/1.0.8.md`
- Modify: `.github/releases/release.json`
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `CHANGELOG.md`
- Modify: `CHANGELOG.en.md`

**Interfaces:**
- Consumes: generic publisher contract introduced in repository `1.0.6`.
- Produces: current repository release declaration `1.0.8` with `plugins: []` and synchronized root release surfaces.

- [ ] **Step 1: Write failing release tests**

Create `tests/test_repository_1_0_8_release_surfaces.py` asserting:

```python
EXPECTED_PLUGINS = {
    "yandex-direct": "2.0.1",
    "yandex-metrika": "2.0.0",
    "yandex-webmaster": "2.0.0",
    "yandex-wordstat": "1.1.2",
    "yandex-search": "1.0.2",
    "yandex-seo": "1.1.2",
    "yandex-marketing": "1.1.0",
}
```

Assert current manifest repository version/tag is `1.0.8`, `plugins == []`, `.github/releases/1.0.8.md` exists, root README RU/EN identify current repository release `1.0.8`, root CHANGELOG RU/EN both contain a `1.0.8` release marker, and every plugin `.codex-plugin/plugin.json`/`.claude-plugin/plugin.json` remains at the expected version.

- [ ] **Step 2: Verify RED**

Commit tests only. Expected failures are exclusively current `1.0.7` release surfaces and missing `1.0.8` notes; plugin version-lock assertions must already pass.

- [ ] **Step 3: Stage manifest/notes/README/CHANGELOG**

Set repository declaration to version/tag `1.0.8`, title `Repository 1.0.8`, notes `.github/releases/1.0.8.md`, and `plugins: []`. Update RU/EN README release badge/current-release line and prepend synchronized `1.0.8` changelog entries describing Fable Round 2 residual cleanup. Notes must explicitly list unchanged plugin versions and say no plugin tags are published.

- [ ] **Step 4: Verify Task 4 GREEN**

Expected: release tests pass and generic release-manifest validator accepts `1.0.8`.

- [ ] **Step 5: Commit**

Commit message: `chore: stage repository 1.0.8 release`.

---

### Task 5: Final verification, review, merge, and immutable publication

**Files:**
- Modify only if a real review/CI defect requires a RED→GREEN fix.

**Interfaces:**
- Consumes: Tasks 1–4 green head.
- Produces: exact tested merge SHA and immutable GitHub release/tag `1.0.8` with historical/plugin invariants preserved.

- [ ] **Step 1: Run exact-head full CI**

Require repository validator/tests on Python 3.10 and 3.13 plus all seven plugin jobs green. Record Actions run ID and exact branch SHA.

- [ ] **Step 2: Perform scope verification**

Diff from base must contain no `plugins/*/scripts`, plugin manifests, plugin changelogs, plugin evals or marketplace manifests. Allowed plugin changes are documentation-only README corrections for SEO/Marketing.

- [ ] **Step 3: Request independent review**

Request Codex/available independent code review on the exact green head. If quota/tool limitation prevents review, record it explicitly in PR evidence and do not call the review clean.

- [ ] **Step 4: Resolve real findings via RED→GREEN**

For each valid finding, first commit a focused failing regression proving the defect, capture RED CI, then implement the minimal correction, capture exact-head GREEN CI, and resolve the review thread with evidence.

- [ ] **Step 5: Squash merge with expected-head guard**

Merge only the exact final green head into `main` using squash. Record the returned merge SHA.

- [ ] **Step 6: Verify post-merge CI**

Require full CI green on the exact squash-merge SHA before treating publication as complete.

- [ ] **Step 7: Verify generic publisher**

Require `Publish current declared release` workflow-run success on the exact merge SHA and verify steps: manifest validation, exact target, immutable publication, complete immutable release-set verification.

- [ ] **Step 8: Verify immutable release and history**

Verify GitHub release `1.0.8` is `draft=false`, `prerelease=false`, `immutable=true`, release target and git tag both equal the merge SHA. Re-check release/tag `1.0.7` still targets `3d25004f32be1b544d0c12f2f82452ed4e26e5d4`. Verify no new `yandex-*` tag targets the `1.0.8` merge SHA.

- [ ] **Step 9: Final report**

Report PR number, final pre-merge SHA, exact-head CI, merge SHA, post-merge CI, publisher run, release ID/state, historical `1.0.7` invariant and unchanged plugin versions. Distinguish independent-review result from CI/self-review evidence.
