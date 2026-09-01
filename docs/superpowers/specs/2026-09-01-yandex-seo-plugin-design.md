# Yandex SEO Cross-Service Plugin Design

**Status:** approved in-chat design, pending written-spec review
**Date:** 2026-09-01
**Target version:** `yandex-seo` 1.0.0
**Stacking base:** `phase-5-yandex-search`

## 1. Purpose

`yandex-seo` is the first cross-service plugin in the marketplace. It composes stable capabilities from Yandex Wordstat, Search, Webmaster, and Metrika into evidence-based SEO analysis without duplicating their API clients or bypassing their safety contracts.

The plugin must answer cross-service questions such as:

- where demand exists but site visibility is weak;
- which query clusters represent real content gaps;
- where multiple own URLs appear to compete for the same intent;
- where CTR or organic conversion underperforms the site's own comparable baseline;
- which technical/indexing issues block otherwise valuable opportunities;
- how to prioritize SEO actions transparently from available evidence.

`yandex-seo` 1.0.0 is read/analyze/recommend/preview only. It does not execute live Webmaster, Metrika, Search, or Wordstat writes.

## 2. Scope and boundaries

### In scope

- cross-service orchestration over Wordstat, Search, Webmaster, and Metrika;
- partial capability modes when only some source plugins/data are available;
- canonical SEO Evidence Bundle;
- provenance-preserving query, URL, period, geography, and data-quality joins;
- content-gap, cannibalization, CTR, organic conversion, technical-impact, and opportunity analysis;
- transparent prioritization without opaque universal scores;
- delegated action previews pointing to the owning service plugin.

### Out of scope for 1.0.0

- direct calls to Yandex APIs;
- storage/database/warehouse infrastructure;
- live recrawl, sitemap, feed, goal, counter, campaign, or other writes;
- scheduled rank monitoring;
- universal SEO benchmark thresholds;
- fuzzy/stemming-based query merging by default;
- automatic deletion of URL query parameters;
- opaque AI-generated opportunity scores;
- `yandex-marketing` workflows.

## 3. Architecture

The cross-service layer operates on artifacts and structured outputs produced by service plugins.

```text
Wordstat ───── demand / trends / regions
Search ─────── SERP / clusters / competitors / snapshots
Webmaster ─── visibility / queries / indexing / diagnostics
Metrika ───── organic visits / landings / goals / conversions
      │
      ▼
SEO Evidence Bundle
      │
      ├── normalize
      ├── align context
      ├── join evidence
      ├── propagate quality limitations
      ├── derive findings
      └── prioritize
             ↓
      SEO action plan
             ↓
 delegated service-plugin preview
```

The plugin must not contain HTTP clients for Yandex endpoints. `scripts/` contains only pure data transformation and analysis helpers.

## 4. Installation boundary and dependencies

`plugins/yandex-seo/` is an independently installable/versioned plugin.

It may operate in four capability modes:

| Mode | Required evidence | Supported analysis |
| --- | --- | --- |
| Discovery | Wordstat + Search | demand, intent, clusters, content-gap candidates |
| Visibility | Search + Webmaster | SERP visibility, competitors, ranking/coverage gaps |
| Performance | Webmaster + Metrika | impression → click → visit → conversion analysis |
| Full SEO | Wordstat + Search + Webmaster + Metrika | complete opportunity analysis |

Missing sources do not make the plugin fail globally. Output must state coverage, unavailable analyses, and limitations.

## 5. Skills

`yandex-seo` 1.0.0 contains ten discoverable skills:

1. `yandex-seo` — router and capability detection;
2. `yandex-seo-audit` — full cross-service SEO audit;
3. `yandex-seo-opportunities` — evidence-based opportunity discovery;
4. `yandex-seo-clusters` — enrich Search clusters with demand/visibility/performance evidence;
5. `yandex-seo-content-gaps` — identify validated content gaps;
6. `yandex-seo-cannibalization` — identify multi-URL intent competition candidates;
7. `yandex-seo-ctr` — CTR opportunity analysis using Webmaster evidence and own-site baselines;
8. `yandex-seo-conversions` — organic landing/conversion analysis using Webmaster + Metrika;
9. `yandex-seo-technical` — correlate diagnostics/indexing blockers with valuable query/page opportunities;
10. `yandex-seo-prioritize` — transparent ordering of findings and delegated action previews.

## 6. Canonical SEO Evidence Bundle

The bundle is the stable internal contract of Phase 6A.

```json
{
  "version": 1,
  "context": {
    "site": "example.com",
    "analysis_period": {"from": "2026-08-01", "to": "2026-08-31"},
    "search_region_id": 213,
    "search_type": "SEARCH_TYPE_RU"
  },
  "coverage": {
    "wordstat": true,
    "search": true,
    "webmaster": true,
    "metrika": true
  },
  "queries": [],
  "pages": [],
  "clusters": [],
  "sources": {},
  "findings": [],
  "limitations": []
}
```

Every observed or derived metric keeps source provenance, relevant period/context, and quality metadata.

