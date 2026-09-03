# Журнал изменений

[**Русский**](CHANGELOG.md) · [English](CHANGELOG.en.md)

Все значимые изменения уровня репозитория фиксируются здесь. Плагины используют независимый SemVer и имеют собственные changelog-файлы.

## [PHASE 7 1.0.1] — 2026-09-03

Post-release hardening patch для Topical Architecture / Semantic Cocoons baseline.

### Исправлено

- Yandex Wordstat `1.1.1` отклоняет duplicate `seeds[].seed`, сохраняя `source_seed` однозначным provenance key.
- Yandex Wordstat `1.1.1` отклоняет candidate topic self-relations (`from_topic_id == to_topic_id`).
- Yandex SEO `1.1.1` нормализует `structural_tree.nodes` через explicit field whitelist и не переносит caller execution/recommendation state (`decision`, `status`, `write`, `execution_id`).
- Yandex SEO `1.1.1` требует list-typed candidate-link `evidence`; scalar/object payload отклоняется до preview serialization.
- Service ownership, Search `1.0.2`, transport-free SEO boundary и preview-only internal-link semantics не меняются.

### Published plugin matrix

Direct `1.0.1`, Metrika `1.0.2`, Webmaster `1.0.3`, Wordstat `1.1.1`, Search `1.0.2`, SEO `1.1.1`, Marketing `1.1.0`.

## [PHASE 7 1.0.0] — 2026-09-02

Evidence-first Topical Architecture / Semantic Cocoons release.

### Architecture

- Yandex Wordstat `1.1.0` получил `yandex-wordstat-topic-map` и `wordstat-topic-map/v1`: candidate-only topic maps, provenance-preserving query deduplication, отдельные demand observations и explicit limitation propagation.
- Yandex Search остаётся `1.0.2` и единственным владельцем real SERP-overlap/Jaccard clustering; Phase 7 не добавляет competing fuzzy-text clusterer и не меняет Search runtime.
- Yandex SEO `1.1.0` получил `yandex-seo-topical-architecture` и `seo-topical-architecture/v1` для `GREENFIELD|EXISTING_SITE`, page decisions, независимых `structural_tree` и `semantic_graph`.
- Yandex SEO `1.1.0` получил `yandex-seo-internal-linking`: preview-only link planning и deterministic audit без CMS writes.

### Evidence and safety contracts

- `OBSERVED`, `DERIVED`, `HYPOTHESIS`, `METHODOLOGY` остаются раздельными; semantic-cocoon/TGA/QBST methodology не заявляется как подтверждённый ranking mechanism.
- Без Search evidence обязателен `SERP_VALIDATION_MISSING`, а page boundaries остаются hypotheses.
- Wordstat associations/co-occurrence не объявляются финальными page boundaries и не агрегируются в fictitious total demand.
- SEO остаётся transport-free: никаких новых Yandex HTTP clients, credentials или live mutations.
- `CONTRACT_MATRIX.json` закрепляет `wordstat.topic-map-candidate-boundary`, `seo.topical-architecture-structural-tree`, `seo.topical-architecture-evidence-classes`, `seo.internal-linking-preview-only`.

### Published plugin matrix

Direct `1.0.1`, Metrika `1.0.2`, Webmaster `1.0.3`, Wordstat `1.1.0`, Search `1.0.2`, SEO `1.1.0`, Marketing `1.1.0`.

## [OPUS 1.1.1] — 2026-09-02

Follow-up fix-release по финальному Opus 5 review.

### Repository controls

- 90-day freshness gate больше не является time-bomb для несвязанных PR: age hard-fail применяется к изменённому freshness-controlled reference, а scheduled strict workflow проверяет весь набор и синхронизирует отдельный GitHub issue.
- `CONTRACT_MATRIX.json` расширен контрактами Metrika Direct-expense duplication guard, Webmaster indexing archive lifecycle, SEO unknown Webmaster impressions и Marketing quality metadata shape.
- `PLUGIN_STANDARD` прямо определяет contract matrix как traceability index, а не semantic proof, и фиксирует, что eval fixtures пока структурно валидируются, но не исполняются против модели.
- Cross-service `authentication: ON_USE` документирован как schema-compatible deferred-auth metadata без собственной credential/transport surface.
- Marketing taxonomy согласована с фактической девяткой executable finding types и explicit deferred set через normative spec amendment.

### Plugin releases

- Yandex Metrika `1.0.2`: source-label guard для Direct expenses распознаёт tokenized labels и сохраняет независимый CSV UTM risk layer.
- Yandex Webmaster `1.0.3`: официально перепроверено поле indexing archive `state` (`IN_PROGRESS` / `DONE` / `FAILED`) и закреплено regression/traceability contract.
- Direct `1.0.1`, Wordstat `1.0.2`, Search `1.0.2`, SEO `1.0.1`, Marketing `1.1.0` не менялись.

## [DOCS 1.0.0] — 2026-09-02

### Изменено

- Русский язык стал основным для root README/CHANGELOG и ключевой repository-документации; английские версии публикуются как `.en.md` mirrors.
- Все семь production-плагинов получили двуязычные README/CHANGELOG пары без изменения их SemVer.
- Добавлены два локальных SVG hero-banner для RU/EN root README в `docs/assets/readme/`.
- В README `yandex-seo` и `yandex-marketing` добавлены Mermaid-схемы orchestration, явно показывающие evidence flow, no-transport boundary и delegated previews.
- Repository validator теперь проверяет наличие языковых пар, reciprocal language links и равенство release markers в RU/EN changelog.
- `docs/PLUGIN_STANDARD.md` закрепляет bilingual documentation как production contract.

### Версии плагинов не изменены

Direct `1.0.1`, Metrika `1.0.1`, Webmaster `1.0.2`, Wordstat `1.0.2`, Search `1.0.2`, SEO `1.0.1`, Marketing `1.1.0`.

## [OPUS 1.1.0] — 2026-09-02

Contract-hardening milestone: Wordstat association coverage cap, Search 250-result depth, Webmaster PRO lifecycle/quota semantics, Marketing evidence roles/taxonomy и executable repository contract/freshness controls.

## [1.0.1] — 2026-09-02

Review-driven maintenance: safe-by-default mutation/API contracts, omission-preserving Metrika attribution, cross-service evidence/context semantics, URL identity, evals и dependency-aware CI.

## [1.0.0] — 2026-09-02

Первый полный marketplace release: Direct, Metrika, Webmaster, Wordstat, Search, SEO и Marketing; единый plugin standard, safety lifecycle, offline tests/evals и path-aware CI.
