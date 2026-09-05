# Declarative Release Publisher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace all release-specific active GitHub Actions publishers with one manifest-driven hardened publisher and ship the migration as repository-only `1.0.6` without changing plugin SemVer or historical releases/tags.

**Architecture:** `scripts/release_manifest.py` owns validation and normalization of `.github/releases/release.json`. `.github/workflows/publish-current-release.yml` owns one reusable exact-main publication algorithm derived from the hardened `1.0.5` publisher. Historical `publish-*.yml` files disappear from current tip after their safety assertions have been migrated into generic tests; Git history/tags remain the immutable archive.

**Tech Stack:** Python 3.10+, `unittest`, JSON, Bash, GitHub Actions, GitHub CLI (`gh`), Git.

**Spec:** `docs/superpowers/specs/2026-09-05-declarative-release-publisher-design.md`

## Global Constraints

- Base is repository `1.0.5`; target repository release is `1.0.6`.
- Plugin versions remain exactly: Direct `2.0.1`, Metrika `2.0.0`, Webmaster `2.0.0`, Wordstat `1.1.2`, Search `1.0.2`, SEO `1.1.2`, Marketing `1.1.0`.
- PR B creates no plugin tags.
- Existing GitHub releases/tags are never deleted, retargeted, recreated, or mutated.
- Current tip ends with exactly one automatic `publish-*.yml`: `.github/workflows/publish-current-release.yml`.
- Publisher is gated by successful canonical-repository `CI` from `push` to `main`, checked out at exact upstream `head_sha`.
- Remote tag probes fail closed; transport/auth/probe errors are not interpreted as absence.
- Draft recovery requires one common ancestor target for the whole declared release set.
- Rollback is armed only during the mutable publication window, probes `isImmutable` before deletion, and is disarmed immediately after immutability is confirmed.
- Every new release set receives a new repository SemVer/tag; an immutable repository release is never reused for a later plugin release set.
- No workflow commits state back into the repository.

---

### Task 1: Declarative release manifest contract

**Files:**
- Create: `scripts/release_manifest.py`
- Create: `tests/test_release_manifest.py`
- Create: `.github/releases/release.json`
- Create: `.github/releases/1.0.6.md`

**Interfaces:**
- `ReleaseItem(kind: str, name: str, version: str, tag: str, title: str, notes_file: str)` — frozen dataclass.
- `load_release_manifest(root: Path, manifest_path: Path | None = None) -> dict`.
- `validate_release_manifest(root: Path, manifest_path: Path | None = None) -> list[str]`.
- `release_items(root: Path, manifest_path: Path | None = None) -> list[ReleaseItem]`; repository first, then plugin entries in manifest order; raise `ValueError` if validation fails.
- CLI `python scripts/release_manifest.py validate [--root PATH] [--manifest PATH]` — exit 0 when valid, 1 when invalid.
- CLI `python scripts/release_manifest.py items [--root PATH] [--manifest PATH] --format tsv` — six stable tab-separated fields in dataclass order.

- [ ] **Step 1: Write the failing manifest tests**

Create a temporary-fixture helper inside `tests/test_release_manifest.py` that writes `.github/releases/release.json`, notes files, and minimal plugin manifests. Then add these executable assertions:

