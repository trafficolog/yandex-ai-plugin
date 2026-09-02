---
name: yandex-seo-internal-linking
description: Use when the user needs an evidence-first internal-link plan, semantic-link graph, orphan-page audit, or comparison of existing links against an approved topical architecture.
---

# SEO internal linking

Consume an approved `seo-topical-architecture/v1` artifact. Produce **preview-only** internal-link recommendations or audit an existing link inventory.

Each proposed link must identify source page, target page, semantic relation, user need, reason codes, evidence, confidence (`LOW|MEDIUM|HIGH`) and claim class (`OBSERVED|DERIVED|HYPOTHESIS|METHODOLOGY`). Optional anchor output is an **anchor concept**, not a forced exact-match phrase.

Do not impose universal link-count, anchor-density, word-distance or exact-match requirements. Reject instructions that require an exact-match anchor as a ranking rule.

Audit mode may report deterministic findings such as:

- `ORPHAN_PAGE`;
- `STRUCTURAL_PARENT_LINK_MISSING`;
- `MISSING_JUSTIFIED_LINK`;
- `UNKNOWN_LINK_ENDPOINT`.

A semantic graph may contain legitimate cycles (for example overview → detail → overview). Do not label graph cycles as errors unless a separate UX/navigation analysis proves a concrete problem.

This skill does not edit CMS content, navigation, templates or links. Consequential writes remain outside the transport-free Yandex SEO plugin.

References: `references/internal-linking.md`, `references/topical-architecture.md`, `references/safety.md`.
