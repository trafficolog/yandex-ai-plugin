# Changelog — Yandex Marketing

[Русский](CHANGELOG.md) · [**English**](CHANGELOG.en.md)

> `DOCS 1.0.0` added a bilingual README with reconciliation/orchestration diagrams; plugin SemVer is unchanged.

## [1.1.0] — 2026-09-02

- Added stable evidence roles `canonical`, `reconciliation_only`, `enrichment`.
- Money evidence without currency/VAT/period context remains explicitly incomparable.
- Replaced the legacy 18-class taxonomy with the nine classes actually produced by deterministic helpers; future classes are deferred.
- Removed dead `NEW_CAMPAIGN_CANDIDATE` delegation; executable routes remain preview-only with approval in the owner.
- Propagated the Wordstat cap limitation.

## [1.0.1] — 2026-09-02

- Aligned Metrika quality shape, canonical reconciliation, ambiguous-demand guard, KPI/money compatibility and adversarial evals.

## [1.0.0]

- Initial cross-service paid-acquisition plugin.