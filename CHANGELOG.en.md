# Changelog

[Русский](CHANGELOG.md) · [**English**](CHANGELOG.en.md)

All notable repository-level changes are documented here. Plugins use independent SemVer and keep their own changelogs.

## [DOCS 1.0.0] — 2026-09-02

### Changed

- Russian became the primary language for root README/CHANGELOG and key repository documentation; English versions are published as `.en.md` mirrors.
- All seven production plugins gained bilingual README/CHANGELOG pairs without changing plugin SemVer.
- Added local RU/EN SVG hero banners under `docs/assets/readme/`.
- Added Mermaid orchestration diagrams to `yandex-seo` and `yandex-marketing` READMEs, making evidence flow, the no-transport boundary, and delegated previews explicit.
- Repository validation now checks bilingual pairs, reciprocal language links, and identical release markers across RU/EN changelogs.
- `docs/PLUGIN_STANDARD.md` now treats bilingual documentation as a production contract.

### Plugin versions unchanged

Direct `1.0.1`, Metrika `1.0.1`, Webmaster `1.0.2`, Wordstat `1.0.2`, Search `1.0.2`, SEO `1.0.1`, Marketing `1.1.0`.

## [OPUS 1.1.0] — 2026-09-02

Contract-hardening milestone: Wordstat association coverage cap, Search 250-result depth, Webmaster PRO lifecycle/quota semantics, Marketing evidence roles/taxonomy, and executable repository contract/freshness controls.

## [1.0.1] — 2026-09-02

Review-driven maintenance covering safe-by-default mutations/API contracts, omission-preserving Metrika attribution, cross-service evidence/context semantics, URL identity, evals, and dependency-aware CI.

## [1.0.0] — 2026-09-02

First complete marketplace release: Direct, Metrika, Webmaster, Wordstat, Search, SEO and Marketing, with a shared plugin standard, safety lifecycle, offline tests/evals, and path-aware CI.