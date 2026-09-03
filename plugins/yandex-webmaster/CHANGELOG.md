# Журнал изменений — Yandex Webmaster

[**Русский**](CHANGELOG.md) · [English](CHANGELOG.en.md)

## [2.0.0] — 2026-09-03

- Breaking safety contract: consequential POST/PUT/PATCH/DELETE больше не выполняются только по `--execute`; после отдельного later-turn user approval требуется `--execute --approve <preview_id>` для exact preview.
- Live write boundary `yw_api.py` связывает approval с method/path/query/body/API version и fail-closed при missing/mismatched approval.
- Embedded URL Basic Auth credentials редактируются из preview и связываются domain-separated HMAC-SHA256 с Yandex OAuth token как ключом; это не публикует deterministic password verifier, а смена credentials или OAuth key инвалидирует approval.
- API/account/file content считается untrusted data, а не инструкциями; generic permission не переносится на новый payload.

Migration:

```bash
# 1.x
python scripts/yw_api.py user/42/hosts/https:example.com/sitemaps --method POST --body '{"url":"https://example.com/sitemap.xml"}' --execute
# 2.0.0
python scripts/yw_api.py user/42/hosts/https:example.com/sitemaps --method POST --body '{"url":"https://example.com/sitemap.xml"}'
python scripts/yw_api.py user/42/hosts/https:example.com/sitemaps --method POST --body '{"url":"https://example.com/sitemap.xml"}' --execute --approve <preview_id>
```

## [1.0.3] — 2026-09-02

- Официально перепроверен indexing archive status contract: response использует `state`, значения `IN_PROGRESS`, `DONE`, `FAILED`, а `download_url` относится к completed `DONE` state.
- Regression tests закрепляют `state` и намеренно не принимают недокументированный `status` fallback.
- Archive lifecycle добавлен как отдельный high-risk contract в repository traceability matrix.

## [1.0.2] — 2026-09-02

- Исправлена PRO export serialization `use_pro_tariff` и validation host-relative paths.
- Добавлена deterministic lifecycle normalization, missing/expired states и 24h age handling без autonomous polling.
- Quota planning различает known remaining quota и unknown usage.

## [1.0.1] — 2026-09-02

- Исправлен feed batch body `{"feeds": [...]}`.
- Усилены credential redaction и HTTPS-only artifact downloads.
- Добавлены verifiable eval expectations для destructive/quota-consuming workflows.

## [1.0.0] — 2026-09-01

- Первый Yandex Webmaster plugin.
