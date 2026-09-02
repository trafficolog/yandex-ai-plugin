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

## Structural tree

Each page has a unique `page_id` and at most one `canonical_parent_id`. The deterministic validator rejects unknown parents, cycles and duplicate URL/proposed-URL locations. No universal maximum depth is imposed.

The normalized page-role vocabulary is `ROOT`, `HUB`, `SUPPORT`, `DETAIL`, `COMPARISON`, `TRANSACTIONAL`, `DEFINITION`, `EVIDENCE`, `BRIDGE`, `UTILITY`, `OTHER`. A **proposed** page with no `canonical_parent_id` must explicitly declare `page_role: ROOT` or `page_role: BRIDGE`; this prevents accidental orphan proposed roots. Existing-site observed URL roots are not retroactively forced to supply a proposed-page role.

## Semantic graph

Semantic relationships are independent from structural parenthood. Allowed initial relations:

`PARENT_CONTEXT`, `CHILD_DETAIL`, `SIBLING`, `SUPPORT`, `DEFINITION`, `COMPARISON`, `ALTERNATIVE`, `EVIDENCE`, `USE_CASE`, `NEXT_STEP`, `TRANSACTIONAL_PATH`, `BRIDGE`, `COMPLIANCE`.

These are repository information-architecture labels, not asserted search-engine internal edge types.

## Missing SERP validation

When `coverage.search=MISSING`, output must disclose `SERP_VALIDATION_MISSING`. Boundary-changing decisions such as `CREATE`, `MERGE`, `SPLIT`, `REDIRECT`, `SECTION_ONLY`, `BRIDGE` or `NO_PAGE` must remain `HYPOTHESIS` while Search evidence is missing. An observed `PRESERVE` decision for an existing page may remain `OBSERVED` when supported by existing-site evidence.

## Recommendation state

Page decisions are normalized as `status: PREVIEW`. Caller-supplied execution/write metadata is not propagated into the architecture artifact, so destructive or migration-oriented recommendations cannot be represented as already executed by this transport-free plugin.

## Mutable facts / SSoT

Optional `fact_sets` may register one canonical page owner and known consumers for mutable facts such as prices, legal terms, regional availability or specifications. This is content-governance consistency, not a ranking contract.
