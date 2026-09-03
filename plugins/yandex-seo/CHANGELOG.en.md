# Changelog — Yandex SEO

[Русский](CHANGELOG.md) · [**English**](CHANGELOG.en.md)

## [1.1.2] — 2026-09-03

- Empirical boundary-changing decisions (`CREATE|MERGE|SPLIT|REDIRECT|SECTION_ONLY|BRIDGE|NO_PAGE`) now require Search-owned provenance; `MERGE`/`REDIRECT` also require existing-page/URL evidence.
- `coverage.search=PARTIAL` now adds explicit `SERP_VALIDATION_PARTIAL`; Search cluster ingress is validated and bridge/source limitations propagate downstream automatically.
- `METHODOLOGY` is now a first-class qualitative kind in the SEO Evidence Bundle, but it cannot masquerade as quantitative metric evidence.
- Topical Architecture distinguishes not-evaluated `link_plan`/`audits` (`null`) from evaluated empty results through explicit attachment helpers.
- Internal-link audit defines orphaning by missing inbound links, preserves and flags duplicate links, and marks a rootless `BRIDGE` without inbound links as orphan/broken bridge. Explicit `ROOT` and a legacy parentless node without `page_role` remain exempt; explicit non-root roles are still audited for orphaning. Self-links are reported as `SELF_LINK` and excluded from valid/inbound reachability counts.
- Transport-free, preview-only, and Search-owned clustering boundaries remain unchanged.

## [1.1.1] — 2026-09-03

- `structural_tree.nodes` now use an explicit field whitelist; caller `decision/status/write/execution_id` state cannot leak into the transport-free structural artifact.
- Candidate-link `evidence` in `yandex-seo-internal-linking` must now be a list; scalar/object payloads are rejected before preview serialization.
- Topical Architecture ownership, Search-owned SERP clustering, and the preview-only/no-CMS-write boundary remain unchanged.

## [1.1.0] — 2026-09-02

- Added `yandex-seo-topical-architecture` and schema `seo-topical-architecture/v1` for `GREENFIELD` / `EXISTING_SITE` architecture workflows.
- Separated `structural_tree` from `semantic_graph`: the canonical structural parent stays singular while semantic relations may be many-to-many.
- Added page decisions `PRESERVE|CREATE|EXPAND|MERGE|SPLIT|REDIRECT|SECTION_ONLY|BRIDGE|NO_PAGE|MANUAL_REVIEW`.
- Explicitly validates evidence classes `OBSERVED|DERIVED|HYPOTHESIS|METHODOLOGY` and confidence `LOW|MEDIUM|HIGH`; methodology is never promoted to a ranking fact.
- Adds `SERP_VALIDATION_MISSING` when Search evidence is unavailable; Search remains the owner of SERP-overlap clustering.
- Added `yandex-seo-internal-linking` for preview-only link plans and deterministic audit findings (`ORPHAN_PAGE`, `STRUCTURAL_PARENT_LINK_MISSING`, `MISSING_JUSTIFIED_LINK`, `UNKNOWN_LINK_ENDPOINT`).
- SEO remains transport-free/read-only and performs no CMS writes.

## [1.0.1] — 2026-09-02

- Enforced required Evidence Bundle context (`site`, `analysis_period`, `search_region_id`).
- Added explicit period/geography/Search-config/device alignment states.
- Prevented missing Webmaster impressions from becoming measured zero and propagated quality/coverage limitations.
- Delegated previews remain non-writing orchestration.

## [1.0.0]

- Initial cross-service SEO Evidence Bundle, findings and delegated-action workflows.