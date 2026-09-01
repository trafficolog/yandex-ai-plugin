---
name: yandex-direct-api
description: Use when constructing or debugging raw Yandex Direct API requests, v501 endpoints, OAuth headers, pagination, reports polling, JSON payloads, agency Client-Login, or safe write execution.
---

# Yandex Direct API v501

Read `../../references/api-2026.md` and `../../references/safety.md`.

## Core rules

- Use lowercase service names under `https://api.direct.yandex.com/json/v501/` for current EPK workflows.
- Send OAuth with `Authorization: Bearer ...`; add `Client-Login` only when operating for the intended agency client.
- For `get`, honor `LimitedBy`/paging semantics instead of assuming the first page is complete.
- For Reports, repeat byte-equivalent request parameters during 201/202 polling and respect `retryIn`.
- Use `returnMoneyInMicros: false` for human-facing report money, but remember report filter money is still expressed in millionths.
- In JavaScript, preserve potentially large IDs as strings to avoid IEEE-754 rounding. Python integers are safe.

## Mutation safety

Default to dry-run/preview for add/update/delete/suspend/resume/archive/unarchive and bid/strategy changes. Show service, method, object IDs, current values if known, and payload. Execute only after explicit approval.

## Local helper

`../../scripts/yd_api.py` is a dependency-free v501 helper. Read operations execute by default; known write methods preview by default and require `--execute`.

Example preview:

```bash
python scripts/yd_api.py campaigns update --params-file update.json
```

Execute only after reviewing the preview:

```bash
python scripts/yd_api.py campaigns update --params-file update.json --execute
```
