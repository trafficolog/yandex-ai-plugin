# First Release Finalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finalize the repository for the first release, place Phase 7 into backlog, add reviewer-oriented documentation, and merge the complete stacked implementation into `main`.

**Architecture:** Keep all existing plugin runtime behavior unchanged. Add only root release documentation and roadmap/backlog changes on top of `phase-6b-yandex-marketing`, validate the release candidate with the repository CI, then merge the stacked PR chain in dependency order and land the release-finalization PR last.

**Tech Stack:** Markdown, JSON/YAML repository metadata, GitHub Actions, Python 3.13 repository tests.

**Spec:** Existing approved Phase 1–6B design specs under `docs/superpowers/specs/`; no new runtime architecture is introduced by this plan.

## Global Constraints

- Do not modify functional code inside existing plugin directories during release finalization.
- Phase 7 Operations / AI / Mobile becomes backlog only; it is not part of the first release.
- Preserve independent plugin version `1.0.0` for all seven shipped plugins.
- Preserve safety invariant: `read → analyze → preview → explicit approval → write → verify`.
- Cross-service SEO and Marketing remain read/analyze/recommend/preview layers without live Yandex writes.
- Merge stack order must remain Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6A → Phase 6B → release finalization.

---

### Task 1: Release documentation

**Files:**
- Modify: `README.md`
- Create: `CHANGELOG.md`
- Create: `docs/REVIEW_FIRST_RELEASE.md`
- Modify: `docs/ROADMAP.md`

**Interfaces:**
- Consumes: shipped plugin manifests, current roadmap/service matrix, approved design specs.
- Produces: complete first-release documentation and a standalone reviewer checklist.

- [ ] **Step 1:** Replace root README with a detailed architecture/install/capability/safety/development guide covering all seven shipped plugins.
- [ ] **Step 2:** Add `CHANGELOG.md` with first release `1.0.0` dated 2026-09-02 and per-phase highlights.
- [ ] **Step 3:** Add `docs/REVIEW_FIRST_RELEASE.md` describing review scope, invariants, recommended inspection order, known limitations, and suggested adversarial checks for an independent model reviewer.
- [ ] **Step 4:** Move Phase 7 into an explicit backlog/future-releases section and mark the first-release feature set frozen after Phase 6B.
- [ ] **Step 5:** Verify documentation links and repository contracts with the existing root test/validator suite.

### Task 2: Release candidate PR

**Files:**
- No runtime files; release branch metadata only.

**Interfaces:**
- Consumes: `release-1.0.0-finalization` branch.
- Produces: stacked release-finalization PR targeting `phase-6b-yandex-marketing`.

- [ ] **Step 1:** Open the release-finalization PR.
- [ ] **Step 2:** Wait for GitHub Actions on the exact release-candidate HEAD and require `completed / success`.
- [ ] **Step 3:** Confirm release-finalization diff contains no functional changes under `plugins/`.

### Task 3: Merge stacked implementation into main

**Files:**
- Git refs and PR metadata only.

**Interfaces:**
- Consumes: PR #1 through PR #7 plus the release-finalization PR.
- Produces: final `main` containing the complete first release.

- [ ] **Step 1:** For each PR in stack order, fetch current PR metadata and CI for its exact HEAD.
- [ ] **Step 2:** Require open, mergeable, non-draft, and successful CI before merging.
- [ ] **Step 3:** Merge the current PR into its base.
- [ ] **Step 4:** Retarget the next stacked PR to `main`, re-check mergeability/CI, and continue.
- [ ] **Step 5:** Retarget and merge release-finalization last.

### Task 4: Post-merge verification

**Files:**
- Read-only verification of `main`.

**Interfaces:**
- Consumes: final `main` HEAD.
- Produces: release verification report.

- [ ] **Step 1:** Confirm `main` includes all seven marketplace plugins and release documentation.
- [ ] **Step 2:** Confirm Phase 7 appears only in backlog/future releases.
- [ ] **Step 3:** Fetch CI for final `main` HEAD and require `completed / success` when available.
- [ ] **Step 4:** Report final main SHA, merged PR chain, review-note path, README, CHANGELOG, and any remaining known limitations.
