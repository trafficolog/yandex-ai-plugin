---
name: yandex-webmaster-api
description: Use when raw Yandex Webmaster endpoint, payload, authentication or API debugging is required.
---

# Webmaster API

Read `../../references/api-2026.md` and `../../references/endpoint-map.md`. Use `scripts/yw_api.py` for generic requests.

The API surface is mixed: do not globally replace v4 with v4.1. Specialized helpers choose v4.1 only for resources documented there. OAuth previews must redact tokens. POST/PUT/PATCH/DELETE are preview-only unless explicitly executed after approval.
