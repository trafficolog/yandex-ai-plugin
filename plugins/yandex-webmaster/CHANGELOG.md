# Changelog

## 1.0.2 — 2026-09-02

- Corrected PRO export `use_pro_tariff` serialization to documented string values and required host-relative paths beginning with `/`.
- Added deterministic `IN_PROGRESS`/`SUCCESS`/`FAILED` lifecycle normalization, explicit missing/expired download states, and 24-hour URL-age handling without autonomous polling.
- Added quota planning that distinguishes known remaining quota from unknown usage instead of assuming missing quota metadata is available capacity.

## 1.0.1 — 2026-09-02

- Corrected feed batch-add request body to the documented `{"feeds": [...]}` shape.
- Redacted embedded URL credentials in previews while preserving execute payloads.
- Restricted archive/PRO artifact downloads to absolute HTTPS URLs.
- Added verifiable eval expectations for destructive/quota-consuming workflows.

## 1.0.0 — 2026-09-01

- Initial Yandex Webmaster plugin.