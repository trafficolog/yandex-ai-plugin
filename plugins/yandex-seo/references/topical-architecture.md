# SEO Topical Architecture contract

The normative model is **Topical Architecture**. “Semantic cocoon” remains a discoverability/methodology term, not a claim that one universal site structure is optimal.

## Ownership

- Wordstat: demand discovery and candidate topic map.
- Search: actual Yandex SERP-overlap clustering.
- SEO: page decisions, canonical structural tree, semantic graph and internal-link plan.
- Webmaster/Metrika/site inventory: optional evidence for existing-site reconciliation.

SEO introduces no cross-service transport or credentials.

## Modes

`GREENFIELD` proposes a new architecture from business scope, Wordstat candidates and Search validation where available.

`EXISTING_SITE` reconciles existing URLs and evidence. Prefer `PRESERVE`, `EXPAND`, `MERGE`, `SPLIT`, `SECTION_ONLY` or `MANUAL_REVIEW` over unnecessary new URLs when existing evidence supports that choice.

## Evidence classes

- `OBSERVED`: supplied directly by services/site inventory/user constraints.
- `DERIVED`: deterministic transformation of observed evidence.
- `HYPOTHESIS`: architectural inference.
- `METHODOLOGY`: external information-architecture heuristic.

A methodology heuristic is never silently promoted to an observed ranking fact.

Confidence is `LOW|MEDIUM|HIGH` evidence quality, not a probability.

The v1 reason-code vocabulary is finite and validated: `SERP_OVERLAP`, `SERP_BRIDGE_RISK`, `WORDSTAT_NESTED_RELATION`, `WORDSTAT_ASSOCIATION`, `WORDSTAT_DEMAND_CONTEXT`, `WORDSTAT_REGION_CONTEXT`, `WORDSTAT_SEASONAL_CONTEXT`, `WEBMASTER_QUERY_VISIBILITY`, `WEBMASTER_EXISTING_URL`, `METRIKA_LANDING_TRAFFIC`, `METRIKA_CONVERSION_CONTEXT`, `EXISTING_INTERNAL_LINK`, `EXISTING_BREADCRUMB`, `USER_BUSINESS_CONSTRAINT`, `MANUAL_ENTITY_RELATION`, `SEMANTIC_HYPOTHESIS`, `METHODOLOGY_HEURISTIC`. Unknown or misspelled reason codes are rejected rather than treated as new evidence classes.

## Structural tree

Each page has a unique `page_id` and at most one `canonical_parent_id`. The deterministic validator rejects unknown parents, cycles and duplicate URL/proposed-URL locations. No universal maximum depth is imposed.

Structural nodes are normalized through an explicit field whitelist: `page_id`, `url`, `proposed_url`, `title`, `page_role`, `canonical_parent_id`, `breadcrumbs`, `cluster_ids`, `evidence`, `confidence`. Arbitrary recommendation/transport/execution metadata such as `decision`, `status`, `write` or `execution_id` is not serialized into `structural_tree.nodes`; page decisions are the dedicated recommendation-state surface.

The normalized page-role vocabulary is `ROOT`, `HUB`, `SUPPORT`, `DETAIL`, `COMPARISON`, `TRANSACTIONAL`, `DEFINITION`, `EVIDENCE`, `BRIDGE`, `UTILITY`, `OTHER`. A **proposed** page with no `canonical_parent_id` must explicitly declare `page_role: ROOT` or `page_role: BRIDGE`; this prevents accidental orphan proposed roots. Existing-site observed URL roots are not retroactively forced to supply a proposed-page role.

When `breadcrumbs` are supplied, they are treated as a structural assertion: every breadcrumb page must exist and the ordered list must exactly match the canonical ancestor chain from root to the node's parent. Omitting the `breadcrumbs` field remains allowed; the helper does not invent a breadcrumb contract that the caller did not supply.

## Semantic graph

Semantic relationships are independent from structural parenthood. Allowed initial relations:

