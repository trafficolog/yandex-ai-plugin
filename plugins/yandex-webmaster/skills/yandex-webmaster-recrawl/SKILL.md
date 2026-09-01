---
name: yandex-webmaster-recrawl
description: Use when checking recrawl quota or preparing/submitting URLs for ordinary recrawl.
---

# Ordinary recrawl

Read `../../references/recrawl.md` and `../../references/safety.md`. Use `scripts/yw_recrawl.py`.

Required order: read quota → inspect queue/task state → validate URL belongs to selected host → analyze whether recrawl addresses the issue → preview exact URL → explicit approval → POST → verify task.

`URL_ALREADY_ADDED` is an idempotent already-queued result. Do not retry it repeatedly or consume more quota unnecessarily. Recrawl is not an indexing/ranking guarantee.