```python
class ReleaseManifestTests(unittest.TestCase):
    def test_repository_only_1_0_6_manifest_is_valid(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(validate_release_manifest(root), [])
        self.assertEqual(
            [(item.kind, item.name, item.version, item.tag) for item in release_items(root)],
            [("repository", "repository", "1.0.6", "1.0.6")],
        )

    def test_repository_tag_must_equal_version(self):
        root = self.make_fixture(repository_version="1.0.6", repository_tag="repository-1.0.6")
        self.assertTrue(any("repository tag must equal version" in e for e in validate_release_manifest(root)))

    def test_repository_version_must_be_strict_semver(self):
        root = self.make_fixture(repository_version="release-1", repository_tag="release-1")
        self.assertTrue(any("strict SemVer" in e for e in validate_release_manifest(root)))

    def test_notes_path_must_be_confined_and_exist(self):
        root = self.make_fixture(notes_file="../notes.md")
        self.assertTrue(any(".github/releases" in e for e in validate_release_manifest(root)))
        root = self.make_fixture(notes_file=".github/releases/missing.md", create_notes=False)
        self.assertTrue(any("notes file does not exist" in e for e in validate_release_manifest(root)))

    def test_declared_plugin_must_exist_and_match_both_manifest_versions(self):
        root = self.make_fixture(plugin="yandex-wordstat", plugin_version="1.2.0", actual_plugin_version="1.1.2")
        errors = validate_release_manifest(root)
        self.assertTrue(any("yandex-wordstat" in e and "1.1.2" in e and "1.2.0" in e for e in errors))

    def test_plugin_tag_must_be_canonical(self):
        root = self.make_fixture(plugin="yandex-wordstat", plugin_version="1.1.2", plugin_tag="wordstat-1.1.2")
        self.assertTrue(any("yandex-wordstat-v1.1.2" in e for e in validate_release_manifest(root)))

    def test_plugins_and_tags_must_be_unique(self):
        root = self.make_fixture(duplicate_plugin=True)
        errors = validate_release_manifest(root)
        self.assertTrue(any("duplicate plugin" in e for e in errors))
        self.assertTrue(any("duplicate release tag" in e for e in errors))
```

The fixture helper returns `Path(tmp.name)` and retains each `TemporaryDirectory` with `self.addCleanup(tmp.cleanup)`.

- [ ] **Step 2: Commit RED and collect CI evidence**

Commit only `tests/test_release_manifest.py`. Expected root failure is import/file-contract failure for the new helper/manifest; existing repository validator must still pass.

- [ ] **Step 3: Implement the manifest helper**

Start `scripts/release_manifest.py` with:

```python
from dataclasses import dataclass
import argparse
import json
from pathlib import Path
import re

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
DEFAULT_MANIFEST = Path(".github/releases/release.json")

@dataclass(frozen=True)
class ReleaseItem:
    kind: str
    name: str
    version: str
    tag: str
    title: str
    notes_file: str
```

Validation rules are exact: schema `1`; `repository` object and `plugins` list required; all release scalar fields non-empty strings; repository strict SemVer and `tag == version`; notes resolve under `<root>/.github/releases` and exist with `.md` suffix; plugin directory exists; both Codex/Claude plugin manifests parse and equal declared version; plugin tag equals `<plugin>-v<version>`; plugin names unique; all release tags unique.

`release_items()` first calls validation and raises `ValueError("; ".join(errors))` if non-empty.

CLI parser has subcommands `validate` and `items`. `validate` writes errors to stderr and returns 1. `items --format tsv` writes `kind`, `name`, `version`, `tag`, `title`, `notes_file` separated by tabs.

- [ ] **Step 4: Add the repository-only `1.0.6` declaration**

`.github/releases/release.json`:

```json
{
  "schema_version": 1,
  "repository": {
    "version": "1.0.6",
    "tag": "1.0.6",
    "title": "Repository 1.0.6",
    "notes_file": ".github/releases/1.0.6.md"
  },
  "plugins": []
}
```

`.github/releases/1.0.6.md` says this release consolidates publication into one manifest-driven workflow, retires historical active publishers from current tip while preserving them in Git history, preserves hardened immutable/rollback behavior, and leaves all seven plugin versions unchanged.

- [ ] **Step 5: Run GREEN and commit**

Require root tests green on Python 3.10/3.13 for manifest tests. Commit helper + manifest + notes separately from the RED test commit.

---

### Task 2: Generic publisher safety contract

**Files:**
- Create: `tests/test_current_release_publisher.py`
- Create: `.github/workflows/publish-current-release.yml`
- Source behavior: `.github/workflows/publish-repository-1.0.5.yml`

**Interfaces:**
- Consumes Task 1 `validate` and `items --format tsv` CLI.
- Produces one workflow named `Publish current declared release`.

