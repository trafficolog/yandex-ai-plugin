# Phase 7 — Post-Release Hardening normative amendment

**Date:** 2026-09-03  
**Applies to:** `seo-topical-architecture/v1`, `wordstat-topic-map/v1`, Phase 7 repository patch `1.0.1`  
**Supersedes where conflicting:** `2026-09-02-phase-7-topical-architecture-semantic-cocoons-design.md`

This amendment records the four post-release contract hardenings tracked in #27. Service ownership, schema identifiers, evidence classes, Search-owned SERP clustering, transport-free SEO and preview-only internal-link behavior remain unchanged.

## 1. Structural page-node fields

Section 10 (`Structural tree contract`) of the original Phase 7 design is amended as follows.

`structural_tree.nodes[]` is a structural/navigation artifact only. Its normalized v1 field whitelist is:

```json
{
  "page_id": "...",
  "url": "...",
  "proposed_url": null,
  "title": "...",
  "page_role": "HUB",
  "canonical_parent_id": "...",
  "breadcrumbs": [],
  "cluster_ids": [],
  "evidence": [],
  "confidence": "LOW|MEDIUM|HIGH"
}
```

The structural node MUST NOT carry recommendation, execution or write state supplied by a caller. In particular, `decision`, `status`, `write` and `execution_id` are not structural-node fields and are removed by normalization.

Page recommendations remain represented only through the bundle-level `page_decisions[]` surface. This amendment therefore supersedes the original Section 10 example that included `decision` inside a structural page node.

## 2. Internal-link evidence type

For `yandex-seo-internal-linking`, candidate-link `evidence` MUST be a list before preview serialization. Scalar strings and object payloads are invalid and MUST be rejected rather than normalized implicitly.

This does not change the preview-only/no-CMS-write boundary.

## 3. Wordstat candidate-topic relations

`wordstat-topic-map/v1` candidate relations are hypotheses between distinct topics. A relation where `from_topic_id == to_topic_id` is invalid and MUST be rejected.

Wordstat remains candidate-only and does not own final SERP clustering, final page boundaries or internal links.

## 4. Wordstat seed identity

Within one topic-map bundle, every `seeds[].seed` identifier MUST be unique. Duplicate seed identifiers are invalid and MUST be rejected before phrase normalization so `phrase_records[].source_seed` remains an unambiguous provenance key.

No new seed-ID schema is introduced by this patch.

## 5. Compatibility

This is a contract-hardening patch, not a schema-version change. Valid Phase 7 inputs that already satisfy these invariants remain valid. Inputs that relied on structural execution-state leakage, malformed link evidence, self-relations or duplicate seed identifiers are rejected or normalized according to the rules above.
