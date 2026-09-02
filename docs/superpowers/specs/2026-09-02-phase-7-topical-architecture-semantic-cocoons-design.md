# Phase 7 — Topical Architecture & Semantic Cocoons design

**Date:** 2026-09-02  
**Status:** approved in-chat architecture, pending written-spec review  
**Base:** `main` at `0b4745361adc752b819845ec85de141b65e93710`  
**Target branch:** `phase-7-topical-architecture-design`  
**Tracking issue:** #23

## 1. Purpose

Phase 7 adds semantic-cocoon / topical-architecture capabilities without turning Yandex Wordstat into a general SEO architect and without breaking the repository's existing service boundaries.

The central architectural decision is:

```text
Wordstat -> candidate demand/topic map
Search   -> SERP-overlap validation and clustering
SEO      -> page architecture, structural tree, semantic graph, internal-link plan
Webmaster/Metrika -> existing-site evidence enrichment
```

The feature is explicitly **evidence-first**. Every page decision, relationship and internal-link recommendation must retain provenance, confidence and limitations. Methodological ideas from semantic-cocoon literature may guide architecture, but undocumented ranking mechanisms must never be represented as verified search-engine contracts.

## 2. Why this belongs across three plugins

Current repository ownership already defines the correct split:

- `yandex-wordstat-semantics` owns seed expansion, associations, frequency provenance and candidate semantics;
- `yandex-search-clustering` owns real SERP-overlap clustering and explicit overlap parameters;
- `yandex-seo-clusters` enriches Search-owned clusters with Wordstat, Webmaster and Metrika evidence.

A semantic cocoon is broader than keyword collection. The reviewed sources consistently combine topic research, page structure and internal linking. Modern variants go further by separating navigational hierarchy from semantic relationships. Therefore a complete cocoon cannot be safely owned by Wordstat alone.

## 3. Source-derived principles and evidence hierarchy

### 3.1 Principles accepted into the design

The following ideas are sufficiently consistent across the reviewed material to use as architecture concepts:

1. **Semantic discovery precedes architecture.** Keyword and user-demand research supplies candidate topics; it does not by itself prove page boundaries.
2. **A cocoon is both structural and semantic.** Classical descriptions distinguish site/page hierarchy from semantic justification for links.
3. **Internal links should answer a user/context relationship, not exist merely to create link density.**
4. **Modern architecture benefits from separating a structural tree and a semantic graph.** The Cocoon 4.0 / TGA material explicitly models these as different layers.
5. **Existing-site work requires audit and reconciliation.** Orphans, cannibalization, duplicate intent, outdated pages and inconsistent navigation must be handled before blindly creating new pages.
6. **Continuous measurement matters.** Search visibility and user-behavior evidence can be used to revise architecture after publication.

### 3.2 Evidence classes

Phase 7 must keep four evidence classes distinct:

- `OBSERVED` — directly present in Wordstat, Search, Webmaster, Metrika, user-provided crawl/site inventory or explicit user constraints;
- `DERIVED` — deterministic transformation of observed evidence, for example SERP Jaccard, source aggregation or graph-integrity checks;
- `HYPOTHESIS` — an architectural inference such as a proposed page split, bridge or semantic relationship;
- `METHODOLOGY` — a non-vendor methodology or heuristic imported from semantic-cocoon literature.

No `METHODOLOGY` claim may be silently upgraded to `OBSERVED` or `DERIVED`.

### 3.3 Concepts that remain heuristic only

The following reviewed claims must **not** become repository ranking contracts unless separately verified from authoritative sources:

- QBST as a mandatory Google ranking mechanism;
- `siteFocusScore`, proprietary `TopicAuthority` formulas, fixed `LinkValue` formulas or fixed coefficient weights;
- claims that one exact cocoon depth, word count, page-role count or link direction is universally optimal;
- claims that embeddings or entity counts alone prove a good internal link;
- fixed ranking/traffic uplift percentages from secondary articles;
- conclusions from a single field case as general causal proof.

These may appear as optional heuristics with provenance such as `methodology_source`, never as guaranteed search-engine behavior.

## 4. Scope

Phase 7 introduces three primary public capabilities:

1. `yandex-wordstat-topic-map`
2. `yandex-seo-topical-architecture`
3. `yandex-seo-internal-linking`

It also updates routers, references, evals, README/CHANGELOG pairs, service matrix and contract traceability.

No new top-level plugin is introduced.

## 5. Non-goals

Phase 7 does not:

- move SERP clustering ownership out of `yandex-search`;
- make Wordstat associations equivalent to semantic clusters;
- create or edit CMS pages automatically;
- execute internal-link changes;
- generate production content as part of the architecture workflow;
- invent live search/demand numbers;
- introduce new cross-service HTTP clients or credentials into `yandex-seo`;
- use embeddings as a substitute for Search SERP evidence when Search evidence is available;
- encode proprietary Google/Yandex algorithm claims as facts;
- define universal `min_shared_urls`, Jaccard, volume, traffic, depth, word-count or internal-link-count thresholds.

## 6. Plugin responsibilities

### 6.1 Yandex Wordstat

Wordstat owns **demand discovery**, not page architecture.

New skill:

```text
yandex-wordstat-topic-map
```

Use when the user needs a demand-oriented topic map, seed-to-topic expansion, candidate subtopics or a structured input for later SEO architecture.

Responsibilities:

- accept one or many seeds;
- reuse GetTop/associations/frequency/dynamics/regions evidence;
- preserve every source seed and query expression;
- normalize duplicate phrases without summing overlapping demand;
- create **candidate** topic groupings and candidate relations;
- attach region, period, operator and coverage metadata;
- propagate `WORDSTAT_ASSOCIATIONS_CAPPED` when applicable;
- explicitly label output as pre-SERP candidate architecture.

It must not emit final `page`, `canonical_parent`, `internal_link` or `cocoon_complete` claims.

### 6.2 Yandex Search

Search remains the owner of **SERP validation and clustering**.

No new public skill is required for the first Phase 7 release. Existing `yandex-search-clustering` is the canonical validator.

Responsibilities remain:

- use actual Yandex SERP snapshots;
- preserve top-K and result-depth constraints;
- use explicit `min_shared_urls`/overlap settings supplied by the workflow/user;
- expose pairwise overlap/Jaccard and bridge risk;
- avoid fuzzy-text-only clustering claims.

Phase 7 may add integration examples/references but must not create a second clustering algorithm in Wordstat or SEO.

### 6.3 Yandex SEO

SEO owns **cross-service topical architecture**.

New skills:

```text
yandex-seo-topical-architecture
yandex-seo-internal-linking
```

`yandex-seo-topical-architecture` consumes Wordstat topic candidates, Search clusters and optional Webmaster/Metrika/site-inventory evidence. It decides what architecture is supportable by the available evidence.

`yandex-seo-internal-linking` converts an approved topical architecture into a justified link graph and audits an existing link graph.

The phrase **semantic cocoon** belongs in skill descriptions and documentation for discoverability, but the normative internal model is called **Topical Architecture** because it supports both classic tree-shaped cocoons and modern graph-oriented architectures.

## 7. Operating modes

### 7.1 Greenfield mode

Inputs:

- business/site scope;
- seed topics;
- Wordstat topic-map evidence;
- Search clusters where available;
- optional manually supplied product/service/entity constraints.

Output focuses on proposed architecture:

```text
candidate topics
-> SERP-validated clusters
-> page decisions
-> canonical structural tree
-> semantic graph
-> internal-link plan
```

When Search evidence is absent, page boundaries remain `HYPOTHESIS` and the output must disclose `SERP_VALIDATION_MISSING`.

### 7.2 Existing-site mode

Inputs additionally include existing URLs/pages and, where available:

- Webmaster query/impression/indexing evidence;
- Metrika landing/traffic/conversion evidence;
- existing navigation/breadcrumb/internal-link inventory;
- canonical/redirect/status metadata supplied by the user or crawl.

The workflow must prefer reconciliation over unnecessary URL creation.

Allowed page decisions:

- `PRESERVE`
- `CREATE`
- `EXPAND`
- `MERGE`
- `SPLIT`
- `REDIRECT`
- `SECTION_ONLY`
- `BRIDGE`
- `NO_PAGE`
- `MANUAL_REVIEW`

