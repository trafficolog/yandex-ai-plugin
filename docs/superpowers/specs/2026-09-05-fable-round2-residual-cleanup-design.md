# Fable Round 2 Residual Cleanup — Repository 1.0.8 Design

Status: approved high-level design, awaiting written-spec review  
Date: 2026-09-05  
Base: `3d25004f32be1b544d0c12f2f82452ed4e26e5d4` (`main`, immutable repository `1.0.7`)

## 1. Purpose

Repository `1.0.7` closed the selected Opus/governance remediation scope, but a cross-check against Fable 5.1 Round 2 found several residual documentation/governance findings that were skipped because later audit rounds were remediated out of order.

Repository `1.0.8` closes those residuals in one bounded hardening patch. It does not redesign plugin runtime behavior.

## 2. Release boundary

This is a **repository-only patch release**:

- repository SemVer: `1.0.7` → `1.0.8`;
- declarative release manifest keeps `plugins: []`;
- no new plugin tags;
- plugin versions remain:
  - Yandex Direct `2.0.1`;
  - Yandex Metrika `2.0.0`;
  - Yandex Webmaster `2.0.0`;
  - Yandex Wordstat `1.1.2`;
  - Yandex Search `1.0.2`;
  - Yandex SEO `1.1.2`;
  - Yandex Marketing `1.1.0`.

A plugin README may receive a **source-of-truth link correction** only when the behavioral/documentation contract remains unchanged. Such a correction is repository governance maintenance under `REQ-DOCS-RELEASE-NO-PLUGIN-BUMP`, not a plugin release.

No plugin helper/runtime code, API behavior, safety semantics, eval schema, marketplace manifest, or plugin version changes are allowed in this PR.

## 3. Residual finding map

### 3.1 Historical `docs/superpowers/` must not be normative in production plugin docs

Current defect: Marketing RU/EN README still describes a `docs/superpowers/specs/...` design file as the normative mapping for executable finding taxonomy, contradicting the `1.0.7` governance boundary.

Required state:

- no `plugins/*/README.md` or `plugins/*/README.en.md` may use `docs/superpowers/` as a production source;
- Marketing RU/EN README must point to current executable/canonical sources such as its local scripts/tests plus repository production contracts;
- `docs/REVIEW_FIRST_RELEASE*` may continue to mention `docs/superpowers/` only as historical implementation context;
- regression coverage must prevent a plugin README from reintroducing a `docs/superpowers/` dependency.

### 3.2 Wordstat product naming must be canonical across current docs

Current canonical wording:

- RU: `Wordstat API в составе Yandex Search API v2`;
- EN: `Wordstat API within Yandex Search API v2`.

Required state:

- current-facing `ROADMAP` and `SERVICE_MATRIX` RU/EN use this wording;
- the stale product label `Cloud Wordstat v2` is forbidden in those canonical current-facing documents;
- historical donor descriptions under plugin references are not rewritten merely because a donor used older naming.

This is a documentation naming correction. It does not change Wordstat authentication/runtime behavior.

### 3.3 `SKILL.md` content contract must match actual validator/safety behavior

Add stable requirement ID `REQ-SKILL-CONTENT`. Existing 17 IDs remain semantically unchanged.

`PLUGIN_STANDARD` §5 RU/EN must explicitly state the mechanical contract already enforced by the repository:

- frontmatter `name` equals the skill directory;
- `description` starts with `Use when`;
- description length is `32–500` characters;
- `SKILL.md` maximum size is `15 KiB` (`15 * 1024` bytes);
- long/volatile facts use progressive disclosure through `references/`;
- write-capable skills must carry the exact-preview and untrusted-data safety metadata already required by eval/validator contracts.

The standard must also define semantic review expectations for every skill body:

- scope includes when the skill should **not** own the request;
- adjacent capability is delegated/routed to the owning skill/plugin rather than silently absorbed;
- source/API limitations are preserved downstream;
- body text must not redefine repository-wide approval or ownership semantics.

These body semantics are `review + policy` in `1.0.8`; they are not converted into brittle heading-name grep rules. No mass rewrite of existing `SKILL.md` files is in scope.

### 3.4 Eval execution limitation must become explicit tracked backlog

Current eval v2 is structurally/lint validated but not executed against a model/judge.

`ROADMAP` RU/EN must gain an explicit backlog item for a **model eval runner / judge** with definition of done:

- execute existing `evals/scenarios.json` v2 against a selected runtime/model;
- judge `outcome`, `must_convey`, and `must_not_claim` semantically;
- preserve exact-token checks as deterministic lint evidence;
- record model/runtime/version and evaluation timestamp;
- include at least one paired backend-equivalence case where the same consequential request through a connected MCP/app path and a bundled-helper/file path preserves the same exact-preview + later-turn approval gate.

Repository `1.0.8` does **not** claim to implement model execution. The finding is closed by making the limitation and required future acceptance criteria explicit rather than leaving an untracked gap.

### 3.5 ROADMAP historical/version/language wording must be unambiguous

Required state:

- historical phase lines use `Изначально выпущен...` / `Initially shipped...` instead of wording that can be mistaken for current plugin version;
- Phase 4 states `nine initial workflow skills` so it cannot be confused with the current number of skill directories or capability rows;
- current versions remain owned by `SERVICE_MATRIX`;
- RU ROADMAP must not contain the known full English prose sentences for SEO/Marketing transport boundaries;
- RU-primary policy is clarified: English product names, identifiers, code and established technical terms are allowed, but ordinary prose sentences in RU-primary docs should be Russian unless quoted.

No generic natural-language detector is added; the known drift is fixed and the policy becomes reviewable.

### 3.6 Repeated `authentication: ON_USE` explanation must have one canonical owner

`ARCHITECTURE` RU/EN becomes the canonical explanatory source for cross-service `.agents` `authentication: ON_USE` semantics:

- the marketplace schema requires a supported authentication policy;
- for transport-free SEO/Marketing, `ON_USE` means deferred authentication in owning service plugins;
- it does not grant SEO/Marketing credentials or HTTP transport ownership.

`PLUGIN_STANDARD`, `SERVICE_MATRIX`, SEO README and Marketing README may retain a concise local statement/link, but must not duplicate the full explanatory paragraph. Regression coverage should keep the distinctive long-form phrase `schema-compatible deferred-auth metadata` owned by one canonical document only.

### 3.7 Community-governance baseline must be complete

Add:

- `CODE_OF_CONDUCT.md` (RU primary) and `CODE_OF_CONDUCT.en.md`;
- `.github/ISSUE_TEMPLATE/bug_report.md`;
- `.github/ISSUE_TEMPLATE/feature_request.md`;
- `.github/pull_request_template.md`.

Requirements:

- security-sensitive reports route to `SECURITY.md` rather than asking for public exploit details;
- PR template covers scope, tests/CI, documentation, plugin SemVer decision, secrets/safety, and review evidence;
- no invented email address, response SLA, or private reporting channel;
- root README RU/EN links the security, contribution, code-of-conduct and review entrypoints.

`SECURITY.md` / `SECURITY.en.md` and the new code-of-conduct pair become mechanically checked bilingual root policy pairs.

### 3.8 Fable Round 2 closure evidence

Add bilingual dated review/remediation artifact:

- `docs/reviews/2026-09-05-fable-round2-closure.md`;
- `docs/reviews/2026-09-05-fable-round2-closure.en.md`.

It must distinguish:

- original Fable Round 2 finding;
- current `1.0.8` disposition (`closed`, `closed as explicit backlog`, or previously closed);
- mechanical evidence vs semantic/review evidence;
- the repository base and the intended `1.0.8` remediation scope.

The artifact is part of the release commit, so it **must not claim future self-referential evidence** such as the eventual squash-merge SHA, post-merge CI run ID, publisher run ID or release ID. Once PR # is known, the artifact may link that PR. Dynamic exact-head/post-merge/publication evidence belongs in the PR discussion/body and the GitHub immutable release record. No later mutation of the `1.0.8` release is performed merely to backfill those identifiers.

## 4. Canonical ownership after 1.0.8

| Topic | Canonical owner |
|---|---|
| Current plugin versions | `docs/SERVICE_MATRIX*` + plugin manifests, mechanically reconciled |
| Wordstat current product naming | plugin README + `SERVICE_MATRIX`/`ROADMAP` canonical wording |
| Cross-service transport/auth explanation | `docs/ARCHITECTURE*` |
| Repository-wide plugin/skill requirements | `docs/PLUGIN_STANDARD*` |
| Historical implementation intent | `docs/superpowers/` (non-normative) |
| Review evidence | `docs/reviews/` |
| Security reporting | `SECURITY*` |
| Release process | `docs/RELEASE_POLICY*` |

Summaries in other documents may exist for usability, but must link back and must not redefine the canonical contract.

## 5. Test strategy — strict RED → GREEN

### RED group A — normative-source and naming drift

Add failing tests proving:

1. production plugin READMEs cannot depend on `docs/superpowers/`;
2. `ROADMAP`/`SERVICE_MATRIX` cannot contain stale `Cloud Wordstat v2` wording;
3. the canonical Wordstat phrase exists in RU/EN current docs.

GREEN changes update Marketing README RU/EN and the four current-facing Wordstat documents.

### RED group B — skill-standard contract

Add failing tests proving:

1. RU/EN requirement tables contain the same `REQ-SKILL-CONTENT` ID;
2. §5 documents the actual `32–500` description contract and `15 KiB` skill limit;
3. §5 documents progressive disclosure, non-ownership/delegation and limitation propagation;
4. validator constants remain the source of the mechanical numeric bounds.

GREEN changes update only repository standard/tests unless an existing validator inconsistency is discovered.

### RED group C — roadmap/canonicalization/community baseline

Add failing tests proving:

1. ROADMAP historical wording is explicitly initial and RU known prose drift is removed;
2. model eval runner/judge backlog with backend-equivalence acceptance exists RU/EN;
3. long-form ON_USE explanation has one canonical owner in `ARCHITECTURE`;
4. CODE_OF_CONDUCT and GitHub issue/PR templates exist and contain required safety/governance entrypoints;
5. SECURITY and CODE_OF_CONDUCT bilingual pairs are validated.

GREEN changes update repository docs/community metadata only.

### RED group D — release `1.0.8`

Add release-contract tests proving:

- root README RU/EN current repository release is `1.0.8`;
- root CHANGELOG RU/EN contains synchronized `1.0.8` markers;
- `.github/releases/release.json` declares repository `1.0.8`;
- `.github/releases/1.0.8.md` exists;
- `plugins: []`;
- all seven plugin manifest versions remain unchanged;
- no plugin release/tag is declared by the release set.

GREEN stages release surfaces only after implementation contracts are green.

## 6. Expected files

Likely modified:

- `docs/PLUGIN_STANDARD.md`
- `docs/PLUGIN_STANDARD.en.md`
- `docs/ARCHITECTURE.md`
- `docs/ARCHITECTURE.en.md`
- `docs/ROADMAP.md`
- `docs/ROADMAP.en.md`
- `docs/SERVICE_MATRIX.md`
- `docs/SERVICE_MATRIX.en.md`
- `plugins/yandex-marketing/README.md`
- `plugins/yandex-marketing/README.en.md`
- `README.md`
- `README.en.md`
- `CHANGELOG.md`
- `CHANGELOG.en.md`
- `scripts/bilingual_docs.py`
- repository tests
- `.github/releases/release.json`

New:

- `CODE_OF_CONDUCT.md`
- `CODE_OF_CONDUCT.en.md`
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/pull_request_template.md`
- `.github/releases/1.0.8.md`
- `docs/reviews/2026-09-05-fable-round2-closure.md`
- `docs/reviews/2026-09-05-fable-round2-closure.en.md`
- focused regression tests for this cleanup.

No files under `plugins/*/scripts`, plugin manifests, plugin changelogs or plugin evals are expected to change.

## 7. Release and verification gates

1. strict RED evidence for every new contract group;
2. GREEN implementation commits;
3. exact-head full CI;
4. independent semantic/code review if available;
5. if reviewer is unavailable due quota/tool limitation, record that explicitly and do not call it clean review;
6. squash merge to exact tested head;
7. post-merge CI on exact `main` SHA;
8. `publish-current-release.yml` publishes repository `1.0.8` only;
9. verify release `1.0.8` is immutable and tag points directly to squash-merge SHA;
10. re-check immutable `1.0.7` release/tag target unchanged;
11. verify no new `yandex-*` plugin tag points to the `1.0.8` merge SHA.

## 8. Success criteria

The patch is complete only when:

- all actionable Fable Round 2 residuals identified after `1.0.7` are either implemented or explicitly converted into a truthful tracked backlog acceptance criterion;
- no production plugin README treats `docs/superpowers/` as normative;
- current Wordstat naming is consistent across canonical current-facing docs;
- `PLUGIN_STANDARD` accurately describes the existing skill contract and adds `REQ-SKILL-CONTENT` without changing the meaning of prior requirement IDs;
- eval-runner limitation and backend-equivalence requirement are explicit backlog, not implied capability;
- ROADMAP historical/language ambiguity is removed;
- ON_USE explanatory ownership is centralized;
- community governance baseline exists without invented contact/SLA data;
- repository `1.0.8` is published immutable at the exact green merge SHA;
- plugin SemVer and historical immutable releases/tags remain unchanged.
