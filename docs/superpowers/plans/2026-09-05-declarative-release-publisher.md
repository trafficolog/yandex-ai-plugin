# Declarative Release Publisher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace all release-specific active GitHub Actions publishers with one manifest-driven hardened publisher and ship the migration as repository-only `1.0.6` without changing plugin SemVer or historical releases/tags.

**Architecture:** A repository-owned Python helper validates `.github/releases/release.json` and exposes a stable release-item representation. One `.github/workflows/publish-current-release.yml` consumes that declaration after successful exact-main CI and applies the hardened immutable/draft-recovery/rollback algorithm currently proven by the `1.0.5` publisher. Historical `publish-*.yml` files and tests that only pin their source are removed from current `main`; continuing safety assertions are migrated into generic tests.

**Tech Stack:** Python 3.10+, `unittest`, JSON, Bash, GitHub Actions, GitHub CLI (`gh`), Git.

**Spec:** `docs/superpowers/specs/2026-09-05-declarative-release-publisher-design.md`

## Global Constraints

- Base is `main` at repository `1.0.5`; target repository release is `1.0.6`.
- Plugin versions stay exactly: Direct `2.0.1`, Metrika `2.0.0`, Webmaster `2.0.0`, Wordstat `1.1.2`, Search `1.0.2`, SEO `1.1.2`, Marketing `1.1.0`.
- PR B creates no plugin tags.
- Existing GitHub releases/tags are never deleted, retargeted, recreated, or otherwise mutated.
- Exactly one automatic `publish-*.yml` remains in current-tip `.github/workflows/`: `publish-current-release.yml`.
- Publisher remains gated by successful canonical-repository `CI` from `push` to `main`, checked out at exact upstream `head_sha`.
- Remote tag probes fail closed; probe errors are not treated as absence.
- Draft recovery requires one common ancestor target for the entire declared release set.
- Rollback is armed only during the mutable publication window, re-checks `isImmutable` before deletion, and is disarmed immediately after immutability is confirmed.
- Every new release set requires a new repository SemVer/tag; an already immutable repository release is never reused for a later plugin release set.
- No workflow commits release state back to the repository.

---

### Task 1: Declarative release manifest contract

**Files:**
- Create: `scripts/release_manifest.py`
- Create: `tests/test_release_manifest.py`
- Create: `.github/releases/release.json`
- Create: `.github/releases/1.0.6.md`

**Interfaces:**
- Produces `ReleaseItem(kind: str, name: str, version: str, tag: str, title: str, notes_file: str)` as an immutable dataclass.
- Produces `load_release_manifest(root: Path, manifest_path: Path | None = None) -> dict`.
- Produces `validate_release_manifest(root: Path, manifest_path: Path | None = None) -> list[str]` where an empty list means valid.
- Produces `release_items(root: Path, manifest_path: Path | None = None) -> list[ReleaseItem]`, repository item first, then plugins in manifest order; raises `ValueError` when validation fails.
- CLI: `python scripts/release_manifest.py validate [--root PATH] [--manifest PATH]` exits 0 for valid, 1 and prints one error per line for invalid.
- CLI: `python scripts/release_manifest.py items [--root PATH] [--manifest PATH] --format tsv` prints six tab-separated fields matching `ReleaseItem` in stable order.

- [ ] **Step 1: Write RED manifest tests**

Create `tests/test_release_manifest.py` covering:

```python
from pathlib import Path
import json
import tempfile
import unittest

from scripts.release_manifest import release_items, validate_release_manifest


class ReleaseManifestTests(unittest.TestCase):
    def test_repository_only_1_0_6_manifest_is_valid(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(validate_release_manifest(root), [])
        items = release_items(root)
        self.assertEqual([(item.kind, item.tag) for item in items], [("repository", "1.0.6")])

    def test_repository_tag_must_equal_strict_semver_version(self):
        # temporary fixture writes version 1.0.6 and tag repository-1.0.6
        # expected error contains "repository tag must equal version"
        ...

    def test_notes_must_stay_under_github_releases_and_exist(self):
        # reject ../notes.md and missing .github/releases file
        ...

    def test_plugin_entry_must_match_existing_plugin_and_manifest_version(self):
        # reject unknown plugin and mismatched version
        ...

    def test_plugin_tag_is_canonical_and_unique(self):
        # require yandex-<service>-v<version>; reject duplicate plugin/tag
        ...

    def test_release_tags_are_unique_across_repository_and_plugins(self):
        ...
```