Every destructive or migration-oriented recommendation remains a preview/recommendation only; actual changes belong to the owning CMS/deployment workflow outside these plugins.

## 8. Wordstat Topic Map Bundle

Proposed normalized contract:

```json
{
  "schema": "wordstat-topic-map/v1",
  "topic_map_id": "...",
  "scope": {
    "market": "...",
    "regions": [],
    "period": null
  },
  "seeds": [
    {
      "seed": "...",
      "operators": "...",
      "filters": {},
      "coverage": {}
    }
  ],
  "queries": [
    {
      "query_id": "...",
      "text": "...",
      "source_seeds": [],
      "relations": ["nested", "association"],
      "demand_observations": [],
      "regions": [],
      "dynamics": null
    }
  ],
  "candidate_topics": [
    {
      "topic_id": "...",
      "label": "...",
      "query_ids": [],
      "candidate_intents": [],
      "reasons": [],
      "confidence": "LOW|MEDIUM|HIGH",
      "status": "CANDIDATE"
    }
  ],
  "candidate_relations": [
    {
      "from_topic_id": "...",
      "to_topic_id": "...",
      "relation": "RELATED|NARROWER|BROADER|COMPLEMENTARY",
      "evidence": [],
      "status": "HYPOTHESIS"
    }
  ],
  "limitations": []
}
```

`confidence` is evidence-quality classification, not an invented probability.

## 9. Topical Architecture Bundle

SEO produces a separate cross-service artifact:

```json
{
  "schema": "seo-topical-architecture/v1",
  "architecture_id": "...",
  "mode": "GREENFIELD|EXISTING_SITE",
  "coverage": {
    "wordstat": "COMPLETE|PARTIAL|MISSING",
    "search": "COMPLETE|PARTIAL|MISSING",
    "webmaster": "COMPLETE|PARTIAL|MISSING",
    "metrika": "COMPLETE|PARTIAL|MISSING",
    "site_inventory": "COMPLETE|PARTIAL|MISSING"
  },
  "clusters": [],
  "page_decisions": [],
  "structural_tree": {
    "nodes": [],
    "edges": []
  },
  "semantic_graph": {
    "nodes": [],
    "edges": []
  },
  "link_plan": [],
  "consistency": {
    "mutable_fact_sets": [],
    "navigation_conflicts": [],
    "parity_checks": []
  },
  "audits": [],
  "limitations": []
}
```

## 10. Structural tree contract

The structural tree models navigation, not every semantic relationship.

Each page node has at most one `canonical_parent_id` unless it is a root. This follows the useful part of the Cocoon 4.0/TGA distinction: one canonical structural home prevents a page from appearing as a structural child of multiple branches while still allowing many semantic relationships in the graph.

Normative page-role vocabulary for v1:

- `ROOT`
- `HUB`
- `SUPPORT`
- `DETAIL`
- `COMPARISON`
- `TRANSACTIONAL`
- `DEFINITION`
- `EVIDENCE`
- `BRIDGE`
- `UTILITY`
- `OTHER`

These are information-architecture roles, not search-engine ranking classes.

Page-node fields:

```json
{
  "page_id": "...",
  "url": "...",
  "proposed_url": null,
  "title": "...",
  "page_role": "HUB",
  "decision": "PRESERVE|CREATE|...",
  "canonical_parent_id": "...",
  "breadcrumbs": [],
  "cluster_ids": [],
  "evidence": [],
  "confidence": "LOW|MEDIUM|HIGH"
}
```

The tree validator must detect:

- multiple canonical parents;
- structural cycles;
- orphan proposed pages without an explicit root/bridge reason;
- duplicate proposed URLs;
- parent/URL/breadcrumb contradictions where those fields are supplied.

No maximum tree depth is universal.

## 11. Semantic graph contract

Semantic edges are independent from the structural parent relation.

Initial relation taxonomy:

- `PARENT_CONTEXT`
- `CHILD_DETAIL`
- `SIBLING`
- `SUPPORT`
- `DEFINITION`
- `COMPARISON`
- `ALTERNATIVE`
- `EVIDENCE`
- `USE_CASE`
- `NEXT_STEP`
- `TRANSACTIONAL_PATH`
- `BRIDGE`
- `COMPLIANCE`

