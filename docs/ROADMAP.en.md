# Roadmap

[Русский](ROADMAP.md) · [**English**](ROADMAP.en.md)

The first-release scope is frozen after Phase 6B. The phases below are shipped architectural milestones; backlog items are not delivery-date or next-release promises.

## First release — completed

### Phase 1 — Marketplace foundation
Direct moved under `plugins/yandex-direct/`; shared marketplace metadata, plugin standard, repository validator and path-aware CI were established.

### Phase 2 — Yandex Metrika
Implemented as plugin `1.0.0` with Reporting/Management/Logs/Data Import workflows, quality metadata and preview-before-write guards.

### Phase 3 — Yandex Webmaster
Implemented as plugin `1.0.0` with mixed v4/v4.1 routing, query/indexing, recrawl, sitemaps, feeds and exports.

### Phase 4 — Yandex Wordstat
Implemented as plugin `1.0.0` with nine workflow skills, Cloud Wordstat v2 helpers, provenance-aware semantics, regions/trends and quota/cost planning.

### Phase 5 — Yandex Search
Implemented as plugin `1.0.0` with Search API v2 sync/deferred helpers, SERP snapshots, rankings, competitor analysis and URL-overlap clustering.

### Phase 6A — Yandex SEO
Implemented as plugin `1.0.0` with an SEO Evidence Bundle, context alignment, findings, transparent prioritization and preview-only delegated actions. The plugin contains no Yandex API clients and performs no live writes.

### Phase 6B — Yandex Marketing
Implemented as plugin `1.0.0` with a Direct-required Marketing Evidence Bundle, KPI reconciliation, demand/query/landing/budget findings and preview-only delegated actions. The plugin contains no Yandex API clients and performs no live writes.

### Maintenance — 1.0.1 / OPUS 1.1.0
Review-driven maintenance strengthened safety/API semantics; OPUS added Wordstat association coverage, Search 250-depth, Webmaster PRO lifecycle/quota, Marketing evidence roles/taxonomy, and executable contract/freshness controls.

### DOCS 1.0.0
RU-primary / EN-mirror documentation layer, hero assets and orchestration diagrams. Plugin SemVer is unchanged.

---

# Future release backlog

Backlog is research direction, not a release promise.

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