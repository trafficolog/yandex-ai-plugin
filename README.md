# Yandex AI Plugins

A marketplace monorepo of independent AI plugins for working with Yandex services from AI agents and coding assistants.

The repository ships a **first-release set of seven independently installable plugins** with one shared architecture, safety model, validation contract and CI pipeline:

- Yandex Direct;
- Yandex Metrika;
- Yandex Webmaster;
- Yandex Wordstat;
- Yandex Search;
- Yandex SEO — cross-service organic-search orchestration;
- Yandex Marketing — cross-service paid-acquisition orchestration.

This repository is intentionally **not one giant Yandex skill**. Installation/versioning happens at plugin level; workflow knowledge is split into focused skills inside each plugin; volatile API behavior stays inside the owning service plugin; cross-service plugins compose structured outputs instead of duplicating API clients.

> **Release status:** the Phase 1–6B feature set is the frozen scope of the first release. Operations / AI / Mobile integrations are kept in backlog for later releases; see [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Table of contents

- [Why this architecture](#why-this-architecture)
- [First-release plugins](#first-release-plugins)
- [Repository structure](#repository-structure)
- [Installation and discovery](#installation-and-discovery)
- [Execution model](#execution-model)
- [Common safety contract](#common-safety-contract)
- [Plugin guides](#plugin-guides)
  - [Yandex Direct](#yandex-direct)
  - [Yandex Metrika](#yandex-metrika)
  - [Yandex Webmaster](#yandex-webmaster)
  - [Yandex Wordstat](#yandex-wordstat)
  - [Yandex Search](#yandex-search)
  - [Yandex SEO](#yandex-seo)
  - [Yandex Marketing](#yandex-marketing)
- [Cross-service architecture](#cross-service-architecture)
- [Data and evidence semantics](#data-and-evidence-semantics)
- [Authentication and secrets](#authentication-and-secrets)
- [Files, large datasets and artifacts](#files-large-datasets-and-artifacts)
- [Testing and validation](#testing-and-validation)
- [Versioning and releases](#versioning-and-releases)
- [Reviewing the first release](#reviewing-the-first-release)
- [Roadmap and backlog](#roadmap-and-backlog)
- [Sources and licensing](#sources-and-licensing)

---

## Why this architecture

The project follows several deliberate boundaries.

### Plugin = installation and version boundary

Each Yandex service is independently installable and independently versioned. A user that only needs Webmaster should not have to install advertising or analytics capabilities.

```text
marketplace repository
├── yandex-direct
├── yandex-metrika
├── yandex-webmaster
├── yandex-wordstat
├── yandex-search
├── yandex-seo
└── yandex-marketing
```

### Skill = workflow and knowledge boundary

A plugin contains multiple discoverable skills. Skills are small enough to represent a recognizable task such as reporting, recrawl, query research, SERP clustering, conversion reconciliation or budget review.

### Service plugin owns API volatility

Endpoint versions, authentication details, quotas, API-specific lifecycle behavior and service-specific writes stay in the service plugin that owns them.

For example:

- Webmaster owns v4/v4.1 routing and recrawl/sitemap/feed mutations;
- Wordstat owns Cloud Wordstat v2 request behavior;
- Search owns sync/deferred Search API v2 retrieval;
- Direct owns Reports v501 and Direct write flows;
- Metrika owns Reporting, Management, Logs and imports.

### Cross-service plugin owns reasoning, not transport

`yandex-seo` and `yandex-marketing` contain **no Yandex HTTP/API client layer**. Their helpers consume structured JSON/artifacts produced by service plugins, align context and quality metadata, derive findings, and prepare delegated action previews.

This avoids a common failure mode where the same API is implemented differently in multiple orchestration layers.

### Official documentation is the source of truth

Donor repositories are useful for workflow ideas, capability discovery and UX patterns, but current Yandex documentation is treated as canonical for API behavior. Third-party influences are recorded in plugin `THIRD_PARTY_NOTICES.md` and source references.

---

## First-release plugins

| Plugin | Version | Type | Primary scope | Live writes in this plugin? |
|---|---:|---|---|---|
| [`yandex-direct`](plugins/yandex-direct/) | 1.0.0 | service | Campaigns, reports, audit, keywords, budgets, safe optimization | Yes, only through preview + explicit approval |
| [`yandex-metrika`](plugins/yandex-metrika/) | 1.0.0 | service | Reporting, conversions, ecommerce, attribution, goals, Logs, imports | Yes, selected Management/import operations with guards |
| [`yandex-webmaster`](plugins/yandex-webmaster/) | 1.0.0 | service | Search queries, indexing, recrawl, sitemaps, links, feeds, exports | Yes, quota/destructive operations require preview + approval |
| [`yandex-wordstat`](plugins/yandex-wordstat/) | 1.0.0 | service | Demand, semantics, frequency, dynamics, regions, trends | No consequential mutation surface in 1.0.0 |
| [`yandex-search`](plugins/yandex-search/) | 1.0.0 | service | Web SERP, batch retrieval, snapshots, rankings, competitors, clustering | No |
| [`yandex-seo`](plugins/yandex-seo/) | 1.0.0 | cross-service | Organic evidence, opportunities, gaps, cannibalization, CTR/conversion/technical context | **No — delegated preview only** |
| [`yandex-marketing`](plugins/yandex-marketing/) | 1.0.0 | cross-service | Paid-acquisition evidence, reconciliation, demand/query/landing/budget opportunities | **No — delegated preview only** |

Detailed service coverage is maintained in [`docs/SERVICE_MATRIX.md`](docs/SERVICE_MATRIX.md).

---

## Repository structure

```text
.
├── .agents/
│   └── plugins/marketplace.json        # marketplace metadata for agent environments
├── .claude-plugin/
│   └── marketplace.json                # marketplace metadata for Claude-compatible discovery
├── .github/
│   └── workflows/ci.yml                # repository + path-aware plugin CI
├── plugins/
│   ├── yandex-direct/
│   ├── yandex-metrika/
│   ├── yandex-webmaster/
│   ├── yandex-wordstat/
│   ├── yandex-search/
│   ├── yandex-seo/
│   └── yandex-marketing/
├── docs/
│   ├── PLUGIN_STANDARD.md
│   ├── SERVICE_MATRIX.md
│   ├── ROADMAP.md
│   ├── REVIEW_FIRST_RELEASE.md
│   └── superpowers/
│       ├── specs/                       # approved architecture/design specs
│       └── plans/                       # implementation plans
├── workflows/                           # cross-repository workflow conventions / future shared workflows
├── packages/                            # reserved shared packages; intentionally minimal in first release
├── scripts/
│   └── validate_repo.py                 # repository contract validator
├── tests/                               # root marketplace/architecture tests
├── CHANGELOG.md
└── README.md
```

A typical plugin has this shape:

```text
plugins/yandex-<service>/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── skills/<skill-name>/SKILL.md
├── references/
├── scripts/
├── tests/
├── evals/
├── README.md
├── CHANGELOG.md
└── THIRD_PARTY_NOTICES.md
```

Service plugins can additionally contain `.env.example` when credentials are required. Cross-service plugins intentionally do not.

---

## Installation and discovery

### Import the repository as a marketplace

Root marketplace metadata is available in:

```text
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
```

Import the GitHub repository as a marketplace in an environment that supports compatible plugin discovery, then install only the plugins needed for the task.

### Install by responsibility, not by bundle size

Examples:

- Direct reporting only → install `yandex-direct`;
- technical SEO / indexing → install `yandex-webmaster`;
- keyword demand research → install `yandex-wordstat`;
- real SERP clustering → install `yandex-search`;
- full organic analysis → install Wordstat + Search + Webmaster + Metrika + `yandex-seo`;
- paid acquisition → install Direct plus relevant Metrika/Wordstat sources + `yandex-marketing`.

### Cross-service dependency model

Cross-service plugins are capability-driven rather than monolithic hard dependencies.

`yandex-seo` can operate with partial evidence:

```text
Discovery   = Wordstat + Search
Visibility  = Search + Webmaster
Performance = Webmaster + Metrika
Full SEO    = Wordstat + Search + Webmaster + Metrika
```

`yandex-marketing` always requires Direct evidence, then enriches it:

```text
Direct only          = Direct
Paid performance     = Direct + Metrika
Demand planning      = Direct + Wordstat
Query intelligence   = Direct + Wordstat
Full acquisition     = Direct + Metrika + Wordstat
Competitive context  = Direct + optional Search context
```

Missing evidence must reduce coverage and confidence rather than cause the agent to invent substitute facts.

---

## Execution model

The project uses a backend-agnostic workflow model:

```text
skill
  ↓
compatible connected MCP/app when available
  ↓
bundled helper
  ↓
file/export fallback when supported
```

The skill contains the workflow and interpretation contract. Helpers provide deterministic execution where useful. A future connected execution backend should not change the analytical semantics of the skill.

### Why helpers are dependency-light

The first release intentionally favors Python standard-library helpers:

- easier inspection during agent execution;
- fewer supply-chain/runtime dependencies;
- simpler packaging;
- deterministic offline unit tests;
- portable use in Codex/Claude/CLI-like environments.

### Large datasets

Large SERP, Logs, archive or export results should be written to files/artifacts rather than pasted into context. Skills should summarize the important structure and preserve the raw artifact path when available.

---

## Common safety contract

Consequential actions use one shared lifecycle:

```text
read
  ↓
analyze
  ↓
preview exact action
  ↓
explicit user approval
  ↓
write
  ↓
verify
```

### Safety invariants

1. **A recommendation is not permission.**
2. **Draft creation is not activation/publication.**
3. **A cross-service plugin never bypasses the owning service plugin's mutation contract.**
4. **Destructive or quota-consuming targets must be explicit.**
5. **Credentials never belong in skills, examples, logs or generated previews.**
6. **No universal optimization threshold is treated as platform truth.**

Examples:

- SEO recommends recrawl → delegation goes to `yandex-webmaster-recrawl`, which performs its own preview/approval flow;
- Marketing proposes budget reallocation → delegation goes to `yandex-direct-budget`;
- Marketing proposes goal changes → delegation goes to `yandex-metrika-goals`;
- creating a Direct campaign and activating it remain separate decisions.

---

# Plugin guides

## Yandex Direct

Path: [`plugins/yandex-direct/`](plugins/yandex-direct/)

The first-release Direct plugin is the advertising execution and analysis layer.

### Skills

- `yandex-direct` — router;
- `yandex-direct-api` — low-level API usage;
- `yandex-direct-audit` — account/campaign audit;
- `yandex-direct-budget` — budget analysis and guarded changes;
- `yandex-direct-create` — campaign/ad creation workflow;
- `yandex-direct-keywords` — keyword/search-query/negative workflows;
- `yandex-direct-optimize` — evidence-based optimization;
- `yandex-direct-reporting` — performance/reporting workflows.

### Important correctness rules

- Reports use the current v501 report surface used by this release.
- 201/202 report polling preserves the original payload and report name and respects `retryIn`.
- Criterion analysis keeps keyword/autotargeting and criterion types explicit.
- Shared negatives and autotargeting are first-class concepts.
- Revenue-dependent metrics are not invented when revenue is absent.
- No universal CPA/CPC/CTR/ROAS kill rule is encoded.
- Before optimization, clarify business objective, goal and data sufficiency.

### Writes

Direct can perform consequential writes, but only after exact preview and explicit approval. Activation/publication must not be silently coupled to object creation.

---

## Yandex Metrika

Path: [`plugins/yandex-metrika/`](plugins/yandex-metrika/)

Metrika provides analytics, conversion and data-quality context for both standalone analytics and cross-service workflows.

### Core areas

- reporting and period comparison;
- goals/conversions;
- ecommerce;
- attribution;
- Logs API lifecycle;
- management operations;
- offline conversion/call/expense imports.

### Data-quality metadata is part of the result

The plugin preserves and surfaces fields such as:

- sampling state/share;
- sample size/space;
- data lag;
- sensitive-data markers;
- row rounding where applicable.

Cross-service plugins are required to propagate these limitations rather than discard them.

### Important guards

- incompatible/legacy attribution assumptions are rejected rather than silently mapped;
- Logs lifecycle is explicit: evaluate → create → status → download → clean;
- expense import protects against duplicating native Yandex Direct expenses;
- goal writes are preview-first;
- unrelated goals are not silently aggregated into one business conversion KPI.

---

## Yandex Webmaster

Path: [`plugins/yandex-webmaster/`](plugins/yandex-webmaster/)

Webmaster is the service plugin for technical/search visibility evidence and Webmaster mutations.

### Skills cover

- site/host management;
- audits/diagnostics;
- search-query analytics/history;
- indexing/search-presence history;
- recrawl queue/quota;
- sitemaps and priority sitemap recrawl;
- links;
- feeds;
- exports/archives;
- raw API workflows.

### Mixed endpoint versions

The plugin intentionally does not pretend that the whole Webmaster API has one uniform version. Standard resources use the appropriate v4 routes while priority Sitemap recrawl uses v4.1 routes captured by the release references.

### Important semantics

- crawl/index/search presence are distinct concepts;
- popular queries/top-N are not described as complete site query coverage;
- recrawl is quota-consuming and does not guarantee indexing or ranking;
- sitemap submission does not guarantee inclusion;
- feed mutations require their documented host/scheme context;
- destructive host/sitemap/feed operations require exact target approval.

---

## Yandex Wordstat

Path: [`plugins/yandex-wordstat/`](plugins/yandex-wordstat/)

Wordstat is the external-demand and semantic research layer.

### Core capabilities

- GetTop-based demand research;
- nested results and associations kept separate;
- provenance-aware seed expansion;
- operator-aware frequency work;
- dynamics/seasonality;
- regions and affinity;
- trend classification;
- quota/cost planning.

### Important interpretation rules

Wordstat phrase counts can overlap. Therefore:

> The plugin never sums overlapping phrase counts and labels the result "total market demand".

`results` and `associations` remain semantically distinct. After deduplication, all relevant seed provenance is retained rather than keeping only the first source.

Regional volume and affinity are separate signals: a large absolute region is not necessarily the strongest relative-interest region.

Trend classification distinguishes growth from low-volume percentage noise and recurring seasonality.

---

## Yandex Search

Path: [`plugins/yandex-search/`](plugins/yandex-search/)

Search provides actual web SERP evidence and the real URL-overlap signal used for SEO clustering.

### Core capabilities

- synchronous web search;
- deferred/async search lifecycle;
- cost-aware batch planning;
- XML structured parsing;
- optional raw HTML artifact preservation;
- reproducible SERP snapshots;
- competitor presence analysis;
- ranking comparison;
- URL-overlap and Jaccard clustering.

### Structured SEO mode

For rank/clustering workflows, the release uses flat result semantics rather than deep domain grouping. This avoids treating domain grouping artifacts as genuine URL overlap.

### Reproducibility

SERP snapshots preserve a configuration fingerprint such as query, region/index, grouping and related request context. Ranking comparison rejects materially incompatible snapshots instead of reporting a misleading rank delta.

### Clustering

The clustering threshold is explicit. There is no hidden universal rule that N shared URLs always means one intent.

Connected-component clustering also reports bridge risk so that:

```text
A ↔ B strong overlap
B ↔ C strong overlap
A ↔ C weak/no overlap
```

is not presented as a perfectly homogeneous cluster.

### Cost behavior

Interactive and batch workloads are separated because deferred search can have materially different economics from synchronous retrieval. Batch helpers provide cost preview rather than blindly looping expensive sync calls.

---

## Yandex SEO

Path: [`plugins/yandex-seo/`](plugins/yandex-seo/)

`yandex-seo` is the first cross-service plugin. It has **no Yandex credentials or transport layer**.

```text
Wordstat ─ demand / trends / regions
Search ─── SERP / intent / clusters
Webmaster  impressions / clicks / position / indexing
Metrika ── visits / landing / goals / conversions
        ↓
SEO Evidence Bundle
        ↓
findings + prioritization + delegated previews
```

### Evidence bundle

The versioned SEO Evidence Bundle preserves:

- source provenance;
- period context;
- geography context;
- query/page/cluster relationships;
- quality limitations;
- distinction between observed and inferred statements.

Evidence/finding semantics:

- `OBSERVED` — reported by a source;
- `DERIVED` — deterministic calculation from observations;
- `HYPOTHESIS` — interpretation requiring validation.

### Important invariants

- Wordstat demand and Webmaster demand are **not automatically interchangeable**.
- Visitor geography from Metrika is not silently treated as the Search ranking region.
- Query joins are conservative; no automatic stemming/fuzzy merge.
- URL query parameters are retained by default.
- Metrika sampling/data lag, Webmaster top-N limitations and Search bridge risk propagate into final findings.
- A Wordstat phrase alone is a discovery candidate, not automatically a validated content gap.
- Cannibalization requires evidence of competing own URLs, not merely two matching strings.
- CTR opportunities use comparable/site evidence, not universal position→CTR benchmarks.
- Conversion/intent explanations remain hypotheses unless the data supports stronger causality.
- There is no opaque universal SEO score.

### Writes

None. `yandex-seo` may emit a delegated action preview, but the owning service plugin must execute any approved action.

---

## Yandex Marketing

Path: [`plugins/yandex-marketing/`](plugins/yandex-marketing/)

`yandex-marketing` is the paid-acquisition cross-service layer. It also contains no Yandex credentials or transport clients.

```text
Direct ─── campaigns / spend / clicks / criteria / queries
Metrika ── sessions / goals / ecommerce / landing behavior
Wordstat ─ external demand / seasonality
Search ─── optional intent / competitive context
       ↓
Marketing Evidence Bundle
       ↓
reconciliation + findings + prioritization + delegated previews
```

### Direct is mandatory

Without Direct evidence, the router must not pretend that a task is a paid-acquisition analysis. It can route the user toward Metrika, Wordstat or Search workflows instead.

### KPI fingerprint

Performance comparisons retain the context that makes them meaningful:

```text
business objective
+ goal IDs
+ attribution model
+ metric basis
+ currency
+ VAT basis
+ period
```

A campaign optimized to a business purchase goal is not declared worse than a campaign optimized to an easier micro-conversion simply because the second has a lower numeric CPA.

### No Direct/Metrika double counting

Overlapping values are reconciled, not added:

```text
Direct cost           = canonical paid-cost evidence
Metrika Direct cost   = reconciliation/context evidence
```

The same rule applies to overlapping conversion and revenue views. Different date bases, attribution contexts or goal definitions can legitimately produce different values.

### Demand/query semantics

A high Wordstat count with low Direct coverage is a **demand expansion candidate**, not proof that the same number of ad impressions was lost.

A search term with zero conversions is not automatically a negative-keyword recommendation. Maturity, objective, spend, conversion delay and evidence sufficiency matter.

### Findings and writes

Landing mismatch and traffic-quality conclusions are hypotheses from observational data. Budget changes, negatives, optimization and goal changes are only delegated previews to their owning service skills and require explicit approval there.

---

## Cross-service architecture

The first release deliberately stops at two domain-specific cross-service layers rather than introducing a generic "Yandex everything" agent.

```text
                         ┌─────────────────┐
                         │  Yandex Wordstat │
                         └────────┬────────┘
                                  │
             ┌────────────────────┼─────────────────────┐
             │                    │                     │
             ▼                    ▼                     ▼
      ┌─────────────┐      ┌──────────────┐      ┌──────────────┐
      │Yandex Search│      │Yandex Webmaster│     │Yandex Direct │
      └──────┬──────┘      └──────┬───────┘      └──────┬───────┘
             │                    │                     │
             └─────────┬──────────┘                     │
                       │                                │
                       ▼                                │
                ┌────────────┐                          │
                │ yandex-seo │◄──── Yandex Metrika ────┼────► yandex-marketing
                └────────────┘                          │          ▲
                                                       └──────────┘
```

The diagram shows analytical composition, not credential sharing. Service plugins remain independently responsible for execution.

### Why SEO and Marketing are separate

Organic and paid acquisition share some sources but answer different questions.

`yandex-seo` asks about:

- external demand;
- organic SERP intent;
- search visibility;
- indexing/technical blockers;
- organic landing/conversion outcomes.

`yandex-marketing` asks about:

- paid spend and delivery;
- paid queries/criteria;
- campaign KPI context;
- Direct↔Metrika reconciliation;
- paid demand coverage;
- landing/budget/query opportunities.

Combining these into one cross-service plugin would create ambiguous metric ownership and a much larger safety surface.

---

## Data and evidence semantics

Cross-service correctness depends more on context than on arithmetic.

### Source provenance

A metric should retain where it came from. Similar names do not imply equivalent definitions.

Examples:

- Wordstat demand ≠ Webmaster demand by default;
- Direct conversion view ≠ generic Metrika conversion report by default;
- Direct revenue ≠ complete ecommerce revenue by default;
- Metrika visitor region ≠ Search SERP region.

### Temporal alignment

Evidence can be classified as:

- `EXACT` — materially equivalent periods/context;
- `APPROXIMATE` — usable with disclosed timing difference;
- `MISMATCHED` — invalid for direct comparative interpretation.

Wordstat rolling windows, point-in-time SERP snapshots, Webmaster date ranges and Metrika periods must not be silently described as one identical measurement interval.

### Data maturity

Paid conversion analysis can additionally preserve:

- `MATURE`;
- `IMMATURE`;
- `MATURITY_UNKNOWN`.

There is intentionally no hard-coded "ignore the last N days" rule.

### Conservative identity joins

Where possible, stable IDs are preferred:

- campaign ID over campaign name;
- goal ID over goal label;
- criterion identity over display text.

Query normalization is limited to safe lexical normalization unless a workflow explicitly introduces another relation. URL normalization retains query parameters by default.

---

## Authentication and secrets

### Service plugins

Credentials are configured only for plugins that actually call the corresponding Yandex service. See each plugin's `.env.example` and references for the exact release contract.

Common patterns include:

```text
Authorization: OAuth <token>
Authorization: Api-Key <key>
Authorization: Bearer <IAM token>
```

The exact mechanism is service-specific.

### Secret-handling rules

- keep tokens/keys in environment variables or connected app credential storage;
- never commit real secrets;
- never echo full Authorization headers in previews/logs;
- redact credentials in dry-run output;
- do not copy service credentials into cross-service plugins.

### Cross-service plugins

`yandex-seo` and `yandex-marketing` intentionally have **no credential surface**. They consume artifacts produced by service plugins.

---

## Files, large datasets and artifacts

Some Yandex APIs naturally produce more data than should be inserted into an agent context.

Examples:

- Metrika Logs parts;
- Webmaster archive/PRO exports;
- large Search batch results;
- large semantic collections;
- SERP snapshot datasets.

Preferred behavior:

1. preserve the raw result as a file/artifact;
2. retain enough metadata to reproduce/identify it;
3. return compact analytical summaries;
4. avoid truncating data and then claiming complete coverage.

---

## Testing and validation

The repository combines a root validator, root architecture tests and per-plugin offline regression suites.

### Root checks

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

### Direct

```bash
cd plugins/yandex-direct
python -m unittest discover -s tests -v
python -m py_compile scripts/yd_api.py scripts/yd_report.py
```

### Metrika

```bash
cd plugins/yandex-metrika
python -m unittest discover -s tests -v
python -m py_compile scripts/_http.py scripts/ym_api.py scripts/ym_report.py scripts/ym_logs.py scripts/ym_import.py
```

### Webmaster

```bash
cd plugins/yandex-webmaster
python -m unittest discover -s tests -v
python -m py_compile scripts/_http.py scripts/yw_api.py scripts/yw_queries.py scripts/yw_indexing.py scripts/yw_recrawl.py scripts/yw_sitemaps.py scripts/yw_feeds.py scripts/yw_export.py
```

### Wordstat

```bash
cd plugins/yandex-wordstat
python -m unittest discover -s tests -v
python -m py_compile scripts/_http.py scripts/ywstat_api.py scripts/ywstat_top.py scripts/ywstat_semantics.py scripts/ywstat_dynamics.py scripts/ywstat_regions.py scripts/ywstat_trends.py
```

### Search

```bash
cd plugins/yandex-search
python -m unittest discover -s tests -v
python -m py_compile scripts/_http.py scripts/ys_api.py scripts/ys_request.py scripts/ys_parse.py scripts/ys_async.py scripts/ys_batch.py scripts/ys_serp.py scripts/ys_overlap.py scripts/ys_compare.py
```

### SEO

```bash
cd plugins/yandex-seo
python -m unittest discover -s tests -v
python -m py_compile scripts/seo_context.py scripts/seo_bundle.py scripts/seo_join.py scripts/seo_quality.py scripts/seo_opportunities.py scripts/seo_cannibalization.py scripts/seo_prioritize.py
```

### Marketing

```bash
cd plugins/yandex-marketing
python -m unittest discover -s tests -v
python -m py_compile scripts/marketing_context.py scripts/marketing_bundle.py scripts/marketing_join.py scripts/marketing_quality.py scripts/marketing_performance.py scripts/marketing_demand.py scripts/marketing_opportunities.py scripts/marketing_prioritize.py
```

### Path-aware CI

`.github/workflows/ci.yml` detects shared/root changes and plugin-specific changes. Shared contract changes intentionally trigger regression coverage across the affected plugin set; isolated plugin changes avoid running unrelated work where possible.

The first release was developed with explicit RED→GREEN tests for the major behavior contracts and with a final server-side GitHub Actions gate before release finalization.

---

## Versioning and releases

Each plugin has independent SemVer.

The first repository release ships the following plugin versions:

```text
yandex-direct-suite  1.0.0
yandex-metrika       1.0.0
yandex-webmaster     1.0.0
yandex-wordstat      1.0.0
yandex-search        1.0.0
yandex-seo           1.0.0
yandex-marketing     1.0.0
```

A future change to one service does not require artificially incrementing every plugin.

Release history is summarized in [`CHANGELOG.md`](CHANGELOG.md); plugin-specific changes remain documented in their local changelogs.

---

## Reviewing the first release

For an independent architecture/code review, start with:

[`docs/REVIEW_FIRST_RELEASE.md`](docs/REVIEW_FIRST_RELEASE.md)

That document provides:

- the recommended inspection order;
- architecture invariants to challenge;
- API-specific high-risk assumptions;
- cross-service double-counting/context checks;
- mutation-safety checks;
- suggested adversarial scenarios;
- known intentional limitations of 1.0.0.

The approved designs are under [`docs/superpowers/specs/`](docs/superpowers/specs/) and are useful for checking implementation-vs-design drift.

---

## Roadmap and backlog

The first-release scope is frozen at **Phase 6B**.

Completed release phases:

1. Marketplace foundation + Direct;
2. Metrika;
3. Webmaster;
4. Wordstat;
5. Search;
6. SEO cross-service layer;
7. Marketing cross-service layer.

The previously named "Phase 7 — Operations, AI, Mobile" is **not part of the first release**. Tracker, Yandex 360, Maps, AppMetrica, YandexGPT and SpeechKit are kept in the future-release backlog together with other possible extensions. See [`docs/ROADMAP.md`](docs/ROADMAP.md).

No backlog item should be interpreted as a compatibility promise or release date.

---

## Standards and design documents

- [`docs/PLUGIN_STANDARD.md`](docs/PLUGIN_STANDARD.md) — mandatory plugin structure, safety, versioning and eval conventions;
- [`docs/SERVICE_MATRIX.md`](docs/SERVICE_MATRIX.md) — current shipped/planned service coverage;
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — completed first-release phases and future backlog;
- [`docs/REVIEW_FIRST_RELEASE.md`](docs/REVIEW_FIRST_RELEASE.md) — independent review guide;
- [`docs/superpowers/specs/2026-09-01-yandex-ai-marketplace-design.md`](docs/superpowers/specs/2026-09-01-yandex-ai-marketplace-design.md) — marketplace architecture baseline;
- subsequent specs in [`docs/superpowers/specs/`](docs/superpowers/specs/) — service and cross-service design decisions;
- implementation plans in [`docs/superpowers/plans/`](docs/superpowers/plans/).

---

## Sources and licensing

Repository-authored code is MIT unless a plugin or vendored/upstream notice states otherwise.

Each plugin documents relevant third-party donor projects and public documentation in `THIRD_PARTY_NOTICES.md` and/or `references/sources.md`.

Third-party projects are treated as methodology/capability references where appropriate; their existence does not override current official Yandex API documentation.

---

## First-release principles in one page

If you only read one section, these are the contracts the repository is designed to preserve:

1. **Install services independently.** Do not turn the marketplace back into a monolith.
2. **Keep volatile APIs in owning service plugins.** Cross-service reasoning should consume outputs, not reimplement endpoints.
3. **Preserve provenance and context.** Similar metric names are not sufficient grounds to merge them.
4. **Do not double-count overlapping service views.** Especially Direct↔Metrika and Wordstat↔Webmaster demand-like metrics.
5. **No magic optimization thresholds.** Targets and weights must come from business/user context or clearly identified evidence.
6. **No causal certainty from observational correlation.** Use `HYPOTHESIS` when that is what the evidence supports.
7. **A recommendation is not permission.** Consequential writes require preview and explicit approval in the owning service plugin.
8. **Keep secrets out of content and previews.** Cross-service plugins need no credentials.
9. **Expose data-quality limitations.** Sampling, lag, top-N coverage, timing mismatch and cluster bridge risk are part of the answer.
10. **Prefer reproducibility.** Preserve request/snapshot/config context needed to explain how a result was produced.
11. **Use artifacts for large outputs.** Do not pretend a truncated context contains the complete dataset.
12. **Treat backlog as backlog.** The first release intentionally stops at the current seven-plugin set.
