# SEO Internal Linking contract

Internal-linking recommendations are a **preview layer** over an approved Topical Architecture Bundle. The SEO plugin never performs CMS writes.

## Required evidence

Every proposed link records:

- distinct source and target page IDs; a self-link preview where `from_page_id == to_page_id` is rejected;
- semantic relation;
- explicit user need/context;
- at least one non-empty reason code plus evidence/context when available;
- confidence class `LOW|MEDIUM|HIGH`;
- claim class `OBSERVED|DERIVED|HYPOTHESIS|METHODOLOGY`.

When `evidence` is supplied on a candidate link, it is list-typed. Scalar strings and objects are rejected before preview serialization so downstream list consumers never receive schema-invalid evidence payloads.

`METHODOLOGY` edges remain methodology. An anchor concept is optional guidance, not a mandatory exact-match phrase.

Reason codes are validated against the same finite v1 vocabulary used by Topical Architecture: `SERP_OVERLAP`, `SERP_BRIDGE_RISK`, `WORDSTAT_NESTED_RELATION`, `WORDSTAT_ASSOCIATION`, `WORDSTAT_DEMAND_CONTEXT`, `WORDSTAT_REGION_CONTEXT`, `WORDSTAT_SEASONAL_CONTEXT`, `WEBMASTER_QUERY_VISIBILITY`, `WEBMASTER_EXISTING_URL`, `METRIKA_LANDING_TRAFFIC`, `METRIKA_CONVERSION_CONTEXT`, `EXISTING_INTERNAL_LINK`, `EXISTING_BREADCRUMB`, `USER_BUSINESS_CONSTRAINT`, `MANUAL_ENTITY_RELATION`, `SEMANTIC_HYPOTHESIS`, `METHODOLOGY_HEURISTIC`. Unknown or misspelled codes are rejected instead of being treated as empirical evidence.

Reason-code provenance and claim class must remain compatible on both approved semantic edges and preview link-plan records. If every reason code is only `METHODOLOGY_HEURISTIC` and/or `SEMANTIC_HYPOTHESIS`, the edge/link cannot be labeled `OBSERVED` or `DERIVED`. A mixed reason set that also contains valid empirical repository evidence is not automatically downgraded; its claim class still has to be supportable by the supplied evidence.

## Audit findings

The deterministic audit may emit:

- `ORPHAN_PAGE` — a non-root architecture page has no observed valid internal links;
- `STRUCTURAL_PARENT_LINK_MISSING` — canonical parent → child navigation/supporting link is absent from supplied inventory;
- `MISSING_JUSTIFIED_LINK` — an approved semantic edge has no matching observed directed link;
- `UNJUSTIFIED_LINK` — an observed known-endpoint link matches neither a canonical structural parent→child relation nor an approved semantic edge;
- `UNKNOWN_LINK_ENDPOINT` — supplied inventory references a page outside the architecture.

These findings describe the supplied architecture/inventory contract. They do not prove ranking impact. `UNJUSTIFIED_LINK` means “not justified by the supplied architecture artifact,” not “harmful for rankings.”

## Cycles

Semantic cycles are legal. Overview → detail → overview or comparison paths can be useful. Do not reject a semantic graph merely because it contains a directed cycle. A cycle becomes a problem only when separate evidence identifies a concrete navigation, UX or crawl issue. This does not permit a preview self-link recommendation: self-links are rejected independently from multi-page semantic-cycle handling.

## Prohibited universal rules

Do not claim one universal optimal number of links, fixed anchor density, exact word-distance window, exact-match anchor requirement, or mandatory link direction for all sites.
