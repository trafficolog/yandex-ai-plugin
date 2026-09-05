# Governance & Traceability Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship repository-only `1.0.7` with function-level contract traceability, explicit governance requirements, bilingual review/security artifacts, and no plugin runtime/SemVer changes.

**Architecture:** Keep runtime plugins untouched. Upgrade only repository governance metadata and validators: `CONTRACT_MATRIX.json` becomes schema v2 with exact Python test selectors, `contract_controls.py` resolves selectors through AST, governance docs become explicit and bilingual, and the existing declarative publisher releases repository `1.0.7` with `plugins: []`.

**Tech Stack:** Python 3.10+, standard-library `ast`, `json`, `pathlib`, `unittest`; Markdown/JSON governance artifacts; existing GitHub Actions CI and `publish-current-release.yml`.

**Spec:** `docs/superpowers/specs/2026-09-05-governance-traceability-hardening-design.md`

## Global Constraints

- Base is `main` at `88d2f45e63308a476cbe456402bf17dc847436cb`.
- Repository release target is `1.0.7`; `.github/releases/release.json` keeps `plugins: []`.
- Plugin SemVer remains Direct `2.0.1`, Metrika `2.0.0`, Webmaster `2.0.0`, Wordstat `1.1.2`, Search `1.0.2`, SEO `1.1.2`, Marketing `1.1.0`.
- Do not modify plugin runtime helpers, API behavior, write execution, transport ownership, credentials, or plugin changelog versions.
- Do not mutate historical tags/releases.
- `docs/superpowers/` remains historical implementation context, never the sole normative source of a production invariant.
- Root verification remains `python scripts/validate_repo.py` and `python -m unittest discover -s tests -v` on Python 3.10+.

---

### Task 1: CONTRACT_MATRIX v2 and AST selector validation

**Files:**
- Modify: `scripts/contract_controls.py`
- Modify: `tests/test_contract_controls.py`
- Modify: `docs/CONTRACT_MATRIX.json`

**Interfaces:**
- Consumes: existing `validate_contract_matrix(root, matrix, *, known_plugins, today=None, changed_paths=None, strict_freshness=False) -> list[str]`.
- Produces: schema-v2 `test_refs` validation inside the same public function; no caller signature change.
- Selector grammar: `path.py::test_function` or `path.py::TestClass::test_method`.

- [ ] **Step 1: Write RED matrix-v2 contract tests**

Update the fixture in `ContractMatrixTests.make_tree()` to create both selector shapes:

```python
test.write_text(
    "import unittest\n\n"
    "def test_value():\n"
    "    assert True\n\n"
    "class HelperTests(unittest.TestCase):\n"
    "    def test_method(self):\n"
    "        self.assertTrue(True)\n",
    encoding="utf-8",
)
matrix = {
    "version": 2,
    "contracts": [{
        "id": "direct.preview-before-write",
        "plugin": "yandex-direct",
        "status": "implemented",
        "skills": ["plugins/yandex-direct/skills/router/SKILL.md"],
        "helpers": ["plugins/yandex-direct/scripts/helper.py"],
        "test_refs": ["plugins/yandex-direct/tests/test_helper.py::test_value"],
        "references": ["plugins/yandex-direct/references/api.md"],
        "freshness_controlled_references": ["plugins/yandex-direct/references/api.md"],
    }],
}
```

Add explicit tests for: legacy `tests` key rejection; mixed `tests` + `test_refs`; valid top-level selector; valid class method selector; missing function/class/method; malformed selector; `../` escape; non-`.py`; invalid syntax; non-UTF8 bytes; `@unittest.skip`; class-level `@unittest.skip`; `skipIf(True)`; `skipUnless(False)`; and a dynamic condition such as `@unittest.skipIf(FLAG, "runtime")` that must not be treated as statically skipped.

- [ ] **Step 2: Run RED tests**

Run:

```bash
python -m unittest tests.test_contract_controls.ContractMatrixTests -v
```

Expected: failures showing v1-only validation and missing selector/AST/skip behavior.

- [ ] **Step 3: Implement minimal AST selector support**

In `scripts/contract_controls.py`, import `ast` and add focused helpers with these exact interfaces:

