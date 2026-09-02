# Yandex Marketing Cross-Service Plugin Design

**Status:** approved Phase 6B design; post-implementation contract amended by OPUS 1.1.1 review  
**Date:** 2026-09-02  
**Original target version:** `yandex-marketing` 1.0.0  
**Current executable contract:** `yandex-marketing` 1.1.0  
**Stacking base:** `phase-6-yandex-seo`

> **OPUS 1.1.1 normative amendment:** the broad finding vocabulary in this design describes intended analytical concepts, but it is not automatically an executable taxonomy. For the current plugin, `IMPLEMENTED_FINDING_TYPES` is the authoritative local producer set and contains exactly nine classes; `DEFERRED_FINDING_TYPES` contains recognized but non-produced classes. `GOAL_ALIGNMENT_RISK` is additionally accepted as a narrowly approved external finding for goal-change delegation. Where older wording below says a workflow “may derive” a broad class, Section 20 governs whether that class is currently executable, deferred, external-only, or historical vocabulary.

## 1. Purpose

`yandex-marketing` is the paid-acquisition cross-service plugin for the marketplace. It composes structured outputs from Yandex Direct, Metrika, Wordstat, and optionally Search into evidence-based marketing analysis without duplicating service API clients or bypassing their safety contracts.

The plugin must answer questions such as:

- which campaigns, criteria, search queries, and landing pages drive business outcomes;
- where Direct spend and Metrika outcome data are comparable, explainably different, or not comparable;
- where external demand exists but paid coverage appears weak;
- which actual search queries deserve expansion or exclusion review;
- where budget constraints or reallocation opportunities may exist;
- whether apparent performance differences are caused by KPI, attribution, maturity, or measurement context mismatches;
- how to prioritize paid-acquisition actions transparently from available evidence.

`yandex-marketing` is read/analyze/recommend/preview only. It never changes campaigns, budgets, bids, keywords, negatives, strategies, goals, or other live settings itself.

## 2. Scope and boundaries

### In scope

- cross-service orchestration over Direct, Metrika, Wordstat, and optional Search;
- Direct as the required primary acquisition source;
- canonical Marketing Evidence Bundle;
- KPI fingerprint and comparability checks;
- source-of-truth rules for cost, clicks, sessions, conversions, revenue, demand, and SERP context;
- conservative joins for campaign, criterion, goal, query, and landing entities;
- cost/revenue/conversion reconciliation without double counting;
- demand coverage and search-query intelligence;
- landing, attribution, measurement, maturity, and budget diagnostics;
- transparent findings and prioritization;
- delegated action previews pointing to the owning service plugin.

### Out of scope

- direct calls to Yandex APIs;
- credentials, OAuth, API keys, or HTTP clients;
- live Direct/Metrika writes;
- automated budget redistribution;
- automated keyword/negative changes;
- campaign creation or activation;
- universal CPA, ROAS, DRR, CTR, CR, CPC, or click-count thresholds;
- opaque marketing scores;
- persistent marketing warehouse/database;
- scheduled campaign monitoring;
- full SEO workflows already owned by `yandex-seo`;
- social, CRM, email, retail media, or non-Yandex paid-channel orchestration.

## 3. Architecture

The plugin operates on structured outputs and exported artifacts from existing service plugins.

```text
Direct ───── campaigns / spend / clicks / criteria / queries / attributed outcomes
Metrika ─── sessions / goals / ecommerce / landing behavior / attribution context
Wordstat ── external demand / seasonality / regions
Search ──── optional SERP / intent / competitor context
      │
      ▼
Marketing Evidence Bundle
      │
      ├── normalize
      ├── align KPI context
      ├── reconcile overlapping metrics
      ├── propagate quality limitations
      ├── derive paid-acquisition findings
      └── prioritize
             ↓
      marketing action plan
             ↓
 delegated service-plugin preview
```

The plugin must not contain Yandex endpoint clients. `scripts/` contains standard-library pure data transformation and analysis helpers only.

## 4. Installation boundary and source requirements

`plugins/yandex-marketing/` is independently installable and versioned.

Direct is mandatory. If no Direct evidence is available, the router must explain that the task should be handled by Metrika, Wordstat, Search, or another plugin rather than pretending to perform paid-acquisition analysis.

