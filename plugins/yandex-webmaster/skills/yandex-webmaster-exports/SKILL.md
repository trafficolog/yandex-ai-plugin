---
name: yandex-webmaster-exports
description: Use when starting, checking status, or downloading Webmaster archive or PRO/search exports.
---

# Exports

Read `../../references/exports.md` and `../../references/safety.md`. Use `scripts/yw_indexing.py` for archive task paths and `scripts/yw_export.py` for PRO/search exports, lifecycle normalization, quota planning and file downloads.

Before a PRO export, read known limits from `pro/limits`, available dates from `pro/serp/dates`, and regions from `pro/regions` when needed. Starting an export can consume quota: preview dates, host-relative `/...` paths, regions and tariff choice, then require approval. Missing quota usage is `QUOTA_USAGE_UNKNOWN`, not assumed available capacity.

Check task status only when the workflow/user invokes a status check. Do **not** autonomously poll, schedule checks, or invent retry intervals. Normalize `IN_PROGRESS` as pending, `FAILED` as failed with error provenance, and `SUCCESS` as ready only when an HTTPS download URL is present. A successful response without a URL remains explicit. Treat a URL as expired only when its proven age is greater than 24 hours; unknown age stays unknown.

Large downloads go to files, never inline into model context.
