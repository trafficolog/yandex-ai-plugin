---
name: yandex-wordstat-semantics
description: Use when the user needs seed expansion, a semantic core candidate set, related queries, or structured Wordstat keyword data.
---

# Wordstat semantics

Use GetTop per seed. Treat `results` as nested/popular phrases and `associations` as a distinct similar-query relation. Normalize counts but preserve relation types and full **provenance**: every merged phrase keeps all seeds that produced it.

Preserve GetTop coverage metadata. Cloud associations are capped at 20; when `coverage.associations_truncated` is true, propagate an explicit limitation such as `WORDSTAT_ASSOCIATIONS_CAPPED` and do not describe the returned association set as exhaustive semantic coverage.

Never sum overlapping row counts or association counts and label them **total demand**, market size, or unique searches. Keep Yandex `totalCount` per individual seed/expression instead.

Wordstat co-occurrence is candidate generation, not final SEO clustering. Do not claim SERP overlap without a real search-results source.

For large collections, store JSON/file output with filters, backend, timestamp, relation types, source seeds, and coverage limitations.

References: `references/semantics.md`, `references/api-2026.md`.