```python
def _parse_test_ref(raw: str) -> tuple[str, str | None, str]:
    parts = raw.split("::")
    if len(parts) == 2:
        path, function = parts
        return path, None, function
    if len(parts) == 3:
        path, class_name, method = parts
        return path, class_name, method
    raise ValueError("test_ref must use path.py::test_function or path.py::TestClass::test_method")


def _decorator_terminal_name(node: ast.expr) -> str | None:
    target = node.func if isinstance(node, ast.Call) else node
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return None


def _is_literal_bool(node: ast.expr, expected: bool) -> bool:
    return isinstance(node, ast.Constant) and node.value is expected
```

Add `_is_statically_skipped(decorators: list[ast.expr]) -> bool` implementing exactly the spec's `skip`, literal `skipIf(True)`, and literal `skipUnless(False)` rules. Add `_validate_test_ref(root, raw, contract_id, errors) -> None` that safely resolves the file, decodes UTF-8, parses AST, resolves exactly one target, requires terminal `test_`, and rejects static skip on the method/function or containing class.

Update `validate_contract_matrix` to require `matrix["version"] == 2`, forbid `tests`, parse `test_refs` as a string list, require at least one `test_ref` for both `implemented` and `infrastructure`, and call `_validate_test_ref` for every selector.

- [ ] **Step 4: Run targeted GREEN tests**

Run:

```bash
python -m unittest tests.test_contract_controls.ContractMatrixTests -v
```

Expected: all matrix/AST selector tests pass.

- [ ] **Step 5: Migrate production matrix to v2**

Change `docs/CONTRACT_MATRIX.json` to `"version": 2`, remove every `tests` field, and replace it with exact `test_refs` that resolve to current non-skipped functions/methods. Each implemented/infrastructure entry must carry at least one exact selector that materially corresponds to the named contract.

- [ ] **Step 6: Verify production matrix and root validator**

Run:

```bash
python scripts/validate_repo.py
python -m unittest tests.test_contract_controls -v
```

Expected: both commands exit 0.

- [ ] **Step 7: Commit Task 1**

```bash
git add scripts/contract_controls.py tests/test_contract_controls.py docs/CONTRACT_MATRIX.json
git commit -m "feat: add function-level contract traceability"
```

---

### Task 2: Explicit normative requirement registry in PLUGIN_STANDARD

**Files:**
- Modify: `docs/PLUGIN_STANDARD.md`
- Modify: `docs/PLUGIN_STANDARD.en.md`
- Create: `tests/test_governance_requirements.py`

**Interfaces:**
- Produces the fixed 17-ID requirement set from the spec as Markdown table rows with four non-empty columns: `REQ-ID`, requirement, enforcement, canonical document.

- [ ] **Step 1: Write RED parser/contract test**

Create `tests/test_governance_requirements.py` with:

```python
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "REQ-SKILL-ROUTING", "REQ-REFERENCE-VOLATILITY", "REQ-HELPER-TESTS",
    "REQ-EVAL-CONTRACT", "REQ-READ-FIRST", "REQ-WRITE-PREVIEW",
    "REQ-EXPLICIT-APPROVAL", "REQ-NO-SECRETS", "REQ-CAPABILITY-MATRIX",
    "REQ-PLUGIN-SEMVER", "REQ-NO-UNIVERSAL-THRESHOLDS",
    "REQ-RUNTIME-PATH-PORTABILITY", "REQ-SOURCE-SEMANTICS",
    "REQ-CROSS-SERVICE-TRANSPORT", "REQ-BILINGUAL-DOCS",
    "REQ-CHANGELOG-PARITY", "REQ-DOCS-RELEASE-NO-PLUGIN-BUMP",
}


def parse_rows(text: str) -> dict[str, list[str]]:
    rows = {}
    for line in text.splitlines():
        if not line.startswith("| REQ-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0]] = cells
    return rows


class GovernanceRequirementTests(unittest.TestCase):
    def test_ru_en_requirement_ids_match_fixed_set_and_rows_are_complete(self):
        for filename in ("docs/PLUGIN_STANDARD.md", "docs/PLUGIN_STANDARD.en.md"):
            rows = parse_rows((ROOT / filename).read_text(encoding="utf-8"))
            self.assertEqual(set(rows), EXPECTED, filename)
            self.assertEqual(len(rows), len(EXPECTED), filename)
            for req_id, cells in rows.items():
                self.assertEqual(len(cells), 4, req_id)
                self.assertTrue(all(cells), (req_id, cells))
                self.assertRegex(cells[2].lower(), r"validator|ci|review|policy")
```

- [ ] **Step 2: Run RED test**

Run `python -m unittest tests.test_governance_requirements -v`.
Expected: failure because the requirement table does not yet exist.

