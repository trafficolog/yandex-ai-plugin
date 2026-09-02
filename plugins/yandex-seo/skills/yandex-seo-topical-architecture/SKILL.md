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

Model two independent layers:

- `structural_tree` — canonical navigation hierarchy; a page has at most one canonical structural parent;
- `semantic_graph` — many justified semantic relationships such as support, comparison, evidence, use-case or bridge relations.

Every recommendation carries evidence, `LOW|MEDIUM|HIGH` confidence as evidence quality, and claim class `OBSERVED|DERIVED|HYPOTHESIS|METHODOLOGY`. Never present `METHODOLOGY` as a verified Yandex/Google ranking mechanism.

If Search evidence is absent, disclose `SERP_VALIDATION_MISSING`; page-boundary recommendations remain hypotheses rather than proven SERP clusters.

This plugin is transport-free and read-only. It does not create pages, redirects, CMS links, recrawl requests or other consequential writes.

References: `references/topical-architecture.md`, `references/evidence-bundle.md`, `references/quality.md`, `references/safety.md`.