Supported capability modes:

| Mode | Required evidence | Supported analysis |
| --- | --- | --- |
| `PAID_PERFORMANCE` | Direct + Metrika | spend → click → visit → business outcome reconciliation |
| `DEMAND_PLANNING` | Direct + Wordstat | external demand versus paid coverage candidates |
| `QUERY_INTELLIGENCE` | Direct + Wordstat | search-query expansion/exclusion review |
| `FULL_ACQUISITION` | Direct + Metrika + Wordstat | full paid-performance + demand analysis |
| `COMPETITIVE_CONTEXT` | Direct + Search, normally with other evidence | optional intent/SERP enrichment |
| `DIRECT_ONLY` | Direct | campaign/query/performance analysis limited to Direct evidence |

Search is optional enrichment and must never be required for ordinary paid-performance calculations.

## 5. Skills

`yandex-marketing` contains eleven discoverable skills:

1. `yandex-marketing` — router, source coverage, capability-mode detection;
2. `yandex-marketing-audit` — end-to-end paid-acquisition audit;
3. `yandex-marketing-performance` — campaign/criterion/query paid-performance analysis;
4. `yandex-marketing-demand` — Wordstat demand versus Direct paid-coverage analysis;
5. `yandex-marketing-queries` — actual Direct search-query intelligence plus Wordstat context;
6. `yandex-marketing-landings` — query/ad/landing behavior analysis using Direct + Metrika;
7. `yandex-marketing-conversions` — goal and conversion reconciliation across Direct/Metrika;
8. `yandex-marketing-attribution` — KPI/goal/attribution comparability diagnostics;
9. `yandex-marketing-budget` — evidence-based budget constraint/reallocation candidates and previews;
10. `yandex-marketing-opportunities` — derive marketing opportunity/risk taxonomy;
11. `yandex-marketing-prioritize` — transparent ordering and delegated action previews.

## 6. Canonical Marketing Evidence Bundle

The Marketing Evidence Bundle is the stable internal contract for Phase 6B.

```json
{
  "version": 1,
  "context": {
    "account": "client-or-account-id",
    "currency": "RUB",
    "vat_basis": "excluded",
    "period": {"from": "2026-08-01", "to": "2026-08-31"},
    "goal_ids": ["1234567"],
    "attribution_model": "automatic"
  },
  "coverage": {
    "direct": true,
    "metrika": true,
    "wordstat": true,
    "search": false
  },
  "campaigns": [],
  "criteria": [],
  "search_queries": [],
  "landings": [],
  "goals": [],
  "demand": [],
  "sources": {},
  "findings": [],
  "limitations": []
}
```

Every observed or derived metric retains source provenance, period, attribution/KPI context when applicable, and data-quality limitations.

## 7. Evidence semantics

Every evidence/finding item is one of:

- `OBSERVED` — directly supplied by one service artifact;
- `DERIVED` — deterministic calculation/reconciliation from observed evidence;
- `HYPOTHESIS` — a plausible interpretation requiring validation.

Examples:

- Direct spend is `OBSERVED`;
- CPA calculated from explicitly compatible spend/conversion evidence is `DERIVED`;
- “landing message does not match search intent” is `HYPOTHESIS` unless independently validated.

Hypotheses must never be phrased as source facts.

## 8. Source-of-truth matrix

The plugin uses explicit metric ownership rather than blindly merging overlapping values.

| Metric/context | Canonical source | Other source role |
| --- | --- | --- |
| paid impressions | Direct | none |
| paid clicks | Direct | Metrika reconciliation/context |
| Direct spend | Direct | Metrika reconciliation only |
| Direct CPC | Direct | Metrika reconciliation only |
| campaign/ad/criterion identity | Direct | none |
| actual paid search query | Direct | Wordstat demand enrichment |
| sessions/visits | Metrika | none |
| landing behavior | Metrika | none |
| business goal definitions/outcomes | Metrika | Direct attributed view for comparison |
| ecommerce orders/revenue | Metrika | Direct attributed subset/context |
| external demand/seasonality | Wordstat | none |
| SERP/intent/competitor context | Search | optional enrichment only |

A noncanonical overlapping metric may be retained for reconciliation, but not silently substituted for the canonical metric.

