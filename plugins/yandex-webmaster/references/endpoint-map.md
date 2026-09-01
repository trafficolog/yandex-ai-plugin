# Endpoint version map — verified 2026-09-01

Use resource-specific versions.

## v4

- `/v4/user`
- `/v4/user/{user-id}/hosts`
- host info, verification, summary, diagnostics
- `/indexing/history`
- `/indexing/archive/` and `/indexing/archive/{task-id}`
- `/search-urls/in-search/history`
- `/search-urls/events/history`
- `/search-queries/popular`
- `/search-queries/all/history`
- `/search-queries/{query-id}/history`
- `/query-analytics/list`
- `/recrawl/queue`, `/recrawl/quota`
- `/sitemaps`, `/user-added-sitemaps`
- `/feeds/*`
- `/pro/regions`, `/pro/limits`, `/pro/serp/dates`, `/pro/serp/queries/download/*`

## v4.1

- `GET /v4.1/user/{user-id}/hosts/{host-id}/sitemaps/recrawl`
- `POST /v4.1/user/{user-id}/hosts/{host-id}/sitemaps/{sitemap-id}/recrawl`

Bundled helpers restrict the version string to `v4` or `v4.1`; specialized Sitemap helpers choose the correct version rather than accepting a user-supplied version override.