Example evidence item:

```json
{
  "kind": "observed",
  "metric": "clicks",
  "value": 324,
  "source": "yandex-webmaster",
  "period": {"from": "2026-08-01", "to": "2026-08-31"},
  "query_key": "регистрация товарного знака"
}
```

## 7. Evidence semantics

Every finding/evidence item is classified as one of:

- `OBSERVED` — directly present in a source artifact;
- `DERIVED` — deterministic calculation from observed evidence;
- `HYPOTHESIS` — interpretation that requires validation.

The plugin must never present a `HYPOTHESIS` as an observed fact.

## 8. Demand semantics

Wordstat demand and Webmaster demand are distinct metrics and must never be silently substituted.

Required fields preserve both when available:

```json
{
  "wordstat_count": 12400,
  "wordstat_window": "rolling_30_days",
  "webmaster_demand": 11870,
  "webmaster_period": {"from": "...", "to": "..."}
}
```

No helper may implement behavior equivalent to `demand = webmaster_demand or wordstat_count`.

## 9. Temporal alignment

Cross-service evidence is classified as:

- `EXACT` — materially equivalent analysis periods/context;
- `APPROXIMATE` — usable with explicit limitation, e.g. rolling Wordstat 30-day data against a calendar-month report;
- `MISMATCHED` — not valid for direct comparative/causal interpretation.

Point-in-time Search SERP snapshots must remain labeled as snapshots rather than period aggregates.

When alignment is `MISMATCHED`, workflows may describe separate observations but must not produce causal or trend claims across them.

## 10. Geography/context alignment

The bundle keeps distinct concepts rather than collapsing all geography into one field:

- Wordstat query region;
- Search SERP ranking region;
- Webmaster search/query region when present;
- Metrika visitor geography.

Visitor geography must never be treated as equivalent to ranking-region configuration without explicit evidence.

Search type, device, attribution, sampling/accuracy, freshness/period, and other context fields must be preserved where they affect interpretation.

## 11. Query normalization and joins

Default query key normalization may perform only:

- Unicode normalization;
- trim;
- case folding;
- whitespace normalization.

No default stemming, lemmatization, fuzzy matching, or commercial-intent inference.

Semantic grouping comes from Search SERP-overlap clusters when available. The SEO layer does not reimplement Search clustering and must preserve its explicit `top_k`, `min_shared_urls`, pairwise overlap/Jaccard, and `bridge_risk` metadata.

## 12. URL normalization and joins

URL joins use conservative canonicalization:

- normalize scheme/host case;
- normalize default ports;
- remove fragments;
- normalize empty path;
- stable ordering of query parameters.

Query parameters are not dropped by default.

The bundle may join Search ranking URLs, Webmaster URLs, and Metrika landing `startURL` values using the canonical URL key while retaining all raw URLs.

## 13. Data-quality propagation

The SEO layer inherits source limitations rather than erasing them.

Examples:

- Metrika sampling, sample share, data lag, sensitive-data restrictions and rounded totals;
- Webmaster top-N/incomplete query coverage and source-specific query statistics;
- Search snapshot/configuration fingerprint and `bridge_risk`;
- Wordstat rolling windows, provenance, operator expression and region/device context.

A derived finding must carry material upstream limitations.

## 14. Content-gap analysis

A `CONTENT_GAP` requires multi-source evidence when those sources are available:

- meaningful Wordstat demand or trend evidence;
- a Search intent/cluster signal;
- weak/absent site representation in Search SERPs;
- weak/absent Webmaster visibility where Webmaster coverage is available.

With demand evidence only, label the result `DISCOVERY_CANDIDATE`, not a confirmed content gap.

## 15. Cannibalization analysis

A cannibalization candidate requires evidence of multiple own URLs associated with the same query/cluster plus evidence of competition/split visibility such as:

- both URLs appearing for the same Search query/cluster;
- Webmaster impressions/clicks/positions split across URLs;
- position/URL instability across compatible snapshots/periods.

Multiple URLs alone are insufficient.

Output includes confidence and supporting evidence; no automatic redirect/canonical/delete recommendation is executed.

## 16. CTR opportunities

Webmaster is the canonical source for Yandex search impressions/clicks/CTR when available.

The plugin must not apply universal position-based CTR benchmarks as facts.

Preferred comparisons:

- same query/page over equivalent periods;
- device-specific own history;
- comparable queries/clusters from the same site;
- before/after comparisons with compatible context.

Low CTR is an observed/derived condition; reasons such as weak title/snippet or intent mismatch are hypotheses unless independently supported.

## 17. Organic conversion analysis

Performance mode joins Webmaster search visibility with Metrika organic landing/conversion evidence where a defensible join exists.

The workflow distinguishes:

```text
Webmaster: impression → click
Metrika: visit → goal/conversion/revenue
```

A query/cluster with strong visibility but weak conversion may generate an intent/landing mismatch hypothesis, but the plugin must not state causation without supporting evidence.

Attribution model, sampling/data quality and landing/query join limitations remain visible.

## 18. Technical-impact correlation

