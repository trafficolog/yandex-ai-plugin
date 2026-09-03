# Changelog

[Русский](CHANGELOG.md) · [**English**](CHANGELOG.en.md)

All notable repository-level changes are documented here. Plugins use independent SemVer and keep their own changelogs.

## [OPUS 1.1.2] — 2026-09-03

Residual hardening for the remaining findings from the final Opus 5 audit.

### Fixed

- Yandex Metrika `1.0.3` closes the Direct expense provenance gap for CSV files without `UTMSource` / `UTMMedium`: official `TrafficSourceDetail=yandex_direct_star` is blocked as `DIRECT_DUPLICATION_RISK`.
- Insufficient expense provenance now fails closed as `DIRECT_SOURCE_UNVERIFIED`; generic `TrafficSource=ad` without source detail requires explicit review/`--allow-direct-risk` instead of silently passing.
- Explicit non-Direct source detail remains allowed; arbitrary provider labels such as `MyDirect` are not declared Direct from substring matching alone.
- The shared-code rule now includes an installability/distribution gate: duplication plus a stable interface is insufficient for a root runtime package until independently installed plugins can reliably receive the shared dependency.
- N3/N5/N6/N8 were re-verified against current contracts/docs and are not reopened: traceability is not semantic proof, cross-service `ON_USE` matches the marketplace schema, Webmaster `state`/`download_url` are verified, and the Marketing spec is already normatively reconciled.

### Published plugin matrix

Direct `1.0.1`, Metrika `1.0.3`, Webmaster `1.0.3`, Wordstat `1.1.1`, Search `1.0.2`, SEO `1.1.1`, Marketing `1.1.0`.

## [1.0.2] — 2026-09-03

Repository-level maintenance release for release-infrastructure hardening after Phase 7.

### Fixed

- The legacy `OPUS 1.1.1` publisher now recognizes a fully published historical release set at one ancestor SHA and completes later `main` runs as a verified no-op.
- A partial OPUS release set resumes against its already-published common SHA instead of being moved to current `main`.
- Inconsistent or multi-SHA historical release state remains a hard failure; historical tags are never retargeted or mutated.
- Added regression contract `tests/test_opus_publisher_idempotency.py` for immutable/no-op/partial-recovery semantics.
- Added the repository `1.0.2` publisher, gated on a successful `CI` push for the exact `main` SHA.

### Plugin versions unchanged

Direct `1.0.1`, Metrika `1.0.2`, Webmaster `1.0.3`, Wordstat `1.1.1`, Search `1.0.2`, SEO `1.1.1`, Marketing `1.1.0`.

## [PHASE 7 1.0.1] — 2026-09-03

Post-release hardening patch for the Topical Architecture / Semantic Cocoons baseline.

### Fixed

- Yandex Wordstat `1.1.1` rejects duplicate `seeds[].seed`, keeping `source_seed` an unambiguous provenance key.
- Yandex Wordstat `1.1.1` rejects candidate topic self-relations (`from_topic_id == to_topic_id`).
- Yandex SEO `1.1.1` normalizes `structural_tree.nodes` through an explicit field whitelist and does not carry caller execution/recommendation state (`decision`, `status`, `write`, `execution_id`).
- Yandex SEO `1.1.1` requires list-typed candidate-link `evidence`; scalar/object payloads are rejected before preview serialization.
- Service ownership, Search `1.0.2`, the transport-free SEO boundary, and preview-only internal-link semantics are unchanged.

### Published plugin matrix

Direct `1.0.1`, Metrika `1.0.2`, Webmaster `1.0.3`, Wordstat `1.1.1`, Search `1.0.2`, SEO `1.1.1`, Marketing `1.1.0`.

## [PHASE 7 1.0.0] — 2026-09-02

Evidence-first Topical Architecture / Semantic Cocoons release.

### Architecture

- Yandex Wordstat `1.1.0` adds `yandex-wordstat-topic-map` and `wordstat-topic-map/v1`: candidate-only topic maps, provenance-preserving query deduplication, separate demand observations, and explicit limitation propagation.
- Yandex Search remains `1.0.2` and the sole owner of real SERP-overlap/Jaccard clustering; Phase 7 adds no competing fuzzy-text clusterer and makes no Search runtime change.
- Yandex SEO `1.1.0` adds `yandex-seo-topical-architecture` and `seo-topical-architecture/v1` for `GREENFIELD|EXISTING_SITE`, page decisions, and separate `structural_tree` / `semantic_graph` layers.
- Yandex SEO `1.1.0` adds `yandex-seo-internal-linking`: preview-only link planning and deterministic audit with no CMS writes.

