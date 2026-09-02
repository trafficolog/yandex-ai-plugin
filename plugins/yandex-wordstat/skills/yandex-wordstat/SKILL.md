---
name: yandex-wordstat
description: Use when a request broadly involves Yandex Wordstat demand, keyword frequency, semantics, topic maps, seasonality, regions, operators, trends, or raw Wordstat API work.
---

# Yandex Wordstat router

Route to the smallest relevant workflow:

- `yandex-wordstat-research` — end-to-end demand research.
- `yandex-wordstat-semantics` — multi-seed semantic expansion and provenance.
- `yandex-wordstat-topic-map` — candidate demand/topic map for later Search + SEO validation.
- `yandex-wordstat-frequency` — one/few expressions and frequency interpretation.
- `yandex-wordstat-dynamics` — historical monthly/weekly demand.
- `yandex-wordstat-regions` — regional volume/share/affinity.
- `yandex-wordstat-trends` — growth/noise/seasonality classification.
- `yandex-wordstat-operators` — operator semantics and compatibility.
- `yandex-wordstat-api` — raw Cloud v2 requests, auth, quota and pricing.

Never invent live numbers. If no compatible live backend exists, request/use an export or explain the methodology and missing data. Preserve filters and exact query expressions with results.

Wordstat owns demand discovery, not final SEO page architecture. Route real SERP-overlap validation to `yandex-search-clustering` and final topical architecture/internal-link decisions to the Yandex SEO plugin.

References: `references/api-2026.md`, `references/topic-map.md`, `references/safety.md`.
