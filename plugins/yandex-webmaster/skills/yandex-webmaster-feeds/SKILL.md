---
name: yandex-webmaster-feeds
description: Use when listing, uploading, checking or deleting feeds in Yandex Webmaster.
---

# Feeds

Read `../../references/feeds.md` and `../../references/safety.md`. Use `scripts/yw_feeds.py`.

Feed mutations require an HTTPS host. For async add: validate URL/type/regions → preview → approval → `feeds/add/start` → poll `feeds/add/info` by requestId → report status. Batch add is limited to 50 items by the documented API.

Feed deletion uses batch remove and is destructive. Preview the exact URLs and require approval before execution.