## 9. No Direct/Metrika double counting

The following patterns are forbidden:

```python
conversions = direct_conversions + metrika_conversions
cost = direct_cost + metrika_direct_cost
revenue = direct_revenue + metrika_revenue
```

Instead, overlapping evidence is represented side by side with source role and context:

```json
{
  "direct_cost": {
    "value": 152300.50,
    "currency": "RUB",
    "source": "yandex-direct",
    "role": "canonical_paid_cost"
  },
  "metrika_direct_cost": {
    "value": 152180.20,
    "currency": "RUB",
    "source": "yandex-metrika",
    "role": "reconciliation_only"
  }
}
```

Differences must be classified rather than automatically treated as errors.

## 10. KPI fingerprint

Any performance comparison that depends on conversion economics must preserve a KPI fingerprint.

```json
{
  "business_objective": "purchase",
  "goal_ids": ["1234567"],
  "attribution_model": "automatic",
  "metric_basis": "converted_sessions",
  "currency": "RUB",
  "vat_basis": "excluded",
  "period": {"from": "2026-08-01", "to": "2026-08-31"}
}
```

Before comparing CPA/ROAS/revenue performance, helpers must check material fingerprint compatibility.

At minimum, incompatibility is raised for materially different:

- business goals or goal IDs;
- attribution models;
- metric basis;
- currency;
- VAT basis when monetary comparisons depend on it;
- noncomparable periods.

The plugin must not rank one campaign as more efficient merely because it uses an easier micro-conversion goal.

## 11. Cost and revenue context

Money evidence must preserve:

- source;
- currency;
- VAT basis when known;
- period;
- date basis when known;
- goal/attribution context for revenue when relevant.

When two monetary observations have different date bases or goal/revenue definitions, the plugin must classify them as contextually different rather than forcing equality.

No currency conversion is performed unless an explicit conversion input/rate is provided by the user or another trusted component.

## 12. Attribution alignment

Direct-attributed conversion metrics and Metrika conversion reports can only be compared when the goal and attribution contexts are materially compatible.

The plugin must report one of:

- `ALIGNED` — suitable for direct comparison;
- `EXPLAINABLE_DIFFERENCE` — comparable context with known/reportable reasons for differences;
- `REVIEW` — evidence suggests a discrepancy that needs investigation;
- `INCOMPARABLE` — materially different KPI/attribution/period basis.

The cross-service layer must not encode stale attribution models as canonical platform truth; source plugins and current references own volatile model names.

## 13. Temporal alignment and maturity

Marketing comparisons use explicit period context. Evidence can be:

- `EXACT` — materially equivalent periods/date basis;
- `APPROXIMATE` — usable with disclosed timing difference;
- `MISMATCHED` — invalid for direct comparative interpretation.

Conversion maturity is represented separately:

- `MATURE` — evidence supports using the period for outcome comparison;
- `IMMATURE` — a known conversion delay/data lag means outcomes are incomplete;
- `MATURITY_UNKNOWN` — insufficient evidence to assert maturity.

There is no universal “ignore last N days” rule.

## 14. Entity joins

### Campaign

Join by campaign ID, not campaign name.

### Criterion

Join by stable Direct criterion identity when supplied. Keyword, autotargeting, and other criterion types remain distinct.

### Goal

Join by goal ID. Human-readable names are labels, not identity keys.

### Query

Default normalization is limited to:

- Unicode normalization;
- trim;
- case folding;
- whitespace collapse.

No stemming, lemmatization, fuzzy merge, or commercial-intent inference by default.

An actual Direct `SearchQuery` and a Wordstat phrase may be joined only under an explicit normalized-key relation; the resulting evidence must preserve that one is an observed paid query and the other is statistical demand context.

### Landing URL

URL normalization is conservative:

- normalize scheme/host case;
- normalize default ports;
- remove fragment;
- normalize empty path;
- stable-sort query parameters.

Query parameters are not deleted by default.

## 15. Demand semantics

Wordstat demand is external demand evidence, not guaranteed advertising inventory.

Therefore:

```text
high Wordstat demand + low/no Direct coverage
```

may produce:

`DEMAND_EXPANSION_CANDIDATE`

but must not produce unsupported claims such as:

`MISSED_TRAFFIC = wordstat_count`.

The plugin must preserve region/device/time context when it materially affects the comparison.

## 16. Search-query intelligence

The query workflow combines:

- Direct actual search queries;
- criterion/keyword/autotargeting context when available;
- spend/click/conversion evidence;
- Wordstat demand/trend/association evidence;
- optional Search intent/SERP context.

The design vocabulary includes search-query expansion, exclusion review, coverage-gap, and intent-review concepts. The current executable contract is narrower:

- `SEARCH_TERM_EXPANSION_CANDIDATE` — implemented;
- `SEARCH_TERM_EXCLUSION_REVIEW` — implemented;
- `QUERY_COVERAGE_GAP` — deferred;
- `QUERY_INTENT_REVIEW` — historical design vocabulary only and not an accepted executable finding type in 1.1.0.

The plugin must not recommend a negative keyword solely because an arbitrary click count produced zero conversions. Business goal, conversion delay, spend context, and evidence sufficiency must be considered.

## 17. Landing analysis

Landing workflows join Direct query/ad/criterion evidence with Metrika landing and outcome evidence.

The broad design vocabulary includes:

- `LANDING_MISMATCH_HYPOTHESIS` — implemented;
- `QUERY_MISMATCH_HYPOTHESIS` — deferred;
- `TRAFFIC_QUALITY_HYPOTHESIS` — deferred;
- `MEASUREMENT_RISK` — implemented.

The cross-service plugin must not claim causal certainty from observational data alone.

## 18. Conversion reconciliation

Direct and Metrika conversion counts are compared, not summed.

Reconciliation must preserve:

- goal IDs/semantics;
- attribution model;
- period;
- metric basis;
- maturity/data-lag limitations.

Output classification is one of `ALIGNED`, `EXPLAINABLE_DIFFERENCE`, `REVIEW`, or `INCOMPARABLE`.

A discrepancy is not automatically a tracking defect.

## 19. Budget analysis

The budget design vocabulary contains:

- `BUDGET_CONSTRAINT_CANDIDATE` — implemented;
- `BUDGET_REALLOCATION_CANDIDATE` — implemented;
- `SPEND_EFFICIENCY_REVIEW` — deferred.

A budget finding must state:

- business/KPI context;
- evidence supporting the candidate;
- data sufficiency/maturity;
- confidence;
- limitations;
- reversibility/blast-radius notes when delegation is prepared.

No universal budget reallocation rule or “winner/loser” cutoff is allowed.

## 20. Opportunity taxonomy

Phase 6B uses explicit finding classes rather than a magic score. The current executable contract is intentionally smaller than the original broad design vocabulary.

### Implemented local producer set

`IMPLEMENTED_FINDING_TYPES` contains exactly these nine classes:

- `MEASUREMENT_RISK`
- `KPI_CONTEXT_MISMATCH`
- `ATTRIBUTION_MISMATCH`
- `BUDGET_CONSTRAINT_CANDIDATE`
- `BUDGET_REALLOCATION_CANDIDATE`
- `DEMAND_EXPANSION_CANDIDATE`
- `SEARCH_TERM_EXPANSION_CANDIDATE`
- `SEARCH_TERM_EXCLUSION_REVIEW`
- `LANDING_MISMATCH_HYPOTHESIS`

Only these classes are claimed as locally produced deterministic finding types by the current helpers.

### Deferred recognized set

`DEFERRED_FINDING_TYPES` contains recognized design vocabulary that is not currently produced locally:

- `GOAL_ALIGNMENT_RISK`
- `MATURITY_RISK`
- `SPEND_EFFICIENCY_REVIEW`
- `QUERY_COVERAGE_GAP`
- `SEASONALITY_ALERT`
- `QUERY_MISMATCH_HYPOTHESIS`
- `TRAFFIC_QUALITY_HYPOTHESIS`
- `COMPETITIVE_CONTEXT`
- `SERP_INTENT_CONTEXT`

Deferred or otherwise unknown types sort after implemented findings under the default prioritizer and receive `UNKNOWN_OR_DEFERRED_TYPE`.

### Approved external exception

