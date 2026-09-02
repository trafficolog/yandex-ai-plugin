# Журнал изменений — Yandex SEO

[**Русский**](CHANGELOG.md) · [English](CHANGELOG.en.md)

## [1.1.0] — 2026-09-02

- Добавлен `yandex-seo-topical-architecture` и schema `seo-topical-architecture/v1` для `GREENFIELD` / `EXISTING_SITE` architecture workflows.
- `structural_tree` и `semantic_graph` разделены: canonical structural parent остаётся единственным, semantic relations могут быть множественными.
- Добавлены page decisions `PRESERVE|CREATE|EXPAND|MERGE|SPLIT|REDIRECT|SECTION_ONLY|BRIDGE|NO_PAGE|MANUAL_REVIEW`.
- Evidence classes `OBSERVED|DERIVED|HYPOTHESIS|METHODOLOGY` и confidence `LOW|MEDIUM|HIGH` валидируются явно; methodology не повышается до ranking fact.
- При отсутствии Search evidence добавляется `SERP_VALIDATION_MISSING`; Search остаётся владельцем SERP-overlap clustering.
- Добавлен `yandex-seo-internal-linking`: preview-only link plans и deterministic audit (`ORPHAN_PAGE`, `STRUCTURAL_PARENT_LINK_MISSING`, `MISSING_JUSTIFIED_LINK`, `UNKNOWN_LINK_ENDPOINT`).
- SEO остаётся transport-free/read-only и не выполняет CMS writes.

## [1.0.1] — 2026-09-02

- Required Evidence Bundle context (`site`, `analysis_period`, `search_region_id`).
- Добавлены explicit period/geography/Search-config/device alignment states.
- Missing Webmaster impressions не считаются measured zero; quality/coverage limitations propagируются.
- Delegated previews остаются non-writing orchestration.

## [1.0.0]

- Первый cross-service SEO Evidence Bundle, findings и delegated-action workflows.
