# Roadmap

## Phase 1 — Marketplace foundation

- Move the existing Yandex Direct implementation into `plugins/yandex-direct/`.
- Keep Direct at version `1.0.0` during the structural move.
- Establish root marketplace metadata, plugin standard, service matrix, repository validator, and path-aware CI.
- Keep Direct's runtime behavior and API helpers unchanged.

## Phase 2 — Yandex Metrika

Next implementation target. Build to the same standard as Direct:

- router + specialized reporting/conversion/ecommerce/attribution/logs/goals skills;
- current official API reference;
- safe management operations;
- compact cache-aware reporting patterns;
- tests and offline evals;
- optional MCP/app execution adapter with bundled/file fallback.

Use `mkultraaaa/claude-yandex-skills` as a workflow donor and `theYahia/YaAll` as a capability/MCP reference, with official Yandex docs as source of truth.

## Phase 3 — Yandex Webmaster

Implement indexing, diagnostics, queries, sitemaps, recrawl, links, and safe management operations.

## Phase 4 — Wordstat + Search

Ship as separate plugins. Demand statistics and web SERP/search are distinct product domains even where Yandex Search infrastructure overlaps.

## Phase 5 — Cross-service workflows

Add `yandex-marketing` and `yandex-seo` after Direct/Metrika/Webmaster/Wordstat/Search interfaces are stable.

## Phase 6 — Operations, AI, mobile

Tracker, Yandex 360, Maps, AppMetrica, YandexGPT, SpeechKit.
