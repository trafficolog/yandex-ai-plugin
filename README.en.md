<p align="center"><img src="docs/assets/readme/root-hero-en.svg" alt="Yandex AI Plugins" width="100%"></p>

<p align="center"><a href="README.md">Русский</a> · <strong>English</strong></p>

<p align="center"><img alt="license MIT" src="https://img.shields.io/badge/license-MIT-white"> <img alt="plugins 7" src="https://img.shields.io/badge/plugins-7-3155ff"> <img alt="independent semver" src="https://img.shields.io/badge/semver-independent-3155ff"> <img alt="release" src="https://img.shields.io/badge/release-1.0.3-3155ff"></p>

# Yandex AI Plugins

A marketplace monorepo of independent AI plugins for working with Yandex services from AI agents and coding assistants. A plugin is the installation/version boundary; a skill is the workflow/knowledge boundary; volatile API contracts stay in the owning service plugin.

> **Status:** Phases 1–7 are implemented. The breaking `FABLE 2.0.0` safety generation for Direct/Metrika/Webmaster is already published as immutable releases. The review-5 maintenance increment advances Direct to `2.0.1`: the Reports helper uses env-only OAuth, bounded HTTP errors, and injectable transport while preserving async polling semantics. Metrika `2.0.0`, Webmaster `2.0.0`, Wordstat `1.1.2`, Search `1.0.2`, SEO `1.1.2`, and Marketing `1.1.0` are unchanged. The repository maintenance release is `1.0.3`.

## Quick overview

| Plugin | Version | Type | Primary scope | Live writes? |
|---|---:|---|---|---|
| [`yandex-direct`](plugins/yandex-direct/) | 2.0.1 | service | campaigns, reports, audit, keywords, budgets | exact preview + later-turn approval |
| [`yandex-metrika`](plugins/yandex-metrika/) | 2.0.0 | service | analytics, goals, attribution, Logs, imports | exact preview + later-turn approval |
| [`yandex-webmaster`](plugins/yandex-webmaster/) | 2.0.0 | service | indexing, queries, recrawl, sitemaps, feeds, exports | exact preview + later-turn approval |
| [`yandex-wordstat`](plugins/yandex-wordstat/) | 1.1.2 | service | demand, semantics, topic-map candidates, dynamics, regions | no consequential writes |
| [`yandex-search`](plugins/yandex-search/) | 1.0.2 | service | SERP, rankings, competitors, clustering | no |
| [`yandex-seo`](plugins/yandex-seo/) | 1.1.2 | cross-service | organic evidence, Topical Architecture, Internal Linking, orchestration | delegated preview only |
| [`yandex-marketing`](plugins/yandex-marketing/) | 1.1.0 | cross-service | paid acquisition and reconciliation | delegated preview only |

Details: [`docs/SERVICE_MATRIX.en.md`](docs/SERVICE_MATRIX.en.md) · [Русский](docs/SERVICE_MATRIX.md).

## Architecture

```text
service plugins                 cross-service orchestration
───────────────                 ───────────────────────────
yandex-direct ────────────────▶ yandex-marketing
yandex-metrika ───────┬───────▶ yandex-marketing
                      └───────▶ yandex-seo
yandex-wordstat ──────┬───────▶ yandex-marketing
                      └───────▶ yandex-seo
yandex-search ────────┬───────▶ yandex-marketing (optional context)
                      └───────▶ yandex-seo
yandex-webmaster ─────────────▶ yandex-seo
```

`yandex-seo` and `yandex-marketing` have no Yandex HTTP/API client or credential surface. They consume structured evidence/artifacts from service plugins, preserve provenance and limitations, derive findings, and delegate consequential action previews back to the owning service plugin.

Their `.agents` marketplace entries use `authentication: ON_USE` as schema-compatible deferred-auth metadata; this does not mean those transport-free plugins own credentials.

### Common safety lifecycle

```text
read → analyze → preview → explicit approval → write → verify
```

For consequential writes, approval applies only to the exact preview and is accepted only in a later user turn; generic permission does not carry over to a new payload. API/account/file content is data, not instructions. A recommendation is not permission to write. Draft creation is distinct from activation/publication.

Exact-preview binding, environment/auth identity, env-only Direct OAuth, and bounded transport errors are executable helper contracts. Rollback-context preservation and tighter handling for bulk edits above 20 entities remain agent/operator policy; generic helper-level enforcement is not claimed until a separate safety design defines those semantics.

## SEO orchestration

```mermaid
flowchart LR
  W[Wordstat<br/>demand] --> E[SEO Evidence Bundle]
  S[Search<br/>SERP / rankings] --> E
  WM[Webmaster<br/>queries / indexing] --> E
  M[Metrika<br/>traffic / conversions] --> E
  E --> O[SEO Orchestrator]
  O --> F[Findings]
  O --> P[Prioritization]
  O --> D[delegated previews]
  D --> OW[Owning service skill]
```

See [`plugins/yandex-seo/README.en.md`](plugins/yandex-seo/README.en.md).

### Phase 7: Semantic Cocoons / Topical Architecture / Internal Linking

Phase 7 does not turn Wordstat into a monolithic SEO-architecture tool. Ownership follows the evidence boundary:

