# Fable Documentation UX & Governance — design

Date: 2026-09-04
Status: approved design, ready for implementation planning
Base: `main` at `4112edefbbcd0618e8bc81f535bf7ca3a90f79b7` (`Repository 1.0.4`)
Target repository release: `1.0.5`
Plugin SemVer: unchanged

## 1. Problem

The repository has strong implementation and safety contracts but its public documentation is optimized for maintainers and models rather than a first-time human user. The root README mixes landing-page content with PR-level implementation detail, onboarding is fragmented across plugin-local references, repository release history mixes SemVer with historical OPUS/PHASE/DOCS/FABLE milestones, and contributor/release governance is implicit rather than documented.

Audit round 1 also included findings already closed or disproved by current `main`: SEO/Wordstat version drift is fixed and now validator-enforced; the repository badge is `1.0.4`; the repository description already clarifies that these are AI plugins for Yandex services; Wordstat is correctly documented against the current Yandex Search API Wordstat surface. This task must not re-open those items as code defects.

## 2. Goals

1. Make the root README a human-first landing page answering: what this is, who it is for, what plugins exist, how to install, how safety works, and where to go next.
2. Provide a single RU/EN Getting Started path from marketplace import through credentials to a first safe read-only request.
3. Document contributor and release governance, explicitly separating repository SemVer, independent plugin SemVer, and historical milestone codenames.
4. Preserve technical rigor by moving low-level architecture and safety detail to dedicated documents rather than deleting it.
5. Reduce Runglish in Russian prose while preserving exact machine tokens and identifiers.
6. Release the documentation/governance work as repository-only `1.0.5`; no plugin version changes.

## 3. Non-goals

- No plugin runtime behavior changes.
- No plugin SemVer bumps or plugin tags.
- No deletion, retargeting, or mutation of historical immutable releases/tags.
- No release-infrastructure simplification in this PR; legacy publisher cleanup is a separate PR B.
- No mass reduction or restructuring of the 72 skills.
- No removal of safety, evidence, SEO, or marketing invariants based only on a documentation audit.
- No migration of historical `docs/superpowers/` artifacts; future neutral-path policy may be defined separately without rewriting history.
- No repository rename.

## 4. Documentation information architecture

Public documentation is split by audience and level:

### Level 1 — landing

`README.md` / `README.en.md`

Purpose: first contact. Keep the hero and plugin table, but prioritize plain-language explanation and navigation.

Required sections:

1. concise one-paragraph definition: AI plugins for Yandex services used from external AI agents/coding assistants;
2. who this is for and what problems it solves;
3. plugin catalog with independent versions and service/cross-service distinction;
4. 3-minute quick start linking to Getting Started;
5. one short end-to-end example;
6. safety lifecycle in one compact block;
7. simplified SEO and Marketing orchestration diagrams;
8. limitations / what the project does not claim;
9. links to architecture, getting started, release policy, plugin standard, service matrix and changelog.

Implementation-detail prose such as `cluster ingress`, evaluated-empty serialization, rootless `BRIDGE`, transport adapter details and exact regression semantics moves out of the landing page.

### Level 2 — user guides

New bilingual documents:

- `docs/GETTING_STARTED.md`
- `docs/GETTING_STARTED.en.md`
- `docs/GLOSSARY.md`
- `docs/GLOSSARY.en.md`

Getting Started covers:

- supported Python floor for bundled helpers;
- marketplace import options for `.agents/plugins/marketplace.json` and `.claude-plugin/marketplace.json` without claiming unsupported runtime-specific commands;
- plugin selection by task;
- credential model per service, linking to owning plugin references instead of duplicating volatile auth facts;
- first read-only examples;
- one consequential-write example showing preview → later-turn approval → execute;
- troubleshooting and verification commands.

Glossary translates/explains recurring prose concepts while preserving exact tokens such as `preview_id`, `OBSERVED`, `DERIVED`, `HYPOTHESIS`, `METHODOLOGY`, `SERP_VALIDATION_MISSING`, `canonical`, `reconciliation_only` and `enrichment`.

### Level 3 — architecture and governance

New bilingual architecture document:

- `docs/ARCHITECTURE.md`
- `docs/ARCHITECTURE.en.md`

It owns the detailed service-vs-cross-service model, evidence flow, transport-free SEO/Marketing boundary, progressive disclosure model, shared-code policy, and orchestration semantics removed from the root README.

Governance documents:

