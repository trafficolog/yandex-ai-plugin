# Declarative Release Publisher — design

Date: 2026-09-05
Status: approved design, awaiting written-spec review
Base: `main` at `51550a6d9f55459077858271ed714df5b09a183c` (`Repository 1.0.5`)
Target repository release: `1.0.6`
Plugin SemVer: unchanged

## 1. Problem

The repository currently keeps one GitHub Actions publisher workflow per historical release or milestone. At the `1.0.5` main push, the successful `CI` run caused roughly ten completed historical `workflow_run` publishers to wake again, while the old `DOCS 1.0.0` publisher also ran from its `push` trigger. Those workflows mostly verified already-immutable history and exited successfully, but they still consume Actions runs, duplicate release-safety logic, complicate review, and make every future publisher fix a many-file concern.

The current tip of `main` contains twelve historical `publish-*.yml` workflows, including OPUS, FABLE, DOCS, Phase 7, repository `1.0.2`, and repository `1.0.5` publishers. Their historical source must remain recoverable, but keeping them active in the current default branch is not required for Git history: the exact files remain available through the commits/tags of their immutable releases.

The `1.0.5` publisher also demonstrated why duplication is risky: Codex found a P1 rollback window where a late error could attempt cleanup after a release had already become immutable. That defect was fixed in one workflow, but duplicated release engines create the recurring question of which historical/current copies carry equivalent safety semantics.

## 2. Goals

1. Keep exactly one active future release publisher in the default branch.
2. Separate release mechanics from the declaration of what should be released.
3. Preserve the hardened `1.0.5` safety properties for every future repository or plugin release.
4. Stop historical publishers from waking on future `main` pushes or successful CI runs.
5. Keep immutable historical tags/releases and their original workflow source untouched in Git history.
6. Make future releases update a small declarative release manifest instead of adding a new workflow file.
7. Replace workflow-specific regression suites with generic publisher/manifest contracts.
8. Ship the infrastructure change as repository-only `1.0.6`; do not change any plugin SemVer or create plugin tags.

## 3. Non-goals

- No mutation, deletion, recreation, or retargeting of existing GitHub releases/tags.
- No plugin runtime behavior changes.
- No plugin SemVer bumps in PR B.
- No rewrite or migration of historical commits/specs/changelogs.
- No generalized external release service or package registry.
- No self-modifying workflow that commits release state back to the repository.
- No automatic inference that every changed plugin needs a release; the human-approved manifest remains authoritative.
- No weakening of exact-head CI, immutable-release, fail-closed probe, draft-recovery, or rollback guarantees.

## 4. Chosen architecture

PR B replaces release-specific publishers with two current-tip artifacts:

- `.github/workflows/publish-current-release.yml` — the only active `publish-*` workflow;
- `.github/releases/release.json` — the declarative description of the release set to reconcile.

Release notes are stored as ordinary versioned Markdown files under `.github/releases/`, referenced by the manifest. For repository `1.0.6`, the notes file is `.github/releases/1.0.6.md`.

The workflow owns the release algorithm. The manifest owns the release intent. A future release changes `release.json` and its notes/changelog/version surfaces; it does not create another publisher workflow.

## 5. Release manifest contract

Schema version 1 uses this shape:

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

A future plugin release may add entries such as:

```json
{
  "plugin": "yandex-wordstat",
  "version": "1.2.0",
  "tag": "yandex-wordstat-v1.2.0",
  "title": "Yandex Wordstat 1.2.0",
  "notes_file": ".github/releases/yandex-wordstat-v1.2.0.md"
}
```

### Manifest invariants

- `schema_version` must equal `1`.
- A repository release declaration is always required; every new release set gets a new repository SemVer/tag even when only one plugin changes.
- Repository `version` must be strict SemVer and `tag` must equal that version.
- An already-immutable repository release declaration must never be reused to append/remove plugin release entries later; that is a new release set and requires the next repository SemVer.
- Repository notes file must be a repository-relative Markdown path under `.github/releases/` and must exist.
- Plugin identifiers must match an existing plugin directory and marketplace/plugin manifests.
- Plugin `version` must equal both owning plugin manifest versions at the release target (`.codex-plugin/plugin.json` and `.claude-plugin/plugin.json`).
- Plugin tag must be exactly `yandex-<service>-v<version>`.
- Plugin entries must be unique by plugin and tag.
- No release tag may appear twice across repository/plugin entries.
- `plugins: []` means a repository-only release.
- The manifest is human-authorized release intent; file-change detection must not silently add release entries.