- [ ] **Step 1: Write RED workflow tests**

The test module loads `WORKFLOW.read_text()` and uses token assertions plus order checks:

```python
class CurrentReleasePublisherTests(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""

    def test_trigger_is_successful_canonical_main_ci_only(self):
        for token in ('workflows: ["CI"]', "conclusion == 'success'", "workflow_run.event == 'push'", "head_branch == 'main'", "head_repository.full_name == github.repository"):
            self.assertIn(token, self.text)

    def test_checkout_is_exact_target_sha(self):
        self.assertIn("TARGET_SHA: ${{ github.event.workflow_run.head_sha }}", self.text)
        self.assertIn("ref: ${{ env.TARGET_SHA }}", self.text)

    def test_manifest_is_validated_before_release_mutation(self):
        validate_i = self.text.index("python scripts/release_manifest.py validate")
        create_i = self.text.index("gh release create")
        self.assertLess(validate_i, create_i)

    def test_remote_tag_probe_fails_closed(self):
        self.assertIn("git ls-remote --exit-code", self.text)
        self.assertIn("2) return 1", self.text)
        self.assertIn("Unable to determine remote tag state", self.text)

    def test_rollback_rechecks_immutability_before_delete(self):
        probe_i = self.text.index('cleanup_release_immutable="$(gh release view')
        delete_i = self.text.index('gh release delete "$tag"')
        self.assertLess(probe_i, delete_i)
        self.assertIn("already immutable; rollback is neither required nor safe", self.text)

    def test_rollback_is_disarmed_before_post_immutability_tag_probe(self):
        immutable_i = self.text.index('[[ "$published_is_immutable" == "true" ]]')
        disarm_i = self.text.index("rollback_armed=false", immutable_i)
        trap_i = self.text.index("trap - ERR", disarm_i)
        fetch_i = self.text.index('git fetch origin "refs/tags/$tag:refs/tags/$tag"', trap_i)
        self.assertLess(immutable_i, disarm_i)
        self.assertLess(disarm_i, trap_i)
        self.assertLess(trap_i, fetch_i)

    def test_repository_only_manifest_does_not_hardcode_plugin_publish_calls(self):
        self.assertNotIn('publish_one "yandex-', self.text)
        self.assertIn("release_manifest.py items", self.text)

    def test_concurrency_serializes_without_cancel(self):
        self.assertIn("group: current-release-publisher", self.text)
        self.assertIn("cancel-in-progress: false", self.text)
```

Add explicit assertions for stale initial run -> no publication, common candidate target equality, ancestor recovery, mutable published release hard fail, standalone tag hard fail, draft reservation before publish, and final verification loop over every item.

- [ ] **Step 2: Commit RED and collect CI evidence**

Commit only the new generic workflow test. Expected failures are all attributable to missing `publish-current-release.yml`.

- [ ] **Step 3: Implement the generic workflow**

Required header:

```yaml
name: Publish current declared release

on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]

permissions:
  contents: write

concurrency:
  group: current-release-publisher
  cancel-in-progress: false
```

The job condition requires canonical repo, upstream success, push event, same head repo, and main branch. Checkout uses exact `TARGET_SHA`.

Implementation sequence is fixed:

1. Run `python scripts/release_manifest.py validate` before any remote release mutation.
2. Read normalized release items via `items --format tsv`.
3. Inspect every declared release and remote tag, collecting immutable/draft target candidates.
4. Fetch `origin/main` and determine live main.
5. No candidate state: if `TARGET_SHA != live_main`, mark `stale=true`, `complete=false`, and skip validation/publication as a verified stale no-op; otherwise target is `TARGET_SHA`.
6. Candidate state: every candidate must equal the first; target must be an ancestor of live main; otherwise fail closed.
7. `complete=true` only if every declared item is already published immutable with no drafts and all tags match the common target.
8. For incomplete non-stale state, detached worktree at common target runs manifest validation, `scripts/validate_repo.py`, and root `unittest` discovery.
9. `publish_one` reserves absent releases as drafts, checks exact draft target/no tag, arms rollback, publishes, reads back draft/immutable/target, rolls back only while mutable, disarms immediately after immutability, then verifies remote tag SHA.
10. Final verification loops over normalized items and proves published, non-draft, immutable, target/common SHA valid, and tag exact.