`GOAL_ALIGNMENT_RISK` is also present in `APPROVED_EXTERNAL_FINDING_TYPES`. It may be accepted from a trusted upstream/external evidence producer and delegated to `yandex-metrika-goals` only when `recommended_action == "goal_change"`; this does not make it a locally produced type.

`QUERY_INTENT_REVIEW` is not part of the implemented, deferred, or approved-external contract and must not be emitted as a current finding type. `NEW_CAMPAIGN_CANDIDATE` is likewise not an active finding/delegation route.

Every finding includes evidence, confidence, limitations, and a recommended next step.

## 21. Performance metrics

The cross-service layer may derive metrics such as CPA, CR, ROAS, or revenue-per-click only when required inputs and KPI context are explicit and compatible.

If revenue is unavailable, ROAS/DRR must not be invented.

If goals are ambiguous or mixed, aggregate CPA/CR must not be presented as a single business KPI without disclosure.

No universal target values or benchmarks are encoded into the plugin.

## 22. Search as optional enrichment

Search does not determine paid efficiency.

It may enrich:

- query/landing intent hypotheses;
- competitor/SERP context;
- understanding of a Wordstat demand cluster.

Search context cannot override Direct spend/conversion evidence or create a paid-performance metric by itself.

## 23. Prioritization

There is no default numeric Marketing Score.

Default prioritization is transparent and categorical, based on:

- user/business objective;
- measurement/KPI validity;
- evidence coverage and strength;
- business relevance;
- outcome evidence;
- demand evidence where relevant;
- maturity/quality limitations;
- confidence;
- reversibility;
- blast radius for consequential recommendations.

If a user explicitly supplies scoring weights, helpers may apply them only while preserving and displaying the formula/weights.

## 24. Delegated action previews

`yandex-marketing` never executes consequential writes.

A delegated action descriptor contains at minimum:

```json
{
  "service": "yandex-direct",
  "skill": "yandex-direct-budget",
  "target": {"campaign_id": 123456},
  "reason": "...",
  "requires_approval": true
}
```

Ownership examples:

| Recommendation | Owning plugin/skill |
| --- | --- |
| budget change | `yandex-direct-budget` |
| keyword/negative change | `yandex-direct-keywords` |
| strategy/targeting optimization | `yandex-direct-optimize` |
| campaign draft/create | `yandex-direct-create` |
| goal definition/change | `yandex-metrika-goals` |
| additional demand research | Wordstat read workflow |

The owning plugin must perform its own preview, explicit approval, mutation, and verification process.

## 25. Helpers

`yandex-marketing` uses eight Python standard-library pure-data helpers:

```text
scripts/
├── marketing_context.py
├── marketing_bundle.py
├── marketing_join.py
├── marketing_quality.py
├── marketing_performance.py
├── marketing_demand.py
├── marketing_opportunities.py
└── marketing_prioritize.py
```

Responsibilities:

- `marketing_context.py` — query/URL normalization, KPI fingerprint, period/maturity/comparability primitives;
- `marketing_bundle.py` — bundle creation, evidence insertion, source provenance;
- `marketing_join.py` — campaign/criterion/goal/query/landing joins;
- `marketing_quality.py` — capability mode, source limitations, reconciliation context;
- `marketing_performance.py` — compatible performance calculations and Direct/Metrika reconciliation;
- `marketing_demand.py` — Wordstat demand enrichment, coverage candidate logic, seasonality context;
- `marketing_opportunities.py` — opportunity/risk taxonomy derivation;
- `marketing_prioritize.py` — transparent ordering and delegated action previews.

No helper may import an HTTP client or contain service credentials/endpoints.

## 26. Error and limitation handling

The plugin must fail closed on analytical comparability rather than inventing precision.

Examples:

- Direct missing → paid-acquisition workflow unavailable; route to another plugin if applicable;
- incompatible goal/attribution fingerprint → `INCOMPARABLE`, no efficiency ranking;
- immature period → qualify outcome findings;
- missing revenue → no ROAS/DRR;
- missing Wordstat → performance analysis remains possible but demand coverage is unavailable;
- missing Metrika → Direct-only analysis remains possible but landing/session/business-goal reconciliation is limited;
- missing Search → no competitive/SERP enrichment, no failure of core marketing workflow;
- source quality limitations must survive into final findings.

## 27. Safety model

