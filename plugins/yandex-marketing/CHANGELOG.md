# Журнал изменений — Yandex Marketing

[**Русский**](CHANGELOG.md) · [English](CHANGELOG.en.md)

> `DOCS 1.0.0` добавил bilingual README с reconciliation/orchestration diagram; SemVer плагина не изменён.

## [1.1.0] — 2026-09-02

- Добавлены stable evidence roles `canonical`, `reconciliation_only`, `enrichment`.
- Money evidence без currency/VAT/period context остаётся explicitly incomparable.
- Legacy 18-class taxonomy заменена на девять classes, реально производимых deterministic helpers; future classes deferred.
- Удалён dead `NEW_CAMPAIGN_CANDIDATE` delegation; executable routes остаются preview-only + approval in owner.
- Wordstat cap limitation propagируется.

## [1.0.1] — 2026-09-02

- Metrika quality schema, canonical reconciliation, ambiguous-demand ban, KPI/money compatibility и adversarial evals.

## [1.0.0]

- Первый cross-service paid-acquisition plugin.