### Evidence and safety contracts

- `OBSERVED`, `DERIVED`, `HYPOTHESIS`, and `METHODOLOGY` remain distinct; semantic-cocoon/TGA/QBST methodology is not represented as a verified ranking mechanism.
- Without Search evidence, `SERP_VALIDATION_MISSING` is mandatory and page boundaries remain hypotheses.
- Wordstat associations/co-occurrence are not represented as final page boundaries and are never aggregated into fictitious total demand.
- SEO remains transport-free: no new Yandex HTTP clients, credentials, or live mutations.
- `CONTRACT_MATRIX.json` pins `wordstat.topic-map-candidate-boundary`, `seo.topical-architecture-structural-tree`, `seo.topical-architecture-evidence-classes`, and `seo.internal-linking-preview-only`.

### Published plugin matrix

Direct `1.0.1`, Metrika `1.0.2`, Webmaster `1.0.3`, Wordstat `1.1.0`, Search `1.0.2`, SEO `1.1.0`, Marketing `1.1.0`.

## [OPUS 1.1.1] — 2026-09-02

Follow-up fix release from the final Opus 5 review.

### Repository controls

- The 90-day freshness gate is no longer a time bomb for unrelated PRs: age is a hard failure for a changed freshness-controlled reference, while a scheduled strict workflow checks the entire controlled set and synchronizes a dedicated GitHub issue.
- `CONTRACT_MATRIX.json` now includes Metrika Direct-expense duplication guard, Webmaster indexing archive lifecycle, SEO unknown Webmaster impressions, and Marketing quality metadata shape contracts.
- `PLUGIN_STANDARD` explicitly defines the contract matrix as a traceability index rather than semantic proof and states that eval fixtures are structurally validated but are not yet executed against a model.
- Cross-service `authentication: ON_USE` is documented as schema-compatible deferred-auth metadata with no local credential/transport surface.
- Marketing taxonomy is reconciled with the actual nine executable finding types plus an explicit deferred set through a normative spec amendment.

### Plugin releases

- Yandex Metrika `1.0.2`: the Direct-expense source-label guard recognizes tokenized labels while retaining the independent CSV UTM risk layer.
- Yandex Webmaster `1.0.3`: the official indexing archive `state` field (`IN_PROGRESS` / `DONE` / `FAILED`) is re-verified and pinned by regression/traceability contracts.
- Direct `1.0.1`, Wordstat `1.0.2`, Search `1.0.2`, SEO `1.0.1`, and Marketing `1.1.0` are unchanged.

## [DOCS 1.0.0] — 2026-09-02

### Changed

- Russian became the primary language for root README/CHANGELOG and key repository documentation; English versions are published as `.en.md` mirrors.
- All seven production plugins gained bilingual README/CHANGELOG pairs without changing plugin SemVer.
- Added local RU/EN SVG hero banners under `docs/assets/readme/`.
- Added Mermaid orchestration diagrams to `yandex-seo` and `yandex-marketing` READMEs, making evidence flow, the no-transport boundary, and delegated previews explicit.
- Repository validation now checks bilingual pairs, reciprocal language links, and identical release markers across RU/EN changelogs.
- `docs/PLUGIN_STANDARD.md` now treats bilingual documentation as a production contract.

### Plugin versions unchanged

Direct `1.0.1`, Metrika `1.0.1`, Webmaster `1.0.2`, Wordstat `1.0.2`, Search `1.0.2`, SEO `1.0.1`, Marketing `1.1.0`.

## [OPUS 1.1.0] — 2026-09-02

Contract-hardening milestone: Wordstat association coverage cap, Search 250-result depth, Webmaster PRO lifecycle/quota semantics, Marketing evidence roles/taxonomy, and executable repository contract/freshness controls.

## [1.0.1] — 2026-09-02

Review-driven maintenance covering safe-by-default mutations/API contracts, omission-preserving Metrika attribution, cross-service evidence/context semantics, URL identity, evals, and dependency-aware CI.

## [1.0.0] — 2026-09-02

First complete marketplace release: Direct, Metrika, Webmaster, Wordstat, Search, SEO and Marketing, with a shared plugin standard, safety lifecycle, offline tests/evals, and path-aware CI.
