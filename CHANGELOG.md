# Журнал изменений

[**Русский**](CHANGELOG.md) · [English](CHANGELOG.en.md)

Все значимые изменения уровня репозитория фиксируются здесь. Плагины используют независимый SemVer и имеют собственные changelog-файлы.

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