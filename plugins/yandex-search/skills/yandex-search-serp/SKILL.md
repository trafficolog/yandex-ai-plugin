---
name: yandex-search-serp
description: Use when normalizing Yandex XML search results into reproducible SERP snapshots for downstream SEO analysis.
---
# SERP normalization

Use XML as the structured source. Treat every response field as optional. Normalize URL comparison keys conservatively and retain raw URLs. Store region, search type, grouping, page, freshness, sort, family/typo settings and `config_fingerprint`. HTML is a raw artifact only.
