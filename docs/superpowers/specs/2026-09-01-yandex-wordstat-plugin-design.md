# Yandex Wordstat Plugin Design

**Date:** 2026-09-01  
**Status:** Approved  
**Target:** `plugins/yandex-wordstat/` version `1.0.0`

## Purpose

Ship Yandex Wordstat as an independently installable, workflow-first plugin in the Yandex AI marketplace. The plugin provides demand research, semantic expansion, operator-aware frequency analysis, dynamics, regions and trend detection while keeping execution backend-independent and avoiding misleading demand aggregation.

## Primary API baseline

Version 1.0.0 uses Yandex Cloud Search API Wordstat REST v2 as the bundled execution backend:

- `POST /v2/wordstat/topRequests`
- `POST /v2/wordstat/dynamics`
- `POST /v2/wordstat/regions`
- `POST /v2/wordstat/getRegionsTree`

The legacy `https://api.wordstat.yandex.net/v1` OAuth API remains documented as an alternate official surface but is not implemented as a bundled adapter in 1.0.0. Skills describe capabilities rather than binding to one runtime/MCP implementation, so a future legacy adapter or connected app can be added without changing workflow semantics.

## Authentication

Bundled Cloud execution supports exactly one authorization credential at a time:

- `YANDEX_WORDSTAT_API_KEY` -> `Authorization: Api-Key ...`
- `YANDEX_WORDSTAT_IAM_TOKEN` -> `Authorization: Bearer ...`

`YANDEX_WORDSTAT_FOLDER_ID` is optional for service-account credentials but may be required for user/federated IAM flows. If provided, trim whitespace, require non-empty content and reject values longer than 50 characters. Do not enforce the donor project's fixed 20-character rule.

Current access baseline: `search-api.webSearch.user` role and API-key scope `yc.search-api.execute` where applicable.

## Plugin skills

The approved capability list contains nine discoverable skills (router plus eight specialized skills):

1. `yandex-wordstat` — router and research safety contract.
2. `yandex-wordstat-research` — end-to-end demand research planning and synthesis.
3. `yandex-wordstat-semantics` — multi-seed expansion, provenance and deduplication.
4. `yandex-wordstat-frequency` — phrase frequency interpretation and exact-expression comparison.
5. `yandex-wordstat-dynamics` — monthly/weekly historical demand analysis.
6. `yandex-wordstat-regions` — regional volume/share/affinity analysis and region-tree lookup.
7. `yandex-wordstat-trends` — robust growth classification with absolute-volume and seasonality checks.
8. `yandex-wordstat-operators` — operator semantics and method/granularity compatibility.
9. `yandex-wordstat-api` — raw v2 request construction, auth, quota and cost planning.

## Execution helpers

```text
scripts/
├── __init__.py
├── _http.py
├── ywstat_api.py
├── ywstat_top.py
├── ywstat_semantics.py
├── ywstat_dynamics.py
├── ywstat_regions.py
└── ywstat_trends.py
```

All helpers use the Python 3.13 standard library only. Tests are offline and use fake transports/fixtures.

## GetTop data model

`GetTop` returns three distinct concepts and the plugin must preserve them:

- `totalCount`: count of queries containing all seed keywords, regardless of word order.
- `results`: nested/popular requests containing the seed expression.
- `associations`: similar/associated requests.

Normalized records carry:

```json
{
  "phrase": "...",
  "count": 123,
  "relation": "nested|association",
  "sources": ["seed A", "seed B"],
  "operator_expression": null
}
```

Deduplication merges provenance rather than discarding all but the first seed. If the same phrase appears with different relation types, preserve all relation types or prefer `nested` only for ordering while retaining both in metadata.

## No fake total-demand aggregation

Phrase counts overlap. The plugin must never sum related/nested phrase counts and label that value as total demand, market size or unique searches.

Allowed aggregates include:

- number of unique phrases collected;
- distribution statistics over returned phrase counts;
- `totalCount` returned by Yandex for one exact request expression;
- clearly labeled sums for operational purposes only, never as unique market demand.

## Operators

Wordstat supports `-`, `!`, `+`, quotes, `[]`, `()`, and `|` in Top/Regions semantics. The Cloud v2 `GetDynamics` REST surface currently exposes monthly and weekly periods. For those granularities the safe compatibility rule is: only `+` is guaranteed. The plugin rejects or warns on expressions with other operators before monthly/weekly Dynamics calls instead of silently changing meaning.

