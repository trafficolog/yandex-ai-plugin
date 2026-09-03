---
name: yandex-seo-topical-architecture
description: Use when the user needs SEO information architecture, semantic-cocoon design, page-boundary decisions, a structural tree, or a semantic graph built from Wordstat/Search/Webmaster/Metrika evidence.
---

# SEO topical architecture

Build `seo-topical-architecture/v1` from preserved cross-service evidence. This skill owns **page architecture**, not raw data transport and not SERP clustering.

Evidence order:

1. explicit business/legal/product/site constraints;
2. Yandex Search SERP-overlap clusters when available;
3. existing-site Webmaster, Metrika and site-inventory evidence;
4. Wordstat demand/topic candidates;
5. semantic reasoning as `HYPOTHESIS`;
6. `MANUAL_REVIEW` when evidence does not support a safe decision.

Supported modes are `GREENFIELD` and `EXISTING_SITE`. Existing-site mode should prefer reconciliation over unnecessary URL creation.

Allowed page decisions: `PRESERVE`, `CREATE`, `EXPAND`, `MERGE`, `SPLIT`, `REDIRECT`, `SECTION_ONLY`, `BRIDGE`, `NO_PAGE`, `MANUAL_REVIEW`.

For empirical (`OBSERVED`/`DERIVED`) boundary-changing decisions — `CREATE`, `MERGE`, `SPLIT`, `REDIRECT`, `SECTION_ONLY`, `BRIDGE`, `NO_PAGE` — require Search-owned provenance through `SERP_OVERLAP` or `SERP_BRIDGE_RISK`. Wordstat association/frequency alone never proves a page boundary. Empirical `MERGE`/`REDIRECT` also require existing-page evidence such as `WEBMASTER_EXISTING_URL` or `METRIKA_LANDING_TRAFFIC`.

Model two independent layers:

- `structural_tree` — canonical navigation hierarchy; a page has at most one canonical structural parent;
- `semantic_graph` — many justified semantic relationships such as support, comparison, evidence, use-case or bridge relations.

Every recommendation carries evidence, `LOW|MEDIUM|HIGH` confidence as evidence quality, and claim class `OBSERVED|DERIVED|HYPOTHESIS|METHODOLOGY`. Never present `METHODOLOGY` as a verified Yandex/Google ranking mechanism.

If Search evidence is absent, disclose `SERP_VALIDATION_MISSING`; page-boundary recommendations remain hypotheses rather than proven SERP clusters. If Search evidence is incomplete, disclose `SERP_VALIDATION_PARTIAL` rather than treating partial SERP validation as complete.

Search cluster ingress validates `cluster_id`, query membership, `min_shared_urls`, `bridge_risk` and limitations. Search bridge risk and upstream Wordstat limitations propagate into the architecture artifact. `link_plan`, `audits` and consistency evaluation fields remain `null` until those stages actually run; evaluated empty results are attached explicitly.

This plugin is transport-free and read-only. It does not create pages, redirects, CMS links, recrawl requests or other consequential writes.

References: `references/topical-architecture.md`, `references/evidence-bundle.md`, `references/quality.md`, `references/safety.md`.
