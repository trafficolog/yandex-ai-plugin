# Журнал изменений — Yandex Direct

[**Русский**](CHANGELOG.md) · [English](CHANGELOG.en.md)

## [2.0.0] — 2026-09-03

- Breaking safety contract: consequential Direct writes теперь требуют exact `preview_id`; одного `--execute` недостаточно.
- Новый flow: preview → approval exact preview в следующем пользовательском turn → `--execute --approve <preview_id>`.
- Approval связывает service, method, `Client-Login`, environment, body и pseudonymous HMAC-SHA256 auth-principal binding; смена OAuth token или payload инвалидирует permission без раскрытия token.
- API/account/file content трактуется как данные, а не инструкции; adjacent service work маршрутизируется в owning plugin.

Migration:

```bash
# 1.x
python scripts/yd_api.py campaigns update --params-file update.json --execute
# 2.0.0
python scripts/yd_api.py campaigns update --params-file update.json
python scripts/yd_api.py campaigns update --params-file update.json --execute --approve <preview_id>
```

## [1.0.1] — 2026-09-02

- API safety переведён на allowlist: unknown и mutating methods preview-first по умолчанию.
- Reports attribution/goals стали explicit; удалён obsolete `IncludeDiscount`; первый HTTP 500 ретраится один раз.
- TSV reports получили KPI provenance metadata sidecars без выдумывания currency.
- Добавлены regression eval expectations для write safety и report context.

## [1.0.0] — 2026-09-01

- Монолитные знания Direct разделены на 8 discoverable skills.
- Core API workflow обновлён до v501 и EPK-first модели.
- Добавлены safe API helper, Reports helper, autotargeting/shared negatives guidance, offline tests и marketplace manifests.