- [ ] **Step 3: Replace the compressed §2 paragraph in RU/EN docs**

Add the same 17 IDs in both files, one per row, preserving current requirements. Enforcement cells must truthfully distinguish `validator`, `CI`, `review`, and `policy`; canonical-document cells must name real current files such as `docs/PLUGIN_STANDARD.md`, `docs/CONTRACT_MATRIX.json`, `docs/EVAL_TOKEN_REGISTRY.json`, `scripts/validate_repo.py`, or `docs/RELEASE_POLICY.md` rather than `docs/superpowers/`.

- [ ] **Step 4: Run GREEN test**

Run `python -m unittest tests.test_governance_requirements -v`.
Expected: pass.

- [ ] **Step 5: Commit Task 2**

```bash
git add docs/PLUGIN_STANDARD.md docs/PLUGIN_STANDARD.en.md tests/test_governance_requirements.py
git commit -m "docs: make plugin requirements traceable"
```

---

### Task 3: Review evidence, security policy, and non-normative implementation specs

**Files:**
- Create: `docs/reviews/README.md`
- Create: `docs/reviews/README.en.md`
- Create: `docs/reviews/2026-09-05-opus-codex-governance.md`
- Create: `docs/reviews/2026-09-05-opus-codex-governance.en.md`
- Create: `SECURITY.md`
- Create: `SECURITY.en.md`
- Modify: `docs/REVIEW_FIRST_RELEASE.md`
- Modify: `docs/REVIEW_FIRST_RELEASE.en.md`
- Modify: `README.md`
- Modify: `README.en.md`
- Create: `tests/test_governance_artifacts.py`

**Interfaces:**
- Produces bilingual governance artifacts with reciprocal language links.
- `docs/superpowers/` is described only as historical implementation context.

- [ ] **Step 1: Write RED governance-artifact tests**

Create `tests/test_governance_artifacts.py` asserting all six new files exist; RU/EN pairs link to each other; root READMEs contain `docs/reviews/README`; both `REVIEW_FIRST_RELEASE` files contain `historical implementation` or the RU equivalent `историческ` plus `docs/superpowers/`; SECURITY files contain `approval`, `secret`, `prompt`, `immutable`, `private`, and a warning against public sensitive disclosure; review artifact contains PR `#56`, reviewed head `130050f11b2612a01ca6909215dbf30952a89d45`, candidate head `23a14d9b9e51825b96286bf6f9a8d4244d035ebe`, main `88d2f45e63308a476cbe456402bf17dc847436cb`, CI `33953946792`, post-merge CI `33954164035`, publisher `33954198278`, and wording that the Codex exact-head re-review was unavailable due to quota.

- [ ] **Step 2: Run RED test**

Run `python -m unittest tests.test_governance_artifacts -v`.
Expected: failures for missing artifacts/current wording.

- [ ] **Step 3: Add review index and dated RU/EN artifact**

Record only repository-supported facts: Opus governance findings, PR #56 Codex P1/P1/P2 findings, their RED→GREEN evidence, exact SHAs/run IDs, and the quota limitation. State explicitly that AI review is advisory semantic input, CI is mechanical evidence, and human authorization owns merge/release.

- [ ] **Step 4: Add RU/EN SECURITY policy**

Document current-line support, secret exposure, approval bypass, prompt-injection/data-as-instructions violations, cross-service credential/transport ownership, immutable release/tag failures, supply-chain risks, private reporting preference, public-issue redaction rule, and no SLA/bounty/email guarantees.

- [ ] **Step 5: Reclassify `docs/superpowers/` in review guidance and README navigation**

Change `REVIEW_FIRST_RELEASE` RU/EN so `docs/superpowers/` is historical implementation context, not production authority. Link the review index/latest artifact from root RU/EN README documentation navigation.

- [ ] **Step 6: Run GREEN governance-artifact tests**

Run `python -m unittest tests.test_governance_artifacts -v`.
Expected: pass.

- [ ] **Step 7: Commit Task 3**

```bash
git add SECURITY.md SECURITY.en.md README.md README.en.md docs/REVIEW_FIRST_RELEASE.md docs/REVIEW_FIRST_RELEASE.en.md docs/reviews tests/test_governance_artifacts.py
git commit -m "docs: add review and security governance artifacts"
```

---

### Task 4: Repository-only `1.0.7` release surfaces