These names describe information architecture; they do **not** claim search engines have identical internal edge types.

Every edge requires:

```json
{
  "from_page_id": "...",
  "to_page_id": "...",
  "relation": "SUPPORT",
  "user_need": "...",
  "reason_codes": [],
  "evidence": [],
  "confidence": "LOW|MEDIUM|HIGH",
  "claim_class": "OBSERVED|DERIVED|HYPOTHESIS|METHODOLOGY"
}
```

## 12. Evidence reason codes

Initial deterministic vocabulary:

- `SERP_OVERLAP`
- `SERP_BRIDGE_RISK`
- `WORDSTAT_NESTED_RELATION`
- `WORDSTAT_ASSOCIATION`
- `WORDSTAT_DEMAND_CONTEXT`
- `WORDSTAT_REGION_CONTEXT`
- `WORDSTAT_SEASONAL_CONTEXT`
- `WEBMASTER_QUERY_VISIBILITY`
- `WEBMASTER_EXISTING_URL`
- `METRIKA_LANDING_TRAFFIC`
- `METRIKA_CONVERSION_CONTEXT`
- `EXISTING_INTERNAL_LINK`
- `EXISTING_BREADCRUMB`
- `USER_BUSINESS_CONSTRAINT`
- `MANUAL_ENTITY_RELATION`
- `SEMANTIC_HYPOTHESIS`
- `METHODOLOGY_HEURISTIC`

An edge based only on `SEMANTIC_HYPOTHESIS` or `METHODOLOGY_HEURISTIC` cannot be described as empirically validated.

## 13. Page-boundary decision rules

Search evidence is the strongest repository-native signal for deciding whether two query groups should share a page, but it is not the only business constraint.

Decision order:

1. preserve explicit legal/product/site constraints;
2. use Search cluster evidence where available;
3. use existing URL/query/landing evidence in existing-site mode;
4. use Wordstat relationships for candidate expansion and demand context;
5. use semantic reasoning only as a hypothesis layer;
6. escalate ambiguous cases to `MANUAL_REVIEW` rather than invent certainty.

The workflow must never say that high Wordstat frequency automatically deserves its own page.

## 14. Consistency / SSoT layer

A useful Cocoon 4.0 idea is retained as an optional **consistency layer** rather than a ranking claim.

For mutable facts such as prices, rates, product specifications, legal conditions, regional availability or dates, architecture may register a canonical fact owner:

```json
{
  "fact_set_id": "...",
  "subject": "...",
  "canonical_page_id": "...",
  "consumers": [],
  "dimensions": ["region", "product", "period"],
  "verification_required": true
}
```

Purpose: prevent contradictory content and duplicated maintenance. This is repository information-architecture governance, not a claim about a specific ranking algorithm.

## 15. Internal-linking skill

`yandex-seo-internal-linking` supports two workflows:

### Design

Given an approved Topical Architecture Bundle, produce a **preview-only** link plan with:

- source page;
- target page;
- relation type;
- user need;
- suggested placement/context, if known;
- candidate anchor concept, not forced exact-match text;
- evidence and confidence;
- warnings for duplicate intent or weak justification.

### Audit

Given an existing link inventory, identify:

- orphan pages;
- structural links that contradict the canonical parent model;
- semantically unjustified links;
- duplicate/competing links where the same intent has no distinct user benefit;
- broken bridges between otherwise related topic groups;
- cycles only when they create a navigation/UX problem, not merely because cycles exist in a graph.

The skill must not claim that exact anchor distance, exact word windows or fixed link counts are universal SEO requirements.

## 16. Cannibalization and duplicate-intent handling

Phase 7 reuses `yandex-seo-cannibalization` rather than duplicating it.

Topical architecture sends suspected conflicts to the cannibalization workflow with context:

- competing query clusters;
- existing URLs;
- Search evidence;
- Webmaster visibility;
- Metrika landing evidence;
- proposed page decision.

The result may change a provisional `CREATE` into `EXPAND`, `MERGE`, `SECTION_ONLY` or `NO_PAGE`.

## 17. Quality and integrity audits

The architecture helper should implement deterministic checks for:

