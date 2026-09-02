# Semantic collection

Use GetTop as candidate generation, not final SEO clustering.

1. Start with explicit seed phrases and geography/device constraints.
2. Request GetTop for each seed.
3. Keep `results` (nested/popular phrases) separate from `associations` (similar phrases).
4. Convert count strings to integers.
5. Deduplicate by normalized phrase while preserving all source seeds and relation types.
6. Write large collections to JSON/files instead of flooding agent context.

Counts overlap. Never sum rows and call the result **total demand**, market size, or unique searches. Yandex `totalCount` is meaningful for the specific request expression that produced it; keep it per seed/expression.

Do not claim Wordstat co-occurrence is real SERP-overlap clustering. That belongs to Yandex Search/SEO cross-service workflows.
