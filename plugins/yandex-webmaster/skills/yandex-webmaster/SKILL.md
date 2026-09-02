---
name: yandex-webmaster
description: Use when the request concerns Yandex Webmaster broadly or spans multiple Webmaster capabilities and needs routing.
---

# Yandex Webmaster router

Read `../../references/api-2026.md` and `../../references/safety.md` when API behavior or state changes matter.

## Route the task

- SEO health / diagnostics → `yandex-webmaster-audit`
- hosts / verification / add or delete site → `yandex-webmaster-site-management`
- search demand, impressions, clicks, positions → `yandex-webmaster-search-queries`
- crawl, indexing, pages in search, search events → `yandex-webmaster-indexing`
- ordinary URL recrawl → `yandex-webmaster-recrawl`
- sitemap discovery/configuration/priority recrawl → `yandex-webmaster-sitemaps`
- internal/external/broken links → `yandex-webmaster-links`
- YML feeds → `yandex-webmaster-feeds`
- archive or PRO/search export → `yandex-webmaster-exports`
- raw endpoint/payload debugging → `yandex-webmaster-api`

Resolve user/host from account data when possible instead of guessing opaque IDs. Consequential actions follow `read → analyze → preview → explicit approval → write → verify`.

Execution fallback: compatible connected app/MCP → bundled helpers → user exports/files.
