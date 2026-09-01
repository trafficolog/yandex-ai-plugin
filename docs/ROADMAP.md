# Roadmap

## Phase 1 — Marketplace foundation

- Move the existing Yandex Direct implementation into `plugins/yandex-direct/`.
- Keep Direct at version `1.0.0` during the structural move.
- Establish root marketplace metadata, plugin standard, service matrix, repository validator, and path-aware CI.
- Keep Direct's runtime behavior and API helpers unchanged.

## Phase 2 — Yandex Metrika

Implemented as plugin `1.0.0` with ten specialized skills, quality-aware Reporting API support, safe Management/Logs/Data Import helpers, offline tests/evals and optional MCP/app execution fallback.

Key correctness rules include current attribution models, sampling/data-lag disclosure, one-year Logs requests, preview-before-write and a guard against duplicate Yandex Direct expense imports.

## Phase 3 — Yandex Webmaster

Implemented as plugin `1.0.0` with eleven specialized skills, mixed v4/v4.1 endpoint routing, query/indexing helpers, quota-aware recrawl, priority Sitemap recrawl, feeds, async archive/PRO exports and destructive-write guards.

## Phase 4 — Yandex Wordstat

Implemented as plugin `1.0.0` with nine workflow skills, Cloud Wordstat v2 helpers, provenance-aware semantics, operator-safe dynamics, regional affinity, trend classification, and quota/cost planning.

## Phase 5 — Yandex Search

Next Tier 1 plugin. Keep SERP/search retrieval separate from Wordstat demand statistics, then use real SERP overlap for SEO clustering workflows.

## Phase 6 — Cross-service workflows

Add `yandex-marketing` and `yandex-seo` after Direct/Metrika/Webmaster/Wordstat/Search interfaces are stable.

## Phase 7 — Operations, AI, mobile

Tracker, Yandex 360, Maps, AppMetrica, YandexGPT, SpeechKit.
