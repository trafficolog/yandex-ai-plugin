# Roadmap

[**Русский**](ROADMAP.md) · [English](ROADMAP.en.md)

First-release scope заморожен после Phase 6B. Ниже зафиксированы выпущенные архитектурные фазы и post-first-release milestones; backlog не является обещанием срока или следующего релиза.

RU-primary означает, что обычные предложения и поясняющий prose в этом документе пишутся по-русски. Английские product names, identifiers, code, API names и устоявшиеся технические термины допустимы; целые английские предложения используются только как цитаты или когда перевод исказил бы точный внешний contract.

## Первый релиз — завершён

### Phase 1 — Marketplace foundation

Direct перенесён в `plugins/yandex-direct/`; marketplace metadata, plugin standard, repository validator и path-aware CI стали общей основой.

### Phase 2 — Yandex Metrika

Изначально выпущен как plugin `1.0.0`. Добавлены Reporting/Management/Logs/Data Import workflows, quality metadata и preview-before-write guards.

### Phase 3 — Yandex Webmaster

Изначально выпущен как plugin `1.0.0`. Добавлены mixed v4/v4.1 routing, query/indexing, recrawl, sitemaps, feeds и export workflows.

### Phase 4 — Yandex Wordstat

Изначально выпущен как plugin `1.0.0` с девятью initial workflow skills, Wordstat API в составе Yandex Search API v2 helpers, provenance-aware semantics, regions/trends и quota/cost planning. Это historical initial count, а не текущее число skill directories или capability rows; current version определяется SERVICE_MATRIX/manifests.

### Phase 5 — Yandex Search

Изначально выпущен как plugin `1.0.0` с Search API v2 sync/deferred helpers, SERP snapshots, rankings, competitor analysis и URL-overlap clustering.

### Phase 6A — Yandex SEO

Изначально выпущен как plugin `1.0.0` с SEO Evidence Bundle, context alignment, findings, transparent prioritization и preview-only delegated actions. Плагин не содержит Yandex API clients и не выполняет live writes.

### Phase 6B — Yandex Marketing

Изначально выпущен как plugin `1.0.0` с Direct-required Marketing Evidence Bundle, KPI reconciliation, demand/query/landing/budget findings и preview-only delegated actions. Плагин не содержит Yandex API clients и не выполняет live writes.

### Maintenance — 1.0.1 / OPUS 1.1.0

Review-driven maintenance укрепил safety/API semantics, затем OPUS добавил Wordstat association coverage cap, Search 250-depth, Webmaster PRO lifecycle/quota, Marketing evidence roles/taxonomy и executable contract/freshness controls.

### DOCS 1.0.0

RU-primary / EN-mirror documentation layer, hero assets и orchestration diagrams. Plugin SemVer не изменяется.

## Post-first-release — выпущено

### Phase 7 — Topical Architecture

Выпущено как repository release `phase-7-topical-architecture-1.0.0`: Wordstat `1.1.0`, SEO `1.1.0`, Search `1.0.2` без изменения runtime.

- `yandex-wordstat-topic-map` формирует candidate-only `wordstat-topic-map/v1` с provenance, отдельными demand observations и limitation propagation.
- `yandex-search-clustering` сохраняет ownership реального SERP-overlap/Jaccard clustering; альтернативный fuzzy-text clusterer не добавлен.
- `yandex-seo-topical-architecture` формирует `seo-topical-architecture/v1` с `GREENFIELD|EXISTING_SITE`, page decisions, `structural_tree` и `semantic_graph`.
- `yandex-seo-internal-linking` создаёт preview-only link plan и deterministic audit без CMS writes.
- `OBSERVED`, `DERIVED`, `HYPOTHESIS`, `METHODOLOGY` остаются раздельными; semantic-cocoon/TGA/QBST methodology не заявляется как подтверждённый ranking mechanism.
- При отсутствии Search evidence обязателен `SERP_VALIDATION_MISSING`, а page boundaries остаются гипотезами.

---

# Future release backlog

Backlog — направление исследований, а не release promise.

## AI quality / evals

### Model eval runner / judge

Нужен отдельный model eval runner / judge поверх существующих `evals/scenarios.json` v2. Definition of done:

1. runner реально выполняет fixtures против выбранного runtime/model и семантически оценивает `outcome`, `must_convey` и `must_not_claim`;
2. deterministic exact-token lint (`must_mention_tokens`) остаётся отдельным mechanical evidence, а не заменяется judge;
3. результат фиксирует runtime, model, version и evaluation timestamp;
4. минимум один paired backend-equivalence scenario прогоняет один и тот же consequential request через connected MCP/app path и bundled-helper/file path и подтверждает одинаковый exact-preview + later-turn approval gate;
5. отчёт явно разделяет model/judge semantic evidence и repository validator/CI evidence.

До появления такого runner зелёный eval-v2 validator не означает, что модель семантически прошла сценарии.

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