Technical analysis correlates Webmaster diagnostics/indexing/search-inclusion evidence with pages/clusters that have demand, visibility, traffic, or conversion importance.

Example priority evidence:

```text
high-demand cluster
+ valuable landing
+ indexing exclusion/diagnostic blocker
→ strong technical opportunity
```

The SEO layer may produce a delegated action preview but does not execute recrawl/sitemap/feed mutations.

## 19. Prioritization

`yandex-seo` 1.0.0 has no universal opaque numeric SEO score.

Prioritization uses explicit dimensions such as:

- demand evidence;
- visibility gap;
- SERP/intent evidence;
- conversion evidence;
- technical blocker;
- trend direction;
- evidence coverage/confidence;
- limitations.

If numeric weights are requested, they must be user-provided or explicitly shown in the output together with the formula.

## 20. Delegated actions and safety

The Phase 6A safety pipeline is:

```text
READ → NORMALIZE → CORRELATE → DERIVE → RECOMMEND → DELEGATE PREVIEW
```

A delegated action has a contract such as:

```json
{
  "action": "recrawl",
  "service": "yandex-webmaster",
  "skill": "yandex-webmaster-recrawl",
  "target": "https://example.com/page",
  "reason": "...",
  "requires_approval": true
}
```

`yandex-seo` does not call the write endpoint. The owning plugin remains responsible for preview, explicit approval, execution, and verification under the repository safety contract.

## 21. Pure-data helpers

Seven standard-library Python helpers are planned:

```text
scripts/
├── seo_context.py
├── seo_bundle.py
├── seo_join.py
├── seo_quality.py
├── seo_opportunities.py
├── seo_cannibalization.py
└── seo_prioritize.py
```

Responsibilities:

- `seo_context.py` — period/geo/search/device context normalization and alignment status;
- `seo_bundle.py` — evidence-bundle construction/validation;
- `seo_join.py` — conservative query/URL/source joins;
- `seo_quality.py` — propagate source limitations/confidence/evidence types;
- `seo_opportunities.py` — content-gap, CTR, conversion and technical opportunity derivation;
- `seo_cannibalization.py` — multi-URL intent competition evidence;
- `seo_prioritize.py` — transparent sorting/grouping and delegated action previews.

No helper imports network libraries or contains Yandex API endpoints/authentication.

## 22. File/artifact contracts

The plugin consumes structured JSON artifacts or equivalent in-memory objects from service plugins. Large cross-service datasets should be written to files/artifacts when runtime supports it, with compact conversational summaries.

Artifact schemas must be versioned. Unknown future fields are ignored when safe; missing required fields produce explicit validation errors rather than guessed values.

## 23. Testing and evals

Offline unit tests cover at minimum:

- capability-mode detection;
- bundle validation;
- query normalization without fuzzy joins;
- conservative URL joins;
- exact/approximate/mismatched period alignment;
- geo-context separation;
- Wordstat vs Webmaster demand separation;
- source-quality propagation;
- content-gap candidate vs confirmed gap logic;
- cannibalization evidence requirements;
- CTR opportunity without universal benchmark;
- conversion-analysis evidence typing;
- transparent prioritization;
- delegated-action preview and no-write guarantees.

Offline agent evals route representative prompts to all ten skills and verify read-only/delegation behavior.

## 24. Marketplace and CI integration

Phase 6A adds `yandex-seo` to root marketplace metadata and `docs/SERVICE_MATRIX.md` as an independently installable cross-service plugin at version `1.0.0`.

Path-aware CI gets a dedicated `yandex-seo` job that runs plugin unit tests and compiles all seven helpers. Shared root contract changes continue to trigger relevant plugin checks.

Existing Direct, Metrika, Webmaster, Wordstat and Search plugin runtime code must not be changed as part of Phase 6A.

## 25. Git strategy

```text
phase-4-yandex-wordstat
        ↓
phase-5-yandex-search / PR #5
        ↓
phase-6-yandex-seo
        ↓
PR #6 → phase-5-yandex-search
```

After preceding stacked PRs land, PR #6 can be retargeted to `main`.

## 26. Definition of Done

`yandex-seo 1.0.0` is complete when it has:

- ten production skills;
- seven dependency-free pure-data helpers;
- canonical versioned SEO Evidence Bundle;
- Discovery, Visibility, Performance and Full SEO modes;
- query/URL/context join contracts;
- exact/approximate/mismatched alignment;
- source-quality propagation;
- content-gap analysis;
- cannibalization analysis;
- CTR opportunity analysis;
- organic conversion analysis;
- technical-impact correlation;
- transparent prioritization;
- delegated action previews with no direct live writes;
- offline unit tests/evals;
- marketplace/service-matrix/roadmap integration;
- path-aware CI;
- regression verification showing prior service plugins are functionally unchanged.

## 27. Phase 6B boundary

`yandex-marketing` is intentionally excluded from this spec. It will be designed separately after `yandex-seo` stabilizes, primarily composing Direct + Metrika + Wordstat and optionally Search for competitive context.
