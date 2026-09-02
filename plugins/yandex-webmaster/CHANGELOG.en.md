# Changelog — Yandex Webmaster

[Русский](CHANGELOG.md) · [**English**](CHANGELOG.en.md)

> `DOCS 1.0.0` added bilingual docs; plugin SemVer is unchanged.

## [1.0.2] — 2026-09-02

- Corrected PRO export `use_pro_tariff` serialization and host-relative path validation.
- Added deterministic lifecycle normalization, missing/expired states and 24-hour age handling without autonomous polling.
- Quota planning distinguishes known remaining quota from unknown usage.

## [1.0.1] — 2026-09-02

- Corrected feed batch body to `{"feeds": [...]}`.
- Strengthened credential redaction and HTTPS-only artifact downloads.
- Added verifiable eval expectations for destructive/quota-consuming workflows.

## [1.0.0] — 2026-09-01

- Initial Yandex Webmaster plugin.