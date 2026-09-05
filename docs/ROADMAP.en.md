# Roadmap

[Русский](ROADMAP.md) · [**English**](ROADMAP.en.md)

The first-release scope is frozen after Phase 6B. The phases below are shipped architectural milestones and post-first-release releases; backlog items are not delivery-date or next-release promises.

RU-primary policy permits English product names, identifiers, code, API names, and established technical terms in Russian mirrors, but ordinary prose sentences should remain Russian unless quoted or translation would distort an exact external contract.

## First release — completed

### Phase 1 — Marketplace foundation
Direct moved under `plugins/yandex-direct/`; shared marketplace metadata, plugin standard, repository validator and path-aware CI were established.

### Phase 2 — Yandex Metrika
Initially shipped as plugin `1.0.0` with Reporting/Management/Logs/Data Import workflows, quality metadata and preview-before-write guards.

### Phase 3 — Yandex Webmaster
Initially shipped as plugin `1.0.0` with mixed v4/v4.1 routing, query/indexing, recrawl, sitemaps, feeds and exports.

### Phase 4 — Yandex Wordstat
Initially shipped as plugin `1.0.0` with nine initial workflow skills, Wordstat API within Yandex Search API v2 helpers, provenance-aware semantics, regions/trends and quota/cost planning. This is the historical initial count, not the current number of skill directories or capability rows; current version is owned by SERVICE_MATRIX/manifests.

### Phase 5 — Yandex Search
Initially shipped as plugin `1.0.0` with Search API v2 sync/deferred helpers, SERP snapshots, rankings, competitor analysis and URL-overlap clustering.

### Phase 6A — Yandex SEO
Initially shipped as plugin `1.0.0` with an SEO Evidence Bundle, context alignment, findings, transparent prioritization and preview-only delegated actions. The plugin contains no Yandex API clients and performs no live writes.

### Phase 6B — Yandex Marketing
Initially shipped as plugin `1.0.0` with a Direct-required Marketing Evidence Bundle, KPI reconciliation, demand/query/landing/budget findings and preview-only delegated actions. The plugin contains no Yandex API clients and performs no live writes.

### Maintenance — 1.0.1 / OPUS 1.1.0
Review-driven maintenance strengthened safety/API semantics; OPUS added Wordstat association coverage, Search 250-depth, Webmaster PRO lifecycle/quota, Marketing evidence roles/taxonomy, and executable contract/freshness controls.

### DOCS 1.0.0
RU-primary / EN-mirror documentation layer, hero assets and orchestration diagrams. Plugin SemVer is unchanged.

## Post-first-release — shipped

### Phase 7 — Topical Architecture

Shipped as repository release `phase-7-topical-architecture-1.0.0`: Wordstat `1.1.0`, SEO `1.1.0`, with Search remaining `1.0.2` and no Search runtime change.

- `yandex-wordstat-topic-map` produces candidate-only `wordstat-topic-map/v1` with provenance, separate demand observations, and limitation propagation.
- `yandex-search-clustering` retains ownership of real SERP-overlap/Jaccard clustering; no competing fuzzy-text clusterer is introduced.
- `yandex-seo-topical-architecture` produces `seo-topical-architecture/v1` with `GREENFIELD|EXISTING_SITE`, page decisions, `structural_tree`, and `semantic_graph`.
- `yandex-seo-internal-linking` produces preview-only link plans and deterministic audits with no CMS writes.
- `OBSERVED`, `DERIVED`, `HYPOTHESIS`, and `METHODOLOGY` remain separate; semantic-cocoon/TGA/QBST methodology is not represented as a verified ranking mechanism.
- When Search evidence is unavailable, `SERP_VALIDATION_MISSING` is mandatory and page boundaries remain hypotheses.

---

# Future release backlog

Backlog is research direction, not a release promise.

## AI quality / evals

### Model eval runner / judge

A dedicated model eval runner / judge is required on top of existing `evals/scenarios.json` v2. Definition of done:

1. the runner actually executes fixtures against a selected runtime/model and semantically judges `outcome`, `must_convey`, and `must_not_claim`;
2. deterministic exact-token lint (`must_mention_tokens`) remains separate mechanical evidence rather than being replaced by the judge;
3. each result records runtime, model, version, and evaluation timestamp;
4. at least one paired backend-equivalence scenario sends the same consequential request through a connected MCP/app path and a bundled-helper/file path and confirms the same exact-preview + later-turn approval gate;
5. reporting explicitly separates model/judge semantic evidence from repository validator/CI evidence.

Until that runner exists, a green eval-v2 validator does not mean that a model semantically passed the scenarios.

## Operations / collaboration
### Yandex Tracker
Issues, queues, permissions, worklogs and boards; official API first.

### Yandex 360
Mail, Calendar, Disk and organization/admin boundaries; personal and administrative mutations must stay distinct.

## Maps / local
### Yandex Maps
Geocoding, places, routes and local enrichment; requires dedicated licensing/product design.

## Mobile
### AppMetrica
Mobile analytics, retention, crashes, deeplinks, push and acquisition context.

## AI / speech
### YandexGPT
Generation/embeddings/summarization as an optional backend, not a mandatory dependency of deterministic service plugins.

### SpeechKit
Speech recognition/synthesis and transcription workflows.

## Backlog entry requirements
1. fresh official API/product research;
2. donor/capability research when useful;
3. plugin boundary decision;
4. approved design;
5. implementation plan;
6. TDD/offline evals;
7. path-aware CI;
8. independent release review.
