# SEO Internal Linking contract

Internal-linking recommendations are a **preview layer** over an approved Topical Architecture Bundle. The SEO plugin never performs CMS writes.

## Required evidence

Every proposed link records:

- source and target page IDs;
- semantic relation;
- explicit user need/context;
- reason codes and evidence;
- confidence class `LOW|MEDIUM|HIGH`;
- claim class `OBSERVED|DERIVED|HYPOTHESIS|METHODOLOGY`.

`METHODOLOGY` edges remain methodology. An anchor concept is optional guidance, not a mandatory exact-match phrase.

## Audit findings

The deterministic audit may emit:

- `ORPHAN_PAGE` — a non-root architecture page has no observed valid internal links;
- `STRUCTURAL_PARENT_LINK_MISSING` — canonical parent → child navigation/supporting link is absent from supplied inventory;
- `MISSING_JUSTIFIED_LINK` — an approved semantic edge has no matching observed directed link;
- `UNKNOWN_LINK_ENDPOINT` — supplied inventory references a page outside the architecture.

These findings describe the supplied architecture/inventory contract. They do not prove ranking impact.

## Cycles

Semantic cycles are legal. Overview → detail → overview or comparison paths can be useful. Do not reject a semantic graph merely because it contains a directed cycle. A cycle becomes a problem only when separate evidence identifies a concrete navigation, UX or crawl issue.

## Prohibited universal rules

Do not claim one universal optimal number of links, fixed anchor density, exact word-distance window, exact-match anchor requirement, or mandatory link direction for all sites.