`PARENT_CONTEXT`, `CHILD_DETAIL`, `SIBLING`, `SUPPORT`, `DEFINITION`, `COMPARISON`, `ALTERNATIVE`, `EVIDENCE`, `USE_CASE`, `NEXT_STEP`, `TRANSACTIONAL_PATH`, `BRIDGE`, `COMPLIANCE`.

These are repository information-architecture labels, not asserted search-engine internal edge types. Every semantic edge must carry at least one validated `reason_code` from the approved v1 vocabulary. If an edge is justified only by `SEMANTIC_HYPOTHESIS` and/or `METHODOLOGY_HEURISTIC`, it cannot use empirical `OBSERVED` or `DERIVED` claim classes.

A semantic edge must connect two distinct pages, so self-referential `p1 -> p1` edges are rejected. Directed cycles across two or more distinct pages remain valid semantic-graph structures; the repository does not impose a universal acyclic semantic-graph rule.

## Missing SERP validation

When `coverage.search=MISSING`, output must disclose `SERP_VALIDATION_MISSING`. Search-owned cluster records are not valid in that state, and Search-owned reason codes `SERP_OVERLAP` / `SERP_BRIDGE_RISK` cannot be used on page decisions, semantic edges, or preview internal-link candidates while Search coverage is missing. Wordstat, Webmaster, Metrika, inventory, user and methodology provenance remain independently usable where their own contracts allow it.

Boundary-changing decisions such as `CREATE`, `MERGE`, `SPLIT`, `REDIRECT`, `SECTION_ONLY`, `BRIDGE` or `NO_PAGE` must remain `HYPOTHESIS` while Search evidence is missing. An observed `PRESERVE` decision for an existing page may remain `OBSERVED` when supported by existing-site evidence.

## Recommendation state

Page decisions are normalized as `status: PREVIEW`. Caller-supplied execution/write metadata is not propagated into the architecture artifact, so destructive or migration-oriented recommendations cannot be represented as already executed by this transport-free plugin. A page may have at most one normalized decision in an architecture bundle; duplicate decisions for the same `page_id` are rejected instead of allowing contradictory states.

When `reason_codes` are supplied on a page decision, every code is validated against the same finite v1 vocabulary used by semantic edges and link-plan records. A decision justified only by `SEMANTIC_HYPOTHESIS` and/or `METHODOLOGY_HEURISTIC` cannot use empirical `OBSERVED` or `DERIVED` claim classes. Empirical `OBSERVED` or `DERIVED` decisions must carry at least one provenance source through validated `reason_codes` or a non-empty `evidence` list; a provenance-free empirical decision is rejected. The `evidence` field itself is list-typed: scalar strings or objects are rejected rather than treated as truthy provenance.

When a page decision supplies `target_page_id`, it must be a non-empty identifier for a page already present in the same architecture bundle. `MERGE` and `REDIRECT` targets must differ from the source `page_id`, so self-merge and self-redirect previews are rejected. When a decision supplies `target_url`, that value must be a non-empty string; for `MERGE` or `REDIRECT`, it must also differ from the source page's known `url` or `proposed_url`. If both `target_page_id` and a `target_url` that belongs to a known architecture node are supplied, both target representations must resolve to the same page. Unknown/external target URLs are not rejected merely because they have no in-bundle owner. Target fields remain optional; this validation does not invent a mandatory target for decisions that do not supply one.

For `MERGE` and `REDIRECT`, known in-bundle targets form a migration graph. That destructive target graph must be acyclic: mixed redirect/merge loops of any length are rejected. A known `target_url` participates in this check by resolving to its architecture page; external or otherwise unknown target URLs are not fabricated into graph nodes. This destructive migration constraint is separate from the semantic graph, where multi-page cycles remain legal.

## Mutable facts / SSoT

Optional `fact_sets` may register one canonical page owner and known consumers for mutable facts such as prices, legal terms, regional availability or specifications. This is content-governance consistency, not a ranking contract.
