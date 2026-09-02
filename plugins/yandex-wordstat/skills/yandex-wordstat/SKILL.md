---
name: yandex-wordstat
description: Use when a request broadly involves Yandex Wordstat demand, keyword frequency, semantics, seasonality, regions, operators, trends, or raw Wordstat API work.
---

# Yandex Wordstat router

Route to the smallest relevant workflow:

- `yandex-wordstat-research` — end-to-end demand research.
- `yandex-wordstat-semantics` — multi-seed semantic expansion and provenance.
- `yandex-wordstat-frequency` — one/few expressions and frequency interpretation.
- `yandex-wordstat-dynamics` — historical monthly/weekly demand.
- `yandex-wordstat-regions` — regional volume/share/affinity.
- `yandex-wordstat-trends` — growth/noise/seasonality classification.
- `yandex-wordstat-operators` — operator semantics and compatibility.
- `yandex-wordstat-api` — raw Cloud v2 requests, auth, quota and pricing.

Never invent live numbers. If no compatible live backend exists, request/use an export or explain the methodology and missing data. Preserve filters and exact query expressions with results.

References: `references/api-2026.md`, `references/safety.md`.