Cross-service safety sequence:

```text
READ
→ NORMALIZE
→ RECONCILE
→ DIAGNOSE
→ RECOMMEND
→ DELEGATE PREVIEW
```

Only an owning service plugin may proceed to:

```text
EXPLICIT APPROVAL
→ WRITE
→ VERIFY
```

The marketing layer must never interpret “optimize”, “reduce wasted spend”, “fix campaigns”, or similar analysis requests as authorization to mutate campaigns.

## 28. Relation to yandex-seo

`yandex-seo` and `yandex-marketing` share an architectural pattern but have separate evidence contracts and responsibilities.

```text
yandex-seo
Wordstat + Search + Webmaster + Metrika
→ organic discovery / visibility / performance
```

```text
yandex-marketing
Direct + Metrika + Wordstat [+ Search]
→ paid acquisition / demand / performance
```

Neither plugin imports or owns the other plugin's bundle contract.

A future higher-level `yandex-growth` workflow may compose both, but it is out of scope for Phase 6B.

## 29. Tests and evals

Offline tests must cover at minimum:

- plugin package/manifests/eleven skills/evals;
- explicit Direct-required capability detection;
- no credentials/endpoints/HTTP imports;
- KPI fingerprint equality and mismatch;
- goal-ID identity, not goal-name identity;
- campaign-ID identity, not campaign-name identity;
- conservative query and landing URL normalization;
- no fuzzy/stemming query merge;
- no URL query-parameter deletion;
- Direct/Metrika cost/conversion/revenue never summed;
- canonical versus reconciliation-only metric roles;
- compatible CPA/CR/ROAS calculations;
- missing-revenue guard;
- currency/VAT/context incompatibility;
- period alignment and maturity states;
- conversion reconciliation classifications;
- Wordstat demand enrichment without treating demand as guaranteed inventory;
- search-query expansion candidates;
- zero-conversion exclusion guard against universal kill rules;
- landing/traffic mismatch as hypotheses;
- budget candidates without automatic mutation;
- transparent prioritization without hidden score;
- delegated Direct/Metrika action previews with `requires_approval=true`;
- source limitation propagation;
- optional Search enrichment;
- no network in tests.

Agent evals must cover all eleven skills and include both read-only and preview-first delegated-action scenarios. Repository validation currently checks eval fixture structure/expectation fields; it does not execute those prompts against a model, so fixture presence is not evidence that agent behavior has been semantically evaluated.

## 30. Repository integration

Phase 6B adds:

- `plugins/yandex-marketing/`;
- marketplace metadata entry;
- README/service matrix/roadmap updates;
- dedicated path-aware `Yandex Marketing plugin` CI job;
- root tests validating discovery and cross-service contracts.

Functional files inside Direct, Metrika, Wordstat, Search, Webmaster, and SEO must remain unchanged unless a later separately approved compatibility change becomes necessary.

## 31. Git stacking

Initial branch and PR structure:

```text
phase-5-yandex-search
        ↓
phase-6-yandex-seo       (PR #6)
        ↓
phase-6b-yandex-marketing
        ↓
PR #7 → phase-6-yandex-seo
```

After preceding PRs merge, retarget stacked PRs appropriately; do not merge them automatically.

## 32. Definition of Done

The Phase 6B design is implemented when:

- 11 production skills are discoverable;
- 8 pure-data standard-library helpers exist;
- Direct is enforced as the required source;
- Marketing Evidence Bundle is versioned and provenance-aware;
- KPI fingerprint prevents invalid efficiency comparisons;
- Direct/Metrika overlapping metrics are reconciled rather than summed;
- goal/attribution/currency/VAT/period/maturity context is preserved;
- demand planning and query intelligence use Wordstat without equating demand to available paid inventory;
- Search is optional context only;
- query/landing joins are conservative;
- the executable finding taxonomy matches Section 20 and current helper constants;
- no universal performance thresholds or hidden Marketing Score exist;
- delegated writes remain previews owned by Direct/Metrika skills;
- no Yandex credentials, endpoints, or HTTP clients exist in the plugin;
- offline tests/evals fixtures and repository structural validators pass;
- root validator and path-aware CI are updated;
- existing plugin functional trees remain unchanged except separately approved compatibility/fix changes.
