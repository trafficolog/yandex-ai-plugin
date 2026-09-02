---
name: yandex-webmaster-indexing
description: Use when analyzing crawl/indexing history, pages in search, search events or important URLs.
---

# Indexing

Read `../../references/indexing.md`. Use `scripts/yw_indexing.py`.

Keep three concepts separate: fetched/crawled, indexed, and present in search. Check history and search events before proposing recrawl. Exclusion/removal reasons are evidence; do not claim a recrawl guarantees inclusion or ranking.

For full page archive, start the async task only after approval, poll `task_id` until `DONE|FAILED`, then pass the download URL to the export/file workflow.