Use fixture helper functions in the same test file rather than weakening production repository validation.

- [ ] **Step 2: Commit and run RED**

Commit only the tests first. CI/root test expectation: failures because `scripts.release_manifest`, `release.json`, and release notes do not exist yet; existing validator remains green.

- [ ] **Step 3: Implement the minimal manifest helper**

`scripts/release_manifest.py` must:

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

Validate schema version `1`, required scalar fields, path confinement using resolved paths, repository tag/version equality, existing plugin directory, both `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` version equality for declared plugins, canonical plugin tag, and uniqueness.

- [ ] **Step 4: Add repository-only declaration**

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

`.github/releases/1.0.6.md` states that the release migrates to one declarative publisher, retires active historical publishers, preserves immutable history, and leaves all seven plugin versions unchanged.

- [ ] **Step 5: Run GREEN**

Run through CI/root suite and require all manifest tests green on Python 3.10 and 3.13.

- [ ] **Step 6: Commit manifest implementation**

Commit helper + manifest + notes without any legacy workflow deletion yet.

---

### Task 2: Generic publisher safety contract

**Files:**
- Create: `tests/test_current_release_publisher.py`
- Create: `.github/workflows/publish-current-release.yml`
- Read/migrate behavior from: `.github/workflows/publish-repository-1.0.5.yml`

**Interfaces:**
- Consumes `python scripts/release_manifest.py validate` and `items --format tsv` from Task 1.
- Consumes `.github/releases/release.json` and declared notes files from Task 1.
- Produces one automatic workflow named `Publish current declared release`.

- [ ] **Step 1: Write RED generic publisher tests**

`tests/test_current_release_publisher.py` parses workflow text and asserts stable safety tokens/order rather than exact prose. Required tests:

```python
def test_trigger_is_successful_canonical_main_ci_only(): ...
def test_checkout_is_exact_target_sha(): ...
def test_publisher_validates_manifest_before_remote_mutation(): ...
def test_stale_initial_main_is_no_publish(): ...
def test_existing_release_targets_must_form_one_common_ancestor(): ...
def test_remote_tag_probe_fails_closed(): ...
def test_draft_reservation_precedes_publication(): ...
def test_mutable_published_release_is_rejected(): ...
def test_standalone_tag_is_rejected(): ...
def test_rollback_checks_is_immutable_before_delete(): ...
def test_rollback_is_disarmed_before_post_immutability_probes(): ...
def test_final_verification_checks_every_declared_item(): ...
def test_empty_plugins_manifest_cannot_publish_plugin_tags(): ...
def test_concurrency_serializes_without_cancellation(): ...
```

Pin ordering by comparing string indexes for `published_is_immutable`, `rollback_armed=false`, `trap - ERR`, and the first subsequent `git fetch origin "refs/tags/$tag`.

- [ ] **Step 2: Commit and observe RED**

CI should fail only the new generic workflow contract because `.github/workflows/publish-current-release.yml` does not exist yet.

- [ ] **Step 3: Implement generic workflow from hardened `1.0.5` semantics**

Workflow structure:

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

The job `if:` must require canonical repository, upstream success, `push`, same head repository, and `main` branch. `TARGET_SHA` is `${{ github.event.workflow_run.head_sha }}` and checkout uses `ref: ${{ env.TARGET_SHA }}`.

Algorithm steps:

1. Validate release manifest locally before state mutation.
2. Load all items into a stable TSV array from `scripts/release_manifest.py`.
3. Inspect each declared release and remote tag; collect candidate targets from immutable releases or drafts.
4. For no existing state, require `TARGET_SHA == origin/main`; if stale, emit verified no-op and do not publish.
5. For recovery/existing state, require all candidate targets equal and common target ancestor of live main.
6. Validate exact selected release target in a detached worktree with `scripts/validate_repo.py`, root unit tests, and manifest validation against that target.
7. Reconcile each declared item using a reusable Bash `publish_one` with the hardened `rollback_armed` window.
8. Final verification loops over all declared items and requires published + immutable + exact/common tag target.

Do not hardcode the seven plugin versions in this workflow. Plugin versions are checked by the manifest helper only for plugins declared for publication.