- `CONTRIBUTING.md`
- `docs/RELEASE_POLICY.md`
- `docs/RELEASE_POLICY.en.md`

`CONTRIBUTING.md` is concise and may remain English-neutral/technical where repository conventions require it; user-facing repository key docs remain RU-primary with EN mirrors.

## 5. Release/version policy

The public rule for future work is:

- repository releases use one SemVer line: `X.Y.Z`;
- plugins continue independent SemVer and service tags such as `yandex-direct-v2.0.1`;
- historical labels `OPUS`, `PHASE`, `DOCS`, `FABLE` are codenames/milestones, not competing current repository version schemes;
- historical immutable tags/releases remain untouched;
- new changelog entries lead with repository SemVer and may mention a codename only as descriptive metadata;
- AI audit output is advisory evidence, not release authorization;
- green CI is mechanical evidence, not independent semantic/API verification;
- independent review is a separate gate where available;
- a human decision authorizes merge/release;
- small hardening findings should be batched into a patch release when practical.

PR A documents this policy but does not alter legacy automatic publisher behavior. PR B implements infrastructure simplification separately.

## 6. Human-first wording rules

Russian is the primary user-facing language.

- Prefer Russian prose for concepts when an exact identifier is not required.
- Keep protocol/API/schema identifiers unchanged.
- First use of unavoidable English jargon should be explained in Russian or linked to the glossary.
- README sentences should describe user value and guarantees, not individual regression-test implementation details.
- Changelog may retain implementation-level vocabulary because it serves maintainers.

Wordstat public wording should use the less ambiguous formulation: “Wordstat API в составе Yandex Search API v2” / “Wordstat API within Yandex Search API v2”. This is a clarity change, not a product/API correction.

## 7. Onboarding contract

A new user should be able to reach a safe first result without reading plugin internals.

Canonical journey:

1. import or register the marketplace metadata in a compatible runtime;
2. choose only the plugin(s) required for the task;
3. satisfy the owning plugin credential requirements using links to its verified references;
4. run or ask for a read-only operation first;
5. for consequential writes, receive an exact preview and approve it in a later user turn before execution;
6. use plugin-local references/tests when deeper API detail is needed.

The docs must not invent OAuth scopes or installation commands not supported by repository sources. Volatile auth facts remain in plugin-local freshness-controlled references and are linked rather than copied into root docs.

## 8. Validation and regression coverage

This PR should add repository tests/contracts for documentation structure, not subjective prose scoring.

Mechanical checks should cover:

- presence of RU/EN pairs for `GETTING_STARTED`, `ARCHITECTURE`, `GLOSSARY`, `RELEASE_POLICY`;
- reciprocal language links and bilingual structural/SemVer parity through existing validator rules;
- root README links to Getting Started, Architecture, Release Policy and plugin catalog;
- root README current repository badge/version remains `1.0.5` and plugin matrix matches manifests;
- Wordstat README uses the clarified Search API wording without changing plugin SemVer;
- release policy contains one-repository-SemVer and independent-plugin-SemVer rules;
- Getting Started includes Python support, marketplace metadata paths, credentials-by-link, read-only first step and exact-preview lifecycle;
- no plugin manifest/marketplace versions change as part of this docs-only release.

Do not add brittle exact-copy tests for human prose beyond stable headings/links/tokens required by the documentation contract.

## 9. Repository 1.0.5 release

`1.0.5` is repository-only.

Release contents:

- human-first RU/EN root README;
- Getting Started, Architecture, Glossary, Release Policy;
- CONTRIBUTING;
- clarified Wordstat wording;
- updated RU/EN root changelog and release badge;
- validation/tests for the new documentation contract.

The release publisher must follow the existing exact-main successful-CI + immutable-release pattern. Because release-infrastructure simplification is deliberately isolated to PR B, PR A may add the minimal current-pattern `1.0.5` publisher needed to publish this release, but must not refactor or mutate historical publisher workflows.

## 10. Success criteria

The task is complete when:

1. a first-time user can identify the right plugin and reach a read-only example from the root README in a few clicks;
2. low-level orchestration/safety rules remain accessible but no longer dominate the landing page;
3. repository vs plugin versioning is unambiguous in current docs;
4. human/AI/CI/review release responsibilities are explicit;
5. RU/EN docs satisfy existing structural parity validation;
6. all root and affected plugin CI jobs are green;
7. repository `1.0.5` is published immutable on the exact post-merge `main` SHA;
8. plugin versions and historical releases remain unchanged.