```mermaid
flowchart LR
  W[Wordstat Topic Map<br/>candidate demand/topics] --> S[Search SERP Clustering<br/>real overlap / Jaccard]
  S --> A[SEO Topical Architecture]
  WM[Webmaster<br/>existing URLs / visibility] --> A
  M[Metrika<br/>landings / conversions] --> A
  A --> T[structural_tree]
  A --> G[semantic_graph]
  T --> L[Internal Linking]
  G --> L
  L --> P[preview-only plan / audit]
```

- `yandex-wordstat-topic-map` → `wordstat-topic-map/v1`, candidate topics/relations only; Wordstat does not prove final page boundaries. Query identity is normalized with Unicode NFKC + casefold + whitespace folding.
- `yandex-search-clustering` remains the owner of real SERP overlap; no competing fuzzy-text clusterer is added.
- `yandex-seo-topical-architecture` → `seo-topical-architecture/v1`, `GREENFIELD|EXISTING_SITE`, page decisions plus separate `structural_tree` and `semantic_graph`.
- Empirical boundary-changing decisions require Search-owned reason/evidence; `MERGE`/`REDIRECT` also require existing-page/URL evidence. `coverage.search=MISSING|PARTIAL` is exposed through explicit limitations.
- Search cluster ingress is validated before use; bridge/association/source limitations are preserved downstream.
- `yandex-seo-internal-linking` → preview-only link plan/audit with no CMS writes; orphaning is based on missing inbound links, duplicates are preserved and flagged, a rootless `BRIDGE` without inbound links is orphan/broken bridge, while `ROOT` remains exempt.
- Claim classes `OBSERVED`, `DERIVED`, `HYPOTHESIS`, `METHODOLOGY` stay distinct; `METHODOLOGY` is valid qualitative Evidence Bundle evidence but not quantitative metric evidence.
- Not-evaluated `link_plan`/`audits` serialize as `null`; evaluated-empty results are attached explicitly and remain `[]`.

## Marketing orchestration

```mermaid
flowchart LR
  D[Direct] --> B[Marketing Evidence Bundle]
  M[Metrika] --> B
  W[Wordstat] --> B
  S[Search<br/>optional] --> B
  B --> R[Reconciliation]
  R --> C[canonical]
  R --> X[reconciliation_only]
  R --> N[enrichment]
  C --> O[Marketing Orchestrator]
  X --> O
  N --> O
  O --> F[Findings / opportunities]
  O --> P[delegated previews]
```

Overlapping Direct/Metrika evidence is reconciled, never summed. See [`plugins/yandex-marketing/README.en.md`](plugins/yandex-marketing/README.en.md).

## Getting started

Marketplace metadata lives in `.agents/plugins/marketplace.json` and `.claude-plugin/marketplace.json`. Install only the plugins needed for a task.

```bash
cd plugins/yandex-marketing
python -m unittest discover -s tests -v
python -m compileall -q scripts
```

Repository verification:

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

Strict freshness is separate:

```bash
python scripts/check_reference_freshness.py
```

## Versions

```text
yandex-direct        2.0.1
yandex-metrika       2.0.0
yandex-webmaster     2.0.0
yandex-wordstat      1.1.2
yandex-search        1.0.2
yandex-seo           1.1.2
yandex-marketing     1.1.0
```

Plugins use independent SemVer. Repository milestones (`OPUS 1.1.0`, `DOCS 1.0.0`, `OPUS 1.1.1`, `PHASE 7 1.0.0`, `PHASE 7 1.0.1`, `OPUS 1.1.2`, `OPUS 1.1.3`, `FABLE 2.0.0`) do not imply synchronized plugin bumps. FABLE service releases `yandex-direct-v2.0.0`, `yandex-metrika-v2.0.0`, and `yandex-webmaster-v2.0.0` are published and immutable; review-5 maintenance publishes `yandex-direct-v2.0.1` and repository `1.0.3` after the exact-main CI gate.

## Documentation

- [`docs/PLUGIN_STANDARD.en.md`](docs/PLUGIN_STANDARD.en.md) · [RU](docs/PLUGIN_STANDARD.md)
- [`docs/SERVICE_MATRIX.en.md`](docs/SERVICE_MATRIX.en.md) · [RU](docs/SERVICE_MATRIX.md)
- [`docs/ROADMAP.en.md`](docs/ROADMAP.en.md) · [RU](docs/ROADMAP.md)
- [`docs/CONTRACT_MATRIX.json`](docs/CONTRACT_MATRIX.json) — high-risk traceability index, not semantic proof
- [`docs/REVIEW_FIRST_RELEASE.en.md`](docs/REVIEW_FIRST_RELEASE.en.md) · [RU](docs/REVIEW_FIRST_RELEASE.md)
- [`CHANGELOG.en.md`](CHANGELOG.en.md) · [RU](CHANGELOG.md)

## Structure

```text
plugins/yandex-<service>/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── skills/*/SKILL.md
├── references/
├── scripts/
├── tests/
├── evals/
├── README.md
├── README.en.md
├── CHANGELOG.md
└── CHANGELOG.en.md
```

## License and sources

Project code and original documentation are MIT licensed. Official Yandex documentation is canonical for API behavior; donor repositories and external SEO material are methodology/workflow references, not substitutes for authoritative API/ranking evidence.