**Files:**
- Modify: `.github/releases/release.json`
- Create: `.github/releases/1.0.7.md`
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `CHANGELOG.md`
- Modify: `CHANGELOG.en.md`
- Modify: `tests/test_documentation_ux_contracts.py`
- Create: `tests/test_repository_1_0_7_release_surfaces.py`

**Interfaces:**
- Produces manifest repository `version/tag = 1.0.7`, title `Repository 1.0.7`, notes `.github/releases/1.0.7.md`, `plugins: []`.

- [ ] **Step 1: Write RED `1.0.7` release-surface tests**

Create `tests/test_repository_1_0_7_release_surfaces.py` asserting `release-1.0.7` in both root READMEs; `## [1.0.7] — 2026-09-05` in both changelogs; release manifest repository version/tag/title/notes point to `1.0.7`; `plugins == []`; and all seven plugin manifest versions remain the fixed values in Global Constraints. Update `test_documentation_ux_contracts.py` from repository `1.0.6` marker expectations to `1.0.7` while keeping plugin expectations unchanged.

- [ ] **Step 2: Run RED tests**

Run:

```bash
python -m unittest tests.test_repository_1_0_7_release_surfaces tests.test_documentation_ux_contracts -v
```

Expected: failures only for stale repository release surfaces.

- [ ] **Step 3: Advance declarative release declaration and docs**

Set `.github/releases/release.json` to repository `1.0.7`, add notes describing function-level traceability/governance/security/review artifacts, keep `plugins: []`, update README badges/markers, and add matching RU/EN changelog entries without changing plugin files.

- [ ] **Step 4: Run GREEN release-surface tests and full root verification**

Run:

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

Expected: validator exits 0 and full root suite passes.

- [ ] **Step 5: Commit Task 4**

```bash
git add .github/releases/release.json .github/releases/1.0.7.md README.md README.en.md CHANGELOG.md CHANGELOG.en.md tests/test_documentation_ux_contracts.py tests/test_repository_1_0_7_release_surfaces.py
git commit -m "release: stage repository 1.0.7"
```

---

### Task 5: PR, exact-head CI/review, merge, and immutable release verification

**Files:**
- No product/runtime files beyond Tasks 1-4.
- PR body records all RED→GREEN run IDs and reviewer disposition.

**Interfaces:**
- Consumes: final branch head with Tasks 1-4 complete.
- Produces: squash-merged `main` plus immutable GitHub release/tag `1.0.7` on the exact merge SHA.

- [ ] **Step 1: Open draft PR C**

Use title `governance: harden contract traceability and review evidence` and document explicit non-goals, plugin versions, and TDD evidence.

- [ ] **Step 2: Require exact-head CI**

Verify all 10 CI jobs succeed on the final PR head: two root validator/test jobs, affected-plugin detection, and seven plugin jobs.

- [ ] **Step 3: Request independent Codex review**

Ask Codex to focus on AST selector correctness/skip handling, matrix migration accuracy, governance claims/evidence honesty, security-reporting wording, non-normative `docs/superpowers/`, release-only scope, and plugin-version preservation. If quota/tool limitation recurs, record it explicitly and do not call the review clean.

- [ ] **Step 4: Resolve review findings through separate RED→GREEN cycles**

For every actionable finding, add a failing regression first, capture RED CI, apply the minimal fix, require exact-head GREEN CI, reply with evidence, and resolve the review thread.

- [ ] **Step 5: Pre-merge immutable-history checks**

Confirm `1.0.7` release/tag do not yet exist. Confirm release `1.0.6` remains immutable and tag `1.0.6` points to `88d2f45e63308a476cbe456402bf17dc847436cb`. Confirm PR diff contains no plugin runtime or plugin manifest/changelog version changes.

- [ ] **Step 6: Squash merge with exact-head guard**

Merge only the verified candidate SHA into `main` using squash. Record the resulting merge SHA and verify the `main` ref equals it.

- [ ] **Step 7: Verify post-merge CI and publisher**

Require post-merge CI success on the exact merge SHA. Verify the only release publisher run is `Publish current declared release` and it succeeds.

- [ ] **Step 8: Verify immutable `1.0.7` and historical preservation**

Confirm release `1.0.7` has `draft=false`, `prerelease=false`, `immutable=true`, `target_commitish=<merge SHA>`, and tag `1.0.7` points exactly to the same SHA. Recheck `1.0.6` is still immutable on `88d2f45e63308a476cbe456402bf17dc847436cb`. Re-read all seven plugin manifests and verify the versions from Global Constraints are unchanged.