- one canonical structural parent per page;
- no structural cycles;
- unique page/URL identifiers;
- every semantic edge references known nodes;
- every proposed link has a non-empty `user_need` and at least one reason code;
- every page decision retains evidence and claim class;
- Search-missing page-boundary decisions expose the limitation;
- Wordstat association-cap limitations propagate downstream;
- existing-site destructive recommendations are never marked as executed;
- no unsupported proprietary ranking claim appears in machine output.

## 18. Helper boundaries

Expected helpers:

### Wordstat

`plugins/yandex-wordstat/scripts/ywstat_topic_map.py`

Deterministic responsibilities:

- merge source query records while retaining seed provenance;
- attach coverage/region/period metadata;
- create normalized candidate-topic inputs;
- validate that no total-demand summation is invented;
- serialize the Topic Map Bundle.

The helper does not perform final LLM clustering or Search requests.

### SEO

`plugins/yandex-seo/scripts/seo_topical_architecture.py`

Deterministic responsibilities:

- validate/normalize Topical Architecture Bundle;
- enforce structural-tree invariants;
- validate page-role/relation taxonomy and evidence fields;
- propagate source coverage/limitations;
- audit duplicate parents/orphans/unknown nodes;
- generate deterministic quality findings.

`plugins/yandex-seo/scripts/seo_internal_linking.py`

Deterministic responsibilities:

- validate link-plan records;
- detect unjustified/duplicate structural relationships;
- check node existence and relation constraints;
- provide audit summaries.

LLM reasoning may propose architecture hypotheses, but helpers validate them before they are presented as a bundle.

## 19. Skill routing changes

### Wordstat router

Add:

```text
yandex-wordstat-topic-map — demand-oriented topic mapping and pre-SERP candidate architecture.
```

`yandex-wordstat-semantics` remains the lower-level semantic expansion skill.

### SEO router

Add routing terms for:

- semantic cocoon;
- topical map / topical architecture;
- site architecture from semantic core;
- hub/support page architecture;
- internal linking architecture;
- existing-site semantic restructuring.

Route architecture requests to `yandex-seo-topical-architecture`; route approved-link-plan/audit requests to `yandex-seo-internal-linking`.

## 20. Evaluation scenarios

Minimum new eval coverage should include:

### Wordstat

1. multi-seed topic map with duplicate phrases and preserved provenance;
2. association cap propagates to topic-map limitations;
3. operator/region context remains attached;
4. user asks for final pages from Wordstat-only evidence -> output remains candidate / warns that SERP validation is missing;
5. no overlapping row summation into total market demand.

### SEO topical architecture

1. greenfield with full Wordstat + Search evidence;
2. greenfield without Search -> hypotheses + limitation;
3. existing site where proposed new page would cannibalize an existing URL;
4. merge two existing URLs based on evidence, but keep action preview-only;
5. one semantic topic belongs to multiple graph relationships but only one structural parent;
6. invalid two-parent structural tree rejected;
7. inter-cocoon bridge with explicit user need accepted;
8. heuristic-only QBST/TGA-style claim stays `METHODOLOGY`/`HYPOTHESIS`;
9. Wordstat capped associations propagate to final architecture limitations;
10. missing Webmaster/Metrika does not fail globally.

### SEO internal linking

1. parent/support links with explicit justification;
2. semantic bridge outside the structural branch;
3. orphan detection;
4. duplicate target with no distinct user need flagged;
5. exact-anchor/15-word rule requested as universal requirement -> skill refuses to present it as a verified Yandex rule.

## 21. Contract-matrix additions

Expected traceability entries:

- `wordstat.topic-map-candidate-not-final-cluster`
- `wordstat.topic-map-provenance-preserved`
- `seo.topical-architecture-search-owns-clustering`
- `seo.topical-architecture-single-canonical-parent`
- `seo.topical-architecture-evidence-classification`
- `seo.topical-architecture-missing-search-limitation`
- `seo.internal-linking-user-need-required`
- `seo.semantic-methodology-not-ranking-fact`

As established in OPUS 1.1.1, the matrix remains a traceability index; semantic correctness is enforced by the referenced tests, not inferred merely from path presence.

## 22. Documentation

Update RU-primary and EN mirror documentation consistently:

### Wordstat

- README / README.en
- CHANGELOG / CHANGELOG.en
- new `references/topic-map.md`
- semantics/research references as needed

