---
name: yandex-metrika-api
description: Use when debugging or constructing low-level Yandex Metrika Management, Reporting, Logs or Data Import API requests that are not covered by a higher-level workflow.
---

# Low-level Metrika API

Read `../../references/api-2026.md` and the domain-specific reference before constructing a request.

Use OAuth from environment/app credentials only. Never put tokens in skill text, commands intended for logs, reports or repository files.

Prefer specialized helpers for reports, Logs and imports. Use `../../scripts/ym_api.py` for Management API reads/writes that do not justify a dedicated helper.

GET requests are read-first. POST/PUT/PATCH/DELETE are consequential and default to a redacted dry-run preview; execute only after explicit approval and verify by reading the object/status back.

When an API response or field is unclear, verify against current Yandex documentation rather than inferring behavior from an older donor project.