Use `set -Eeuo pipefail` in publication code so ERR traps propagate through functions. Preserve the hardened `1.0.5` `remote_tag_exists()` distinction: rc 0 present, rc 2 absent, other rc fatal.

- [ ] **Step 4: Run GREEN and commit**

Generic publisher tests must all pass while legacy workflows still exist. Commit the workflow only after RED evidence is recorded.

---

### Task 3: Retire historical publishers and migrate continuing tests

**Files:**
- Create: `tests/test_publisher_migration_contract.py`
- Modify: `tests/test_publisher_repository_identity.py`
- Delete all release-specific `.github/workflows/publish-*.yml` except `publish-current-release.yml`.
- Delete/rewrite publisher-specific tests that only pin removed YAML after their continuing safety assertions are migrated.

**Historical workflows to remove from current tip:**

```text
publish-docs-1.0.0.yml
publish-fable-2.0.0.yml
publish-fable-audit3-maintenance.yml
publish-fable-review5-maintenance.yml
publish-opus-1.1.0.yml
publish-opus-1.1.1.yml
publish-opus-1.1.2.yml
publish-opus-1.1.3.yml
publish-phase-7-topical-architecture.yml
publish-phase-7-topical-architecture-1.0.1.yml
publish-repository-1.0.2.yml
publish-repository-1.0.5.yml
```

- [ ] **Step 1: Write RED migration assertions**

```python
ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github/workflows"

class PublisherMigrationContractTests(unittest.TestCase):
    def test_exactly_one_active_publish_workflow_exists(self):
        self.assertEqual(
            sorted(path.name for path in WORKFLOWS.glob("publish-*.yml")),
            ["publish-current-release.yml"],
        )

    def test_historical_publish_names_are_absent_from_current_tip(self):
        names = "\n".join(path.name.lower() for path in WORKFLOWS.glob("publish-*.yml"))
        for token in ("opus", "fable", "phase", "docs", "1.0.2", "1.0.5"):
            self.assertNotIn(token, names)
```

- [ ] **Step 2: Commit and observe RED**

Expected two failures because legacy workflows still exist. Generic publisher tests from Task 2 remain green.

- [ ] **Step 3: Inventory and migrate safety assertions before deletion**

Inspect these historical suites: FABLE audit/review publisher tests, OPUS 1.1.2/1.1.3 publisher + draft/residue/idempotency tests, Phase7 publisher/idempotency tests, repository 1.0.2/1.0.5 publisher tests, and publisher repository identity test.

Map continuing behavior into `test_current_release_publisher.py` or `test_publisher_migration_contract.py`. The following must survive: canonical repository identity; exact checkout; complete immutable no-op; common-target recovery; draft recovery; remote-probe rc distinction; `set -E` ERR trace; rollback arm timing; cleanup residue verification; immutability-before-delete; post-immutability disarm; final exact-tag verification.

- [ ] **Step 4: Delete old workflow files and source-pinning tests**

After migration, remove all 12 historical workflow files. Remove historical test files whose subject no longer exists in current tip. Keep unrelated Phase7 functional contracts.

Rewrite `tests/test_publisher_repository_identity.py` to inspect only `.github/workflows/publish-current-release.yml` and assert canonical repository guard plus `GH_REPO`/`GITHUB_REPOSITORY` use rather than historical filenames.

- [ ] **Step 5: Run full GREEN and commit**

Require `python scripts/validate_repo.py` and `python -m unittest discover -s tests -v` green. Commit retirement/test migration together so no branch head lands with deleted safety tests but missing generic equivalents.

---

### Task 4: Stage repository `1.0.6` documentation/governance surfaces