### SEO

- README / README.en
- CHANGELOG / CHANGELOG.en
- new `references/topical-architecture.md`
- new `references/internal-linking.md`
- update sources/evidence/quality references

### Root

- README orchestration diagram to show `Wordstat -> Search -> SEO Topical Architecture`;
- SERVICE_MATRIX RU/EN;
- root CHANGELOG RU/EN;
- CONTRACT_MATRIX.

## 23. Independent SemVer and release identity

Because the release adds new public skills/capabilities without breaking existing contracts:

| Plugin | Current | Target | Reason |
| --- | ---: | ---: | --- |
| `yandex-wordstat` | 1.0.2 | **1.1.0** | new public topic-map capability |
| `yandex-search` | 1.0.2 | 1.0.2 | existing clustering contract reused |
| `yandex-seo` | 1.0.1 | **1.1.0** | new topical-architecture + internal-linking capabilities |
| all others | current | unchanged | evidence providers only |

The repository-level release tag for this phase is fixed as:

```text
phase-7-topical-architecture-1.0.0
```

Plugin SemVer remains independent.

## 24. Source assessment

The design reviewed the user-provided materials as methodology sources, not vendor API documentation.

### Strongly used concepts

- DrMax semantic cocoon: structural + semantic aspects, contextual internal linking, classical hierarchy and later semantic-link emphasis.
- Sape semantic cocoon guide: keyword research (including Wordstat), content hierarchy, internal linking and iterative measurement.
- AffGate Cocoon 4.0 / Topical Graph Architect: separate structural tree and semantic graph, canonical home, relation justification, consistency/SSoT and existing-site audit concepts.
- Evgeniy Zaharenko: summary of classical hierarchy, modern semantic-link interpretation and practical workflow.
- Sales-Hacking semantic-cocoon guide: intent-oriented topic research, structure, linking, governance and measurement; fixed performance claims are not adopted.

### Used only as heuristic inspiration

- 1888.center Semantic Cocoon 3.0 and Nepolyakov QBST/Cocoons: useful vocabulary around entities, graph thinking and link-context analysis, but proprietary formulas, `QBST`, fixed weights and asserted ranking mechanisms are not accepted as facts.
- Kofelatte/Pikabu field case: treated as anecdotal project evidence, not a general causal guarantee.

### Source access note

The Seciva URL and some original localized pages were not directly retrievable during the design research session. No normative requirement in this spec depends on claims that could not be independently read from the accessible reviewed sources.

## 25. Acceptance criteria for implementation

Phase 7 implementation is complete only when:

1. Wordstat exposes a discoverable topic-map skill and deterministic bundle helper.
2. Wordstat output cannot masquerade as final SERP clustering.
3. Search remains the sole owner of real SERP-overlap clustering.
4. SEO exposes topical-architecture and internal-linking skills.
5. Topical Architecture Bundle separates `structural_tree` from `semantic_graph`.
6. One canonical structural parent per page is enforced.
7. Every graph/link relation contains user need, evidence/reason and claim class.
8. Greenfield and existing-site modes both have regression/eval coverage.
9. Missing Search/Wordstat/Webmaster/Metrika is represented through explicit coverage and limitations rather than fabricated evidence.
10. Methodological ranking claims remain marked as methodology/hypothesis.
11. RU/EN docs, manifests, marketplaces and changelogs are version-consistent.
12. Contract matrix entries point to real skills/helpers/tests/references.
13. Full repository CI passes on exact PR head and post-merge main before releases are published.

## 26. Design decision summary

Phase 7 intentionally does **not** implement a monolithic `yandex-wordstat-cocoons` skill.

The normative pipeline is:

```text
Wordstat Semantics
        |
        v
Wordstat Topic Map
(candidate demand graph)
        |
        v
Yandex Search Clustering
(real SERP-overlap validation)
        |
        v
SEO Topical Architecture
  |                |
  v                v
Structural Tree   Semantic Graph
  |                |
  +-------+--------+
          v
 SEO Internal-Link Plan
          |
          v
Webmaster/Metrika feedback for existing-site iteration
```

This preserves the repository's service ownership while adding a substantially richer SEO information-architecture layer.