This preserves independent plugin SemVer without permitting a release set to be extended after its repository record has become immutable.

A small repository-owned validator/helper should parse this contract so CI and the publisher use the same local interpretation instead of duplicating JSON parsing rules in shell.

## 6. Publisher trigger and ordering

`publish-current-release.yml` triggers only on `workflow_run` completion for `CI`.

The publish job is eligible only when all of these are true:

- repository is `trafficolog/yandex-ai-plugins-skills`;
- upstream workflow conclusion is `success`;
- upstream workflow event is `push`;
- upstream head repository is the canonical repository;
- upstream head branch is `main`.

`TARGET_SHA` is the successful CI run's `head_sha`. Checkout is detached at exactly `TARGET_SHA`, never implicit latest `main`.

A single repository-wide concurrency group serializes publisher executions with `cancel-in-progress: false`.

Before an initial publication, the workflow refreshes authoritative `origin/main`. If `TARGET_SHA` is no longer live `main` and there is no recoverable state for the declared release set, the run is a verified stale no-op rather than publishing an old release declaration. The newer successful-main CI run is responsible for the current manifest.

If recoverable draft state already exists at an ancestor commit, recovery may continue only when every existing candidate in the declared release set resolves to the same release target and that target remains an ancestor of live `main`.

Operationally, maintainers must not advance `release.json` to the next release until the currently declared release has been confirmed immutable. This keeps recovery intent explicit and avoids orphaning a draft under a different future manifest.

## 7. Release-state reconciliation

For every declared release item, the publisher classifies remote state before making changes.

### Absent release + absent remote tag

Safe initial state. The release may be reserved as a draft at the selected release target.

### Immutable published release + tag

Verified no-op state when the tag resolves to the recorded release target and that target is an ancestor of live `main`. A later main push with the same manifest therefore does not republish or fail merely because current `main` has advanced.

### Draft release without tag

Recoverable only when the draft has a concrete 40-hex target and all declared existing release items agree on the same target. The target must remain an ancestor of live `main`.

### Published but mutable release

Hard failure. The workflow must not normalize or overwrite an unexpectedly mutable published release.

### Standalone remote/local tag without GitHub Release

Hard failure. The workflow must not adopt or retarget an unexplained tag.

### Conflicting targets / partial inconsistent release set

Hard failure. Every existing item in one declared release set must point to one common release target.

Remote tag absence checks use fail-closed `git ls-remote` semantics: success means present, the documented not-found exit code means absent, and transport/auth/probe errors are not interpreted as absence.

## 8. Publication safety

The generic publisher preserves the hardened `1.0.5` publication window:

1. reserve an absent release as a draft without materializing a tag;
2. verify the draft target;
3. arm rollback only immediately before publishing the mutable draft;
4. publish with the exact target/title/notes;
5. read back `isDraft`, `isImmutable`, and target;
6. if publication did not become immutable, perform fail-closed cleanup while rollback is still safe;
7. as soon as immutability is confirmed, set rollback state to disarmed and remove the `ERR` trap;
8. only then perform post-immutability target/tag probes;
9. never attempt deletion of an immutable release.

The rollback helper probes `isImmutable` again before destructive cleanup. If the release is already immutable, rollback refuses deletion and returns the original failure.

The final verification phase checks every declared item, even when the run was a no-op/recovery path: release exists, is published, is immutable, target semantics are valid, and the Git tag resolves to the common release target.

## 9. Local validation at the release target

Before publishing an incomplete release set, the workflow validates the exact selected release target in a detached worktree.

At minimum it runs:

- `python scripts/validate_repo.py`;
- `python -m unittest discover -s tests -v`.

The manifest validator also checks repository release surfaces against the repository version declared by `release.json` (which is `1.0.6` in PR B):

- root RU/EN changelog contains the declared repository version;
- root RU/EN README current release badge/version contains the declared repository version;
- plugin entries, when present, agree with their plugin manifests and version surfaces.

