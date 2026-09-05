# Release Policy

[Русский](RELEASE_POLICY.md) · [**English**](RELEASE_POLICY.en.md)

This document defines the current release process. It does not rewrite historical tags/releases and does not replace independent SemVer for plugins.

## 1. Two independent version lines

**repository SemVer** is the single current version line for the marketplace/repository. New repository releases use ordinary SemVer `X.Y.Z`.

**plugin SemVer** is the independent version of each installable plugin. A repository documentation or orchestration change does not automatically bump every plugin.

## 2. Repository SemVer and release sets

A repository release describes one coherent release set: repository-level changes plus any explicitly declared plugin releases. New changelog entries lead with repository SemVer, not a model name or phase label.

Use a patch release for compatible fixes/documentation, minor for significant compatible repository-contract capability, and major for a breaking repository-level contract.

**Every new release set receives a new repository SemVer and a new repository tag.** An already immutable repository release is never reused later to attach another plugin release. This keeps the release set → exact commit relationship unambiguous.

## 3. Plugin SemVer

A plugin changes version only when its own public/runtime/documentation contract changes enough to require a release. Service tags keep the form `yandex-<service>-vX.Y.Z`.

A repository-only release creates no new plugin tags when plugin artifacts and contract versions are unchanged. In the declarative manifest, `plugins: []` explicitly means repository-only and prohibits creation of a new plugin tag by that release set.

## 4. Declarative release manifest

Human-approved release intent lives in [`.github/releases/release.json`](../.github/releases/release.json). The manifest declares repository version/tag/title/notes and an optional list of plugin releases. It is not inferred automatically from changed files: no plugin entry means no authorization to publish that plugin.

The only automatic publisher in the current default branch is [`.github/workflows/publish-current-release.yml`](../.github/workflows/publish-current-release.yml). The workflow owns the shared publication mechanics; the manifest owns the contents of a particular release set. A future release changes manifest/notes/version surfaces instead of adding another publisher workflow.

The publisher and CI use the repository-owned `scripts/release_manifest.py` validator so schema, SemVer, notes paths, plugin versions, and canonical plugin tags share one interpretation.

## 5. Historical codenames and publisher source

`OPUS`, `PHASE`, `DOCS`, and `FABLE` are historical codenames/milestones. They can remain as context in old changelog entries and immutable releases, but they do not form competing future repository version lines.

Historical tags/releases are not retargeted, deleted, or rewritten merely to normalize naming.

After a historical release is immutable, its **historical publisher** YAML is removed from the active workflow set on the current default branch. Its source is not lost: the exact version remains recoverable through **Git history** and the immutable release tag/commit. There is no need to copy these workflows into an executable `archive/` directory at current tip.

## 6. Release gates

### AI audit

An `AI audit` is advisory input: a source of hypotheses, edge cases, and review questions. A model audit alone does not prove a defect and does not authorize a release.

### CI

`CI` is mechanical evidence: validator, tests, compilation, and release-contract checks. Green CI proves those checks passed, but does not replace semantic review or verification of an external API's current behavior.

### Independent review

`independent review` is a separate gate when available: a reviewer checks scope, semantics, safety, and regressions independently of the fix author. If external review is unavailable because of quota/tool limitations, that limitation is recorded explicitly rather than represented as a clean review.

### Human authorization

A `human` decision authorizes merge/release. AI audit, CI, or a reviewer must not silently replace the repository owner in the publication decision.

### Publication

After human authorization, the PR is merged with an exact-head guard. Post-merge CI must then pass on the exact `main` SHA. `publish-current-release.yml` reads only the declared release set, verifies exact tag SHA, immutable release state, and idempotent recovery semantics, and never adds release items on its own initiative.

## 7. Publisher safety contract

For an initial publication, the publisher requires the successful CI SHA still to be current `main`; a stale initial run completes as a verified no-op. Recovery from existing draft/immutable state is allowed only for one common target that remains an ancestor of live `main`.

Remote tag absence is checked fail-closed: a transport/auth/probe error is not treated as absence. A standalone tag, a published-but-mutable release, conflicting targets, or ambiguous recovery state is a hard failure.

Rollback is armed only for the mutable publication window. Before destructive cleanup the publisher probes `isImmutable` again; immediately after immutability is confirmed, rollback is disarmed before any later tag/target probes. Rollback never deletes an immutable release.

## 8. Batching hardening fixes

Small compatible hardening findings should be batched into one patch release when practical instead of producing several releases within a few hours. A separate urgent patch is appropriate when delay increases security, safety, or correctness risk.

An audit source or codename can appear in release notes as change provenance, while the repository version remains SemVer.

## 9. Immutable history

A published release is a historical immutable record. Its tag is never moved to another commit. A correction to a published version is released as a new version.

The publisher fails closed on conflicting tag/release state, an unexpected target SHA, or an inability to prove remote tag absence. No normal release flow mutates a previous immutable release merely to align it with a newer `main`.

## 10. Responsibility

- contributor/agent — proposes a change and evidence;
- human-approved `.github/releases/release.json` — defines the concrete release set;
- tests/CI — mechanically verify declared contracts;
- independent reviewer — searches for semantic/safety gaps;
- human maintainer — decides whether to merge/release;
- `publish-current-release.yml` — deterministically reconciles the already authorized exact-main release set.

Related documents: [`CONTRIBUTING.md`](../CONTRIBUTING.md), [`REVIEW_FIRST_RELEASE.en.md`](REVIEW_FIRST_RELEASE.en.md), [`PLUGIN_STANDARD.en.md`](PLUGIN_STANDARD.en.md).
