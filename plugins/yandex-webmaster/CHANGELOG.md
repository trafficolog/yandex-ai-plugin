# Журнал изменений — Yandex Webmaster

[**Русский**](CHANGELOG.md) · [English](CHANGELOG.en.md)

> `DOCS 1.0.0` добавил bilingual docs; SemVer плагина не изменён.

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