- [ ] **Step 4: Run GREEN generic publisher contract**

Require all new publisher safety tests green while historical workflows still exist.

- [ ] **Step 5: Commit generic publisher**

Commit only generic workflow changes after RED evidence is recorded.

---

### Task 3: Retire historical active publishers and migrate tests

**Files:**
- Delete every release-specific `.github/workflows/publish-*.yml` except `publish-current-release.yml`, including:
  - `.github/workflows/publish-docs-1.0.0.yml`
  - `.github/workflows/publish-fable-2.0.0.yml`
  - `.github/workflows/publish-fable-audit3-maintenance.yml`
  - `.github/workflows/publish-fable-review5-maintenance.yml`
  - `.github/workflows/publish-opus-1.1.0.yml`
  - `.github/workflows/publish-opus-1.1.1.yml`
  - `.github/workflows/publish-opus-1.1.2.yml`
  - `.github/workflows/publish-opus-1.1.3.yml`
  - `.github/workflows/publish-phase-7-topical-architecture.yml`
  - `.github/workflows/publish-phase-7-topical-architecture-1.0.1.yml`
  - `.github/workflows/publish-repository-1.0.2.yml`
  - `.github/workflows/publish-repository-1.0.5.yml`
- Delete/rewrite historical workflow-source tests whose only subject is one removed YAML, including publisher-specific FABLE/OPUS/Phase7/repository publisher suites.
- Modify: `tests/test_publisher_repository_identity.py`
- Create: `tests/test_publisher_migration_contract.py`

**Interfaces:**
- Current-tip workflow set becomes an invariant: exactly one filename matching `publish-*.yml`, `publish-current-release.yml`.
- Historical workflow source remains available only through Git history/tags, not duplicated into an archive directory.

- [ ] **Step 1: Write RED migration contract before deleting anything**

`tests/test_publisher_migration_contract.py`:

```python
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github/workflows"

class PublisherMigrationContractTests(unittest.TestCase):
    def test_exactly_one_active_publish_workflow_exists(self):
        publishers = sorted(path.name for path in WORKFLOWS.glob("publish-*.yml"))
        self.assertEqual(publishers, ["publish-current-release.yml"])

    def test_historical_codenames_are_not_active_publish_workflows(self):
        names = "\n".join(path.name.lower() for path in WORKFLOWS.glob("publish-*.yml"))
        for token in ("opus", "fable", "phase", "docs", "1.0.2", "1.0.5"):
            self.assertNotIn(token, names)
```

- [ ] **Step 2: Observe RED**

Expect only migration assertions to fail because historical publisher workflows are still present.

- [ ] **Step 3: Inventory continuing safety assertions**

Before deleting old tests, inspect every publisher-specific test and map each continuing invariant to either `tests/test_current_release_publisher.py`, `tests/test_release_manifest.py`, or `tests/test_publisher_migration_contract.py`. At minimum retain: repository identity, exact checkout, idempotent immutable no-op, common-target recovery, draft recovery, remote probe failure distinction, ERR trace/rollback arm, cleanup residue checks, and post-immutability rollback disarm.

- [ ] **Step 4: Delete historical workflows and source-pinning tests**

Delete only tests that cannot have continuing value after the workflow is intentionally absent. If a test contains a reusable safety invariant, migrate that assertion first, then delete the historical test file.

Update `tests/test_publisher_repository_identity.py` to inspect only `publish-current-release.yml` and require canonical `GH_REPO`/repository identity semantics there.

- [ ] **Step 5: Run full repository GREEN**

Require `python scripts/validate_repo.py` and `python -m unittest discover -s tests -v` to pass. No test may require a deleted historical workflow on current tip.

- [ ] **Step 6: Commit retirement migration**

Commit workflow deletions and test migration as one independently reviewable change.

---

### Task 4: Document the new policy and stage repository `1.0.6`

**Files:**
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `CHANGELOG.md`
- Modify: `CHANGELOG.en.md`
- Modify: `docs/RELEASE_POLICY.md`
- Modify: `docs/RELEASE_POLICY.en.md`
- Modify: `CONTRIBUTING.md` only if its release procedure references per-release workflows.
- Modify: `tests/test_documentation_ux_contracts.py` if current repository release badge assertions are pinned to `1.0.5`.
- Create or modify generic documentation/release tests as needed; do not revive historical publisher tests.

**Interfaces:**
- Current repository version becomes `1.0.6` in root RU/EN release surfaces.
- Release policy describes manifest-driven release sets and historical workflow retirement.

- [ ] **Step 1: Write/update RED release-surface assertions**

Tests require:

```python
assert "release-1.0.6" in README_RU
assert "release-1.0.6" in README_EN
assert "## [1.0.6]" in CHANGELOG_RU
assert "## [1.0.6]" in CHANGELOG_EN
```

and release policy RU/EN must mention `.github/releases/release.json`, one active generic publisher, immutable Git history as the historical publisher archive, and the rule that every new release set receives a new repository SemVer.

- [ ] **Step 2: Observe RED**

Expected failures should be limited to current `1.0.5` release surfaces/policy wording.

- [ ] **Step 3: Update RU/EN docs and changelog**

Add `## [1.0.6] — 2026-09-05` to both changelogs with equivalent SemVer/release content. Update README badge/current repository release to `1.0.6` without changing the seven plugin versions.

Release policy must explicitly say:

- future release intent is declared in `.github/releases/release.json`;
- `publish-current-release.yml` is the only automatic publisher at current tip;
- historical publisher YAML is removed from active default-branch workflows once immutable and remains recoverable from Git history/tags;
- a new release set always increments repository SemVer, even when only a plugin is being released;
- `plugins: []` is repository-only and produces no plugin tags.

- [ ] **Step 4: Run bilingual/contract GREEN**

Require root validator + all repository tests green on exact branch head.

- [ ] **Step 5: Commit repository `1.0.6` surfaces**

Commit docs/version surfaces separately from publisher mechanics.

---

### Task 5: Exact-head review, merge, and immutable `1.0.6` publication

**Files:**
- No new implementation files unless review finds a defect.
- PR metadata for branch `refactor/declarative-release-publisher`.

**Interfaces:**
- Produces squash-merged `main` SHA.
- Produces immutable repository release/tag `1.0.6` at exactly that SHA.
- Must not produce any new plugin tags.

- [ ] **Step 1: Open/update draft PR**

PR title: `refactor: consolidate release publishing into one declarative workflow`.

Body states scope, explicit non-goals, spec, plan, plugin versions unchanged, repository-only `1.0.6`, and immutable-history guarantee.

- [ ] **Step 2: Verify exact-head CI**

Require all root matrix and affected plugin jobs green on one exact head SHA. Record run ID and job count.

- [ ] **Step 3: Request independent exact-head review**

Ask Codex review on the exact green SHA. Fix blocker findings via their own RED -> GREEN regression before re-requesting review. If review is unavailable due an explicit quota/tool limitation, document that limitation rather than claiming a clean review.

- [ ] **Step 4: Final scope guard**

Confirm changed files contain no plugin runtime/helper/manifest version changes and no historical tag/release mutation. Confirm `.github/workflows/` contains exactly one `publish-*.yml` at branch head.

- [ ] **Step 5: Squash merge with expected-head guard**

Merge only when PR is mergeable, unresolved blocker threads are zero, exact-head CI is green, and head SHA has not moved.

- [ ] **Step 6: Verify post-merge CI at exact main SHA**

Require post-merge `CI` success on the squash SHA. Confirm legacy publishers do not appear as new runs for that SHA; the only release publisher should be `Publish current declared release`.

- [ ] **Step 7: Verify generic publisher run**

Require its run to target the same squash SHA and complete successfully. Inspect job steps for manifest validation, release-state detection, exact-target validation, publication, and final immutable-set verification.

- [ ] **Step 8: Verify GitHub release state directly**

Check release/tag `1.0.6`: release exists, draft=false, prerelease=false, immutable=true, target/tag SHA equals exact squash `main` SHA.

Re-check release/tag `1.0.5`: release ID/target remains unchanged and immutable. Verify no plugin service tag version advanced.

- [ ] **Step 9: Report final evidence**

Report final branch head, PR number, exact-head CI run, review outcome, squash SHA, post-merge CI run, generic publisher run, `1.0.6` release ID/immutable state/tag SHA, unchanged `1.0.5`, unchanged plugin versions, and absence of legacy publisher runs on the new main SHA.