The generic publisher must not hardcode all seven plugin versions for a repository-only release. Plugin versions remain validator-owned repository state unless a plugin is explicitly listed for publication.

## 10. Historical workflow migration

After generic publisher tests are GREEN, current-tip `main` removes all historical `publish-*.yml` files, including the completed `publish-repository-1.0.5.yml`.

They are not copied to an `archive/` directory. Git history and immutable release tags are the archive and preserve their exact source without leaving executable workflow definitions in the default branch.

Current release policy RU/EN is updated to state:

- historical publisher workflows are removed from the active default-branch workflow set after their releases are immutable;
- their historical source remains recoverable from Git commits/tags;
- only the generic current publisher may have an automatic release trigger.

No historical GitHub release or tag API mutation is part of this migration.

## 11. Test migration

PR B uses RED -> GREEN coverage before deleting legacy workflows.

New generic tests should establish these contracts:

1. exactly one active `.github/workflows/publish-*.yml` exists and it is `publish-current-release.yml`;
2. no OPUS/FABLE/PHASE/DOCS/release-specific publisher remains in current-tip workflows;
3. the generic workflow has only the successful canonical-main `workflow_run` automatic path;
4. concurrency is serialized and not cancel-in-progress;
5. manifest schema/paths/SemVer/plugin-tag rules fail closed;
6. repository-only `1.0.6` has an empty plugin release list;
7. stale-main initial state cannot publish;
8. existing immutable release is an ancestor-safe idempotent no-op;
9. drafts are recoverable only at one common ancestor target;
10. standalone tags, mutable published releases, conflicting targets, and ambiguous remote probes fail;
11. rollback is armed only during the mutable publication window;
12. cleanup probes immutability before delete and never deletes immutable history;
13. rollback is disarmed before any post-immutability tag/target probe;
14. final verification covers every declared release item;
15. the publisher never creates plugin tags when `plugins` is empty;
16. a release-set change cannot reuse the same already-current repository SemVer while altering plugin entries.

Workflow-specific tests that only pin removed historical YAML are deleted or rewritten into the generic contract suite. Safety assertions with continuing value are migrated, not silently discarded.

## 12. Repository `1.0.6`

PR B itself is a repository-only patch release.

Release set:

- repository tag/release: `1.0.6`;
- plugin release list: empty;
- plugin SemVer: unchanged;
- no service tags created.

Root `CHANGELOG.md` / `CHANGELOG.en.md` and README release badge/version move from `1.0.5` to `1.0.6`. Plugin README/changelog/version manifests do not change merely for this repository infrastructure release.

Release notes describe the single-publisher migration, manifest contract, legacy workflow retirement, and unchanged plugin versions.

## 13. Future release procedure

After `1.0.6`, a normal release does not add another workflow.

Every new release set receives the next repository SemVer, even when only selected plugins change. Independent plugin SemVer still changes only for the plugins whose own contract changes.

The release PR updates:

1. `.github/releases/release.json` to the new repository release and optional explicitly approved plugin entries;
2. one or more `.github/releases/*.md` notes files;
3. root changelog/version surfaces;
4. plugin versions/changelogs only for plugins actually being released.

After human authorization and squash merge, exact-main CI succeeds and the same `publish-current-release.yml` reconciles the new declaration.

The current manifest may remain unchanged after publication. Future successful main CI runs verify the already-immutable release and no-op. No workflow commits `enabled=false` or any other state back into `main`.

## 14. Success criteria

PR B is complete when:

1. current default branch contains exactly one active automatic release publisher;
2. historical publisher workflows no longer wake on future `main` CI completion;
3. the generic publisher is driven by validated declarative release intent;
4. hardened exact-main, immutable, draft-recovery, fail-closed probe, rollback, and idempotency semantics are regression-tested;
5. generic tests replace continuing safety value from workflow-specific tests;
6. repository `1.0.6` is published immutable on the exact squash-merged `main` SHA;
7. `1.0.5` and all earlier releases/tags remain unchanged and immutable;
8. all seven plugin versions and plugin tags remain unchanged;
9. a subsequent repository or selected-plugin release requires manifest/notes/version changes, not a new publisher workflow.