**Files:**
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `CHANGELOG.md`
- Modify: `CHANGELOG.en.md`
- Modify: `docs/RELEASE_POLICY.md`
- Modify: `docs/RELEASE_POLICY.en.md`
- Modify: `CONTRIBUTING.md` only if it references release-specific workflow creation.
- Modify/add documentation contract tests as needed.

- [ ] **Step 1: Add RED current-release and policy tests**

Assertions must require:

```python
self.assertIn("release-1.0.6", read("README.md"))
self.assertIn("release-1.0.6", read("README.en.md"))
self.assertIn("## [1.0.6] — 2026-09-05", read("CHANGELOG.md"))
self.assertIn("## [1.0.6] — 2026-09-05", read("CHANGELOG.en.md"))
for policy in (read("docs/RELEASE_POLICY.md"), read("docs/RELEASE_POLICY.en.md")):
    self.assertIn(".github/releases/release.json", policy)
    self.assertIn("publish-current-release.yml", policy)
```

Also assert policy conveys: historical publisher YAML is removed from active default-branch workflows after immutable publication but remains in Git history/tags; every new release set increments repository SemVer; empty plugin list means no plugin tags.

- [ ] **Step 2: Commit and observe RED**

Expected failures are only `1.0.5` current surfaces and missing generic policy wording.

- [ ] **Step 3: Update RU/EN surfaces**

Add `## [1.0.6] — 2026-09-05` to both changelogs with parity. Update root release badge/current version to `1.0.6`. Do not alter the seven plugin versions.

Update release policy RU/EN with manifest-driven future releases, exactly one automatic current publisher, Git-history archival of historical workflow source, new repository SemVer for every release set, and `plugins: []` repository-only semantics.

- [ ] **Step 4: Run GREEN and commit**

Require bilingual validator and full root tests green. Commit docs/current release surfaces separately from publisher mechanics.

---

### Task 5: Exact-head CI, independent review, merge, and immutable `1.0.6`

**Files:** no implementation changes unless review finds a defect.

- [ ] **Step 1: Open draft PR**

Title: `refactor: consolidate release publishing into one declarative workflow`.

Body lists scope, non-goals, spec, plan, repository-only `1.0.6`, unchanged plugin versions, immutable-history guarantee, and RED/GREEN evidence.

- [ ] **Step 2: Require exact-head CI success**

Record exact branch SHA, CI run ID, and all job conclusions. Root matrices and affected plugin jobs must be green on the same SHA.

- [ ] **Step 3: Request independent exact-head Codex review**

Any blocker gets its own regression RED -> fix -> GREEN before thread resolution and re-review. If external review is explicitly unavailable because of quota/tool limitation, record the exception and do not label it clean review.

- [ ] **Step 4: Final scope guard**

Verify no plugin runtime/helper/plugin manifest version changes; `.github/workflows/` has exactly one `publish-*.yml`; `release.json` has repository `1.0.6` and empty plugins; unresolved blocker threads are zero.

- [ ] **Step 5: Squash merge with expected-head guard**

Merge only exact reviewed/verified head into `main`.

- [ ] **Step 6: Verify post-merge CI and workflow retirement**

Require successful `CI` on exact squash SHA. Query workflow runs for that SHA: historical OPUS/FABLE/PHASE/DOCS/release-specific publishers must not start; the only release publisher is `Publish current declared release`.

- [ ] **Step 7: Verify generic publication**

Publisher run must target exact squash SHA and complete manifest validation, release-state detection, exact-target validation, publication/recovery, and final immutable verification successfully.

- [ ] **Step 8: Verify release/tag state directly**

`1.0.6`: release exists, draft=false, prerelease=false, immutable=true; release target and tag SHA equal exact squash main SHA.

`1.0.5`: same release ID, immutable state, and target as before PR B. Service plugin tags/versions remain unchanged.

- [ ] **Step 9: Final evidence report**

Report PR, branch final SHA, exact-head CI, review outcome, squash SHA, post-merge CI, generic publisher run, `1.0.6` release ID/tag SHA/immutable state, `1.0.5` unchanged, plugin matrix unchanged, and zero historical publisher runs on the new main SHA.
