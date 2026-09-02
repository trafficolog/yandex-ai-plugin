# Changelog — Yandex Direct

[Русский](CHANGELOG.md) · [**English**](CHANGELOG.en.md)

> Repository release `DOCS 1.0.0` added the RU/EN documentation mirror; plugin SemVer is unchanged.

## [1.0.1] — 2026-09-02

- Made API method safety allowlist-based: unknown and mutating methods are preview-first by default.
- Made Reports attribution/goals explicit, removed obsolete `IncludeDiscount`, and retry the first HTTP 500 once.
- Added KPI provenance metadata sidecars for TSV reports without inventing currency.
- Added regression eval expectations for write safety and report context.

## [1.0.0] — 2026-09-01

- Split monolithic Direct knowledge into 8 discoverable skills.
- Updated core API workflow to v501 and an EPK-first model.
- Added safe API and Reports helpers, autotargeting/shared-negative guidance, offline tests and marketplace manifests.