# Журнал изменений — Yandex Direct

[**Русский**](CHANGELOG.md) · [English](CHANGELOG.en.md)

> Repository release `DOCS 1.0.0` добавил RU/EN documentation mirror; SemVer плагина не изменён.

## [1.0.1] — 2026-09-02

- API safety переведён на allowlist: unknown и mutating methods preview-first по умолчанию.
- Reports attribution/goals стали explicit; удалён obsolete `IncludeDiscount`; первый HTTP 500 ретраится один раз.
- TSV reports получили KPI provenance metadata sidecars без выдумывания currency.
- Добавлены regression eval expectations для write safety и report context.

## [1.0.0] — 2026-09-01

- Монолитные знания Direct разделены на 8 discoverable skills.
- Core API workflow обновлён до v501 и EPK-first модели.
- Добавлены safe API helper, Reports helper, autotargeting/shared negatives guidance, offline tests и marketplace manifests.