# Release Policy

[Русский](RELEASE_POLICY.md) · [**English**](RELEASE_POLICY.en.md)

This document defines the future release process. It does not rewrite historical tags/releases and does not replace independent SemVer for plugins.

## 1. Two independent version lines

**repository SemVer** is the single current version line for the marketplace/repository. New repository releases use ordinary SemVer `X.Y.Z`.

**plugin SemVer** is the independent version of each installable plugin. A repository documentation or orchestration change does not automatically bump every plugin.

## 2. Repository SemVer

A repository release describes a coherent set of repository-level changes such as documentation, validator/CI contracts, marketplace metadata, or other shared infrastructure. New changelog entries lead with repository SemVer, not a model name or phase label.

Use a patch release for compatible fixes/documentation, minor for significant compatible repository-contract capability, and major for a breaking repository-level contract.

## 3. Plugin SemVer

A plugin changes version only when its own public/runtime/documentation contract changes enough to require a release. Service tags keep the form `yandex-<service>-vX.Y.Z`.

A repository-only release creates no new plugin tags when plugin artifacts and contract versions are unchanged.

## 4. Historical codenames

`OPUS`, `PHASE`, `DOCS`, and `FABLE` are historical codenames/milestones. They can remain as context in old changelog entries and immutable releases, but they do not form competing future repository version lines.

Historical tags/releases are not retargeted, deleted, or rewritten merely to normalize naming.

## 5. Release gates

### AI audit

An `AI audit` is advisory input: a source of hypotheses, edge cases, and review questions. A model audit alone does not prove a defect and does not authorize a release.

### CI

`CI` is mechanical evidence: validator, tests, compilation, and release-contract checks. Green CI proves those checks passed, but does not replace semantic review or verification of an external API's current behavior.

### Independent review

`independent review` is a separate gate when available: a reviewer checks scope, semantics, safety, and regressions independently of the fix author. If external review is unavailable because of quota/tool limitations, that limitation is recorded explicitly rather than represented as a clean review.

### Human authorization

A `human` decision authorizes merge/release. AI audit, CI, or a reviewer must not silently replace the repository owner in the publication decision.

### Publication

After human authorization, the PR is merged with an exact-head guard. Post-merge CI must then pass on the exact `main` SHA. The publisher creates only the predeclared release set and verifies exact tag SHA, immutable release state, and idempotent recovery semantics.

## 6. Batching hardening fixes

Small compatible hardening findings should be batched into one patch release when practical instead of producing several releases within a few hours. A separate urgent patch is appropriate when delay increases security, safety, or correctness risk.

An audit source or codename can appear in release notes as change provenance, while the repository version remains SemVer.

## 7. Immutable history

A published release is a historical record. Its tag is never moved to another commit. A correction to a published version is released as a new version.

The publisher fails closed on conflicting tag/release state, an unexpected target SHA, or an inability to prove remote tag absence.

## 8. Responsibility

- contributor/agent — proposes a change and evidence;
- tests/CI — mechanically verify declared contracts;
- independent reviewer — searches for semantic/safety gaps;
- human maintainer — decides whether to merge/release;
- publisher — deterministically publishes the already authorized exact-main artifact.

Related documents: [`CONTRIBUTING.md`](../CONTRIBUTING.md), [`REVIEW_FIRST_RELEASE.en.md`](REVIEW_FIRST_RELEASE.en.md), [`PLUGIN_STANDARD.en.md`](PLUGIN_STANDARD.en.md).