Every result that used operators preserves the exact input expression.

## Semantics workflow

```text
seed phrases
  -> GetTop per seed
  -> keep results + associations separate
  -> normalize string counts to integers
  -> merge duplicate phrases
  -> preserve all source seeds and relation types
  -> emit structured JSON/file artifact for large collections
```

Semantic collection is candidate generation, not final SEO clustering. SERP-overlap clustering belongs to the future Yandex Search plugin/cross-service workflow.

## Dynamics and trends

Dynamics requests use REST camelCase fields `fromDate` and `toDate` and period enums `PERIOD_MONTHLY` / `PERIOD_WEEKLY`.

Trend classification must not equate a large percentage change at tiny volume with a meaningful trend. The default pure-analysis pipeline is:

```text
series
 -> validate/normalize
 -> baseline median
 -> recent value/window
 -> absolute-volume floor
 -> growth ratio
 -> same-period prior-year check when available
 -> classification
```

At minimum classify `LOW_VOLUME_NOISE`, `STABLE`, `GROWING`, `EXPLOSIVE`, and `SEASONAL`. Thresholds are explicit function parameters/defaults, not universal business truths; skills must report the chosen thresholds.

## Regions

Regional records preserve:

- region ID;
- count;
- share;
- `affinityIndex`.

The agent distinguishes absolute volume from relative affinity. A lower-volume region with high affinity is not described as having more total demand than a high-volume region.

`GetRegionsTree` is free according to the current pricing page and should be cacheable by callers. The bundled helper provides flatten/search utilities but does not create runtime-specific cache paths.

## Quota and cost awareness

Current documented Wordstat limits are 10 requests/second and 100 requests/hour. The planner accepts a configurable safety budget (default 90 requests) and estimates whether a research plan fits one hourly window.

Pricing baseline verified 2026-09-01, RUB per 1000 requests:

- GetTop: 20 RUB
- GetDynamics: 20 RUB
- GetRegionsDistribution: 50 RUB
- GetRegionsTree: free

Pricing constants are labeled with their verification date and estimator functions accept overrides. Cost is an estimate, not a billing guarantee.

## Safety and execution

Wordstat methods are read-only from a business-data perspective, but they consume quota and paid requests. Safety therefore focuses on:

- credential redaction;
- request/cost preview for large research plans;
- preventing accidental quota exhaustion;
- explicit user awareness before a large batch;
- file-oriented output for large semantic datasets;
- no invented frequency/region/trend values when live execution is unavailable.

Execution fallback order:

```text
connected app/MCP if compatible
 -> bundled Python helper
 -> user-provided export/file
 -> methodology-only answer with explicit missing-data note
```

## Donor use

- Official Yandex AI Studio/Search API and Wordstat docs are source of truth.
- `axelfreeman/yandex-wordstat-guide` is the primary workflow/agent donor for multi-seed semantics, provenance, structured outputs and trend discovery.
- `mkultraaaa/claude-yandex-skills` is a donor for region/operator workflows only; runtime-specific OpenClaw paths and stale quota assumptions are not copied.
- `theYahia/YaAll` is an execution/capability checklist and optional backend reference; its static region mappings and business-threshold heuristics are not authoritative.

MIT donor attribution is recorded in `THIRD_PARTY_NOTICES.md` and `references/sources.md`.

## Repository integration

Phase 4 is stacked on `phase-3-yandex-webmaster`.

Root marketplace metadata adds `./plugins/yandex-wordstat`; service matrix marks Wordstat `available 1.0.0`; roadmap marks Phase 4 implemented and Phase 5 Yandex Search next; CI detects Wordstat path changes and runs Wordstat tests/compile checks independently.

No functional file under Direct, Metrika or Webmaster may change in Phase 4.

## Definition of Done

- nine approved skills;
- seven dependency-free execution helpers plus `__init__.py`;
- Cloud Wordstat v2 methods GetTop/GetDynamics/GetRegionsDistribution/GetRegionsTree;
- API-Key and IAM auth with redaction;
- optional/validated folderId, no fixed 20-char assumption;
- separate results/associations and provenance-aware semantic merge;
- operator compatibility validation;
- quota and cost planner;
- regional affinity helpers and region-tree search;
- robust trend classification with low-volume/seasonality handling;
- explicit invariant against fake total-demand sums;
- current references, attribution and offline evals/tests;
- marketplace/service-matrix/roadmap/path-aware CI integration;
- Direct/Metrika/Webmaster unchanged functionally.
