---
name: yandex-search-serp
description: Use when normalizing Yandex XML search results into reproducible SERP snapshots for downstream SEO analysis.
---
# SERP normalization

Use XML as the structured source. Treat every response field as optional. Normalize URL comparison keys conservatively and retain raw URLs. Store region, search type, grouping, page, freshness, sort, family/typo settings and `config_fingerprint`. HTML is a raw artifact only.

Structured SEO snapshots use flat grouping with `docs_in_group=1`, preserve absolute rank and `position_on_page`, and expose result-depth metadata: `max_supported_results=250`, `window_start`, `window_end` and `reaches_result_ceiling`. Reject configured windows that start at or cross past 250 and reject impossible observed ranks above 250. A window ending exactly at 250 is valid.

Competitor presence inside the observed SERP is not market share, and reaching the result ceiling is not proof of exhaustive market coverage.
