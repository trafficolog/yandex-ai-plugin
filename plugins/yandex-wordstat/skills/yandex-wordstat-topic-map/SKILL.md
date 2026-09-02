---
name: yandex-wordstat-topic-map
description: Use when the user needs a demand-oriented topic map, seed-to-topic expansion, candidate subtopics, or structured Wordstat input for later SEO architecture.
---

# Wordstat topic map

Build a **candidate** demand/topic map from Wordstat evidence. Reuse seed expansion, GetTop nested phrases and associations, frequency, dynamics and regional evidence where available. Preserve every source seed, query expression, filter, period and coverage limitation.

The normalized artifact is `wordstat-topic-map/v1`. Deduplicate equivalent query text without summing overlapping demand observations. Keep all source seeds and relation types attached to the normalized query.

Candidate topic assignments and relations are hypotheses supplied by the reasoning layer and validated by the deterministic helper. Use confidence classes `LOW`, `MEDIUM`, `HIGH` as evidence-quality labels, not probabilities.

This skill **does not decide final SEO page boundaries**. It must not emit final `page`, `canonical_parent`, `internal_link` or completed-cocoon claims. Wordstat co-occurrence and associations are candidate discovery signals only.

When Search evidence is available, route final cluster validation through `yandex-search-clustering`. Route final page architecture and semantic-cocoon design through `yandex-seo-topical-architecture`.

If any seed has truncated GetTop associations, propagate `WORDSTAT_ASSOCIATIONS_CAPPED` and do not claim exhaustive semantic coverage.

References: `references/topic-map.md`, `references/semantics.md`, `references/api-2026.md`.
