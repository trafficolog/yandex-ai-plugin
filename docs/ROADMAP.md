# Roadmap

[**Русский**](ROADMAP.md) · [English](ROADMAP.en.md)

First-release scope заморожен после Phase 6B. Ниже зафиксированы выпущенные архитектурные фазы; backlog не является обещанием срока или следующего релиза.

## Первый релиз — завершён

### Phase 1 — Marketplace foundation

Direct перенесён в `plugins/yandex-direct/`; marketplace metadata, plugin standard, repository validator и path-aware CI стали общей основой.

### Phase 2 — Yandex Metrika

Implemented as plugin `1.0.0`. Добавлены Reporting/Management/Logs/Data Import workflows, quality metadata и preview-before-write guards.

### Phase 3 — Yandex Webmaster

Implemented as plugin `1.0.0`. Добавлены mixed v4/v4.1 routing, query/indexing, recrawl, sitemaps, feeds и export workflows.

### Phase 4 — Yandex Wordstat

Implemented as plugin `1.0.0` с девятью workflow skills, Cloud Wordstat v2 helpers, provenance-aware semantics, regions/trends и quota/cost planning.

### Phase 5 — Yandex Search

Implemented as plugin `1.0.0` с Search API v2 sync/deferred helpers, SERP snapshots, rankings, competitor analysis и URL-overlap clustering.

### Phase 6A — Yandex SEO

Implemented as plugin `1.0.0` с SEO Evidence Bundle, context alignment, findings, transparent prioritization и preview-only delegated actions. The plugin contains no Yandex API clients and performs no live writes.

### Phase 6B — Yandex Marketing

Implemented as plugin `1.0.0` с Direct-required Marketing Evidence Bundle, KPI reconciliation, demand/query/landing/budget findings и preview-only delegated actions. The plugin contains no Yandex API clients and performs no live writes.

### Maintenance — 1.0.1 / OPUS 1.1.0

Review-driven maintenance укрепил safety/API semantics, затем OPUS добавил Wordstat association coverage cap, Search 250-depth, Webmaster PRO lifecycle/quota, Marketing evidence roles/taxonomy и executable contract/freshness controls.

### DOCS 1.0.0

RU-primary / EN-mirror documentation layer, hero assets и orchestration diagrams. Plugin SemVer не изменяется.

---

# Future release backlog

Backlog — направление исследований, а не release promise.

## Operations / collaboration

### Yandex Tracker
Issues, queues, permissions, worklogs, boards; official API first.

### Yandex 360
Mail, Calendar, Disk и organization/admin boundaries; персональные и административные mutations должны быть разделены.

## Maps / local

### Yandex Maps
Geocoding, places, routes и local enrichment; перед реализацией требуется отдельный licensing/product design.

## Mobile

### AppMetrica
Mobile analytics, retention, crashes, deeplinks, push и acquisition context.

## AI / speech

### YandexGPT
Generation/embeddings/summarization как optional backend, а не обязательная зависимость deterministic service plugins.

### SpeechKit
Speech recognition/synthesis и transcription workflows.

## Backlog entry requirements

1. свежая official API/product research;
2. donor/capability research при необходимости;
3. решение о plugin boundary;
4. approved design;
5. implementation plan;
6. TDD/offline evals;
7. path-aware CI;
8. independent release review.