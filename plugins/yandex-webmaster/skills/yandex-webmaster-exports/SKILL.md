---
name: yandex-webmaster-exports
description: Use when starting, polling or downloading Webmaster archive or PRO/search exports.
---

# Exports

Read `../../references/exports.md` and `../../references/safety.md`. Use `scripts/yw_indexing.py` for archive task paths and `scripts/yw_export.py` for PRO/search exports and file downloads.

Before PRO export read `pro/limits`, available dates and regions when needed. Starting an export can consume quota: preview dates, paths, regions and tariff choice, then require approval. Poll task status; download only when `SUCCESS`/`DONE`.

Large downloads go to files, never inline into model context.
