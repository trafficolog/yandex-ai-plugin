# Журнал изменений — Yandex Metrika

[**Русский**](CHANGELOG.md) · [English](CHANGELOG.en.md)

## [1.0.2] — 2026-09-02

- Усилен Direct expense duplication guard: помимо exact aliases блокируются явные tokenized labels (`Yandex Direct RU`, `direct_ads`, `Яндекс Директ агентство`).
- CSV-content guard по `UTMSource` / `UTMMedium` остаётся независимым вторым слоем и сохраняет explicit `--allow-direct-risk` override.
- Arbitrary substring вроде `MyDirect` не объявляется Direct provenance без дополнительного evidence.
- Guard добавлен в repository contract matrix как high-risk traceability contract.

## [1.0.1] — 2026-09-02

- Усилено обнаружение duplicate-risk для Yandex Direct expense imports.
- Reporting attribution metadata сохраняет explicit-vs-omitted provenance без invented default.
- Nested producer quality metadata сохранена для cross-service consumers.
- Добавлены verifiable eval expectations для reporting, imports, Logs и write safety.

## [1.0.0] — 2026-09-01

- Первый Yandex Metrika plugin: специализированные analytics/data-quality/goals/Logs/import skills и dependency-light helpers с preview-before-write.
