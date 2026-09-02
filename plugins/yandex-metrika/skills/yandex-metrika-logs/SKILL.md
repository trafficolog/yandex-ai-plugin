---
name: yandex-metrika-logs
description: Use when exporting or managing non-aggregated Yandex Metrika visit/hit data through Logs API.
---

# Work with Logs API

Read `../../references/logs.md` and `../../references/safety.md`.

Follow the lifecycle exactly:

`evaluate → create → poll status → download every part → clean`

Reject a request period over one year. Choose `hits` versus `visits` and fields explicitly. Logs API does not support request-level filtering, so plan downstream filtering outside the creation request.

Creating a Logs request mutates server-side state; cleaning prepared logs is consequential. Preview/approval is required for both in agent workflows.

Save downloaded parts to files; do not flood the context window with raw TSV data. `../../scripts/ym_logs.py` implements endpoint construction, period validation, safe previews and part download.
