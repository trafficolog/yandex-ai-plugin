# Wordstat Topic Map contract

`yandex-wordstat-topic-map` prepares evidence for later SEO architecture. It is not a final semantic-cocoon builder.

## Ownership boundary

Wordstat owns demand discovery and candidate topic mapping. Search owns SERP-overlap validation. SEO owns final page architecture and internal-link planning.

## Artifact

The deterministic helper emits `wordstat-topic-map/v1` with:

- original seeds and their filters/operators/coverage;
- normalized queries with all source seeds and Wordstat relation types;
- the first canonical `query_id` plus ordered `query_ids` containing every distinct identifier that collapsed into the normalized query;
- separate demand observations rather than summed overlapping demand;
- candidate topics with `status: CANDIDATE`;
- candidate topic relations with `status: HYPOTHESIS`;
- explicit limitations.

Each `seeds[].seed` identifier is unique within one topic-map bundle. Duplicate seed names are rejected so every phrase `source_seed` resolves to exactly one seed record and therefore to one unambiguous operators/filters/coverage context.

`query_id` is a provenance identifier. Reusing one `query_id` is allowed only when all occurrences resolve to the same normalized query text; the helper rejects one identifier that points to different normalized queries. Different identifiers may still collapse into one normalized query, but the complete ordered alias set is serialized in `query_ids` so downstream joins do not lose provenance.

Every phrase record's `source_seed` must exactly reference a declared input `seeds[].seed`. Undeclared or misspelled source seeds are rejected, preventing dangling provenance that cannot be joined back to the seed's operators, filters or coverage metadata.

Allowed topic relation labels are `RELATED`, `NARROWER`, `BROADER`, and `COMPLEMENTARY`. These are information-organization hypotheses, not Yandex ranking or page-boundary contracts. Candidate relations must connect two distinct topic IDs; self-relations such as `t1 -> t1` are invalid.

Confidence values are `LOW`, `MEDIUM`, `HIGH`. They describe evidence quality and must not be presented as calibrated probabilities.

## Coverage

When any input seed reports truncated GetTop associations, the artifact must contain `WORDSTAT_ASSOCIATIONS_CAPPED`. A capped association response cannot be described as exhaustive semantic coverage.

## Prohibited claims

The Wordstat topic-map layer must not claim that:

- overlapping phrase counts sum to unique market demand;
- Wordstat association alone proves that queries belong on one SEO page;
- a high-frequency phrase automatically requires its own page;
- candidate relations define canonical parents or internal links.
