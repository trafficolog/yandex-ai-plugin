# Changelog

[Русский](CHANGELOG.md) · [**English**](CHANGELOG.en.md)

All notable repository-level changes are documented here. Plugins use independent SemVer and keep their own changelogs.

## [OPUS 1.1.1] — 2026-09-02

Follow-up fix release from the final Opus 5 review.

### Repository controls

- The 90-day freshness gate is no longer a time bomb for unrelated PRs: age is a hard failure for a changed freshness-controlled reference, while a scheduled strict workflow checks the entire controlled set and synchronizes a dedicated GitHub issue.
- `CONTRACT_MATRIX.json` now includes Metrika Direct-expense duplication guard, Webmaster indexing archive lifecycle, SEO unknown Webmaster impressions, and Marketing quality metadata shape contracts.
- `PLUGIN_STANDARD` explicitly defines the contract matrix as a traceability index rather than semantic proof and states that eval fixtures are structurally validated but are not yet executed against a model.
- Cross-service `authentication: ON_USE` is documented as schema-compatible deferred-auth metadata with no local credential/transport surface.
- Marketing taxonomy is reconciled with the actual nine executable finding types plus an explicit deferred set through a normative spec amendment.

### Plugin releases

- Yandex Metrika `1.0.2`: the Direct-expense source-label guard recognizes tokenized labels while retaining the independent CSV UTM risk layer.
- Yandex Webmaster `1.0.3`: the official indexing archive `state` field (`IN_PROGRESS` / `DONE` / `FAILED`) is re-verified and pinned by regression/traceability contracts.
- Direct `1.0.1`, Wordstat `1.0.2`, Search `1.0.2`, SEO `1.0.1`, and Marketing `1.1.0` are unchanged.

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
