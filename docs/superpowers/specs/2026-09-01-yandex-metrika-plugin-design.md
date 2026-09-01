# Yandex Metrika Plugin — Phase 2 Design

**Date:** 2026-09-01  
**Repository:** `trafficolog/yandex-ai-plugin`  
**Branch:** `phase-2-yandex-metrika`  
**Status:** Approved for implementation

## 1. Goal

Add `plugins/yandex-metrika/` as the second production plugin in the Yandex AI marketplace monorepo. The plugin must match the Phase 1 Direct standard: independent installability/versioning, specialized skills, current API references, offline tests/evals, read-first behavior, preview-before-write safety, and backend-agnostic execution.

The plugin is not a thin copy of an upstream skill and not a full MCP server. It is a workflow/reasoning layer with dependency-free local API helpers and optional compatibility with connected MCP/app backends.

## 2. Current API baseline

The current Yandex Metrika API documentation defines four major API families:

1. **Management API** — counters, goals, filters, access and other managed objects, including CRM management endpoints.
2. **Data Import API** — expenses, CRM clients/orders, calls, offline conversions and visitor parameters.
3. **Reporting API** — tabular reports, by-time reports, segment comparison, drilldown and comparison drilldown.
4. **Logs API** — non-aggregated visit/hit data prepared asynchronously and downloaded in parts.

Canonical documentation:

- https://yandex.ru/dev/metrika/ru/
- https://yandex.ru/dev/metrika/ru/management/
- https://yandex.ru/dev/metrika/ru/stat/
- https://yandex.ru/dev/metrika/ru/logs/

Authentication uses a Yandex OAuth token. Secrets must only come from environment/app credentials and must never be committed or echoed in previews.

## 3. Plugin structure

```text
plugins/yandex-metrika/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── .env.example
├── README.md
├── CHANGELOG.md
├── THIRD_PARTY_NOTICES.md
├── skills/
│   ├── yandex-metrika/
│   ├── yandex-metrika-audit/
│   ├── yandex-metrika-reporting/
│   ├── yandex-metrika-conversions/
│   ├── yandex-metrika-ecommerce/
│   ├── yandex-metrika-attribution/
│   ├── yandex-metrika-goals/
│   ├── yandex-metrika-logs/
│   ├── yandex-metrika-imports/
│   └── yandex-metrika-api/
├── references/
│   ├── api-2026.md
│   ├── reporting.md
│   ├── attribution.md
│   ├── audit-framework.md
│   ├── logs.md
│   ├── imports.md
│   ├── safety.md
│   └── sources.md
├── scripts/
│   ├── __init__.py
│   ├── _http.py
│   ├── ym_api.py
│   ├── ym_report.py
│   ├── ym_logs.py
│   └── ym_import.py
├── evals/scenarios.json
└── tests/
    ├── test_plugin_layout.py
    ├── test_ym_api.py
    ├── test_ym_report.py
    ├── test_ym_logs.py
    └── test_ym_import.py
```

Initial semantic version: `1.0.0`.

## 4. Skill boundaries

### `yandex-metrika`
Router for ambiguous or cross-cutting Metrika requests. It selects the specialized skill and establishes counter/date/goal/attribution context before analysis.

### `yandex-metrika-audit`
Evidence-first audit of counter configuration and measurement quality. Areas: counter identity/timezone, business goals, conversion coverage, ecommerce data, UTM/source quality, Direct linkage where relevant, sampling/data lag, sensitive-data limitations, attribution choice and suspicious gaps. Findings use `PASS / ISSUE / REVIEW / N/A` rather than folklore thresholds.

### `yandex-metrika-reporting`
Traffic, source/channel, landing/page, UTM, device, geography, time-series and period-comparison analysis. Every result must expose material quality metadata returned by the API.

### `yandex-metrika-conversions`
Goal-based conversion analysis and funnel reasoning. It must distinguish goal reach, conversion rate, user/session basis and business outcome; it must not assume every configured goal is a primary conversion.

### `yandex-metrika-ecommerce`
Orders, revenue, products, average order value and ecommerce performance. It must separate transactional metrics from goal-based conversions and state the reporting currency/model when relevant.

### `yandex-metrika-attribution`
Selects and explains attribution models for the analytical question. Current documented models include:

- `cross_device_first`
- `last`
- `cross_device_last_significant`
- `automatic`

As of 2026-06-25, requests using several legacy models are mapped by Yandex to current analogues. The plugin must not silently hard-code a legacy `lastsign` model.

Canonical reference:
https://yandex.ru/dev/metrika/ru/stat/param

### `yandex-metrika-goals`
Reads goal configuration and proposes/executes goal creation/update/delete workflows. Goal deletion is destructive and always approval-gated.

### `yandex-metrika-logs`
Implements the Logs API lifecycle:

```text
evaluate → create → poll → download parts → clean
```

`clean` is a consequential write and must be previewed/approved. A single Logs request must not exceed the documented one-year period limit.

Canonical reference:
https://yandex.ru/dev/metrika/ru/logs/practice/quick-start

### `yandex-metrika-imports`
Covers data-import workflows: offline conversions, calls, expenses, visitor parameters and CRM data. It validates local CSV inputs before network upload, produces a preview and requires explicit approval before execution.

Direct expenses must not be manually uploaded through the expense import workflow because Yandex Direct transfers its cost data automatically; manual upload can duplicate costs.

Canonical reference:
https://yandex.ru/dev/metrika/ru/management/openapi/expense/uploadMultipart

### `yandex-metrika-api`
Low-level API payload/endpoint debugging and generic read/write operations when a higher-level workflow is unsuitable. Consequential methods remain dry-run by default.

## 5. Reporting correctness contract

Reporting helpers must support the current `/stat/v1/data` family:

- table: `/stat/v1/data`
- by time: `/stat/v1/data/bytime`
- comparison: `/stat/v1/data/comparison`
- drilldown: `/stat/v1/data/drilldown`
- comparison drilldown: `/stat/v1/data/comparison/drilldown`

The helper must surface these response fields when present:

- `sampled`
- `sample_share`
- `sample_size`
- `sample_space`
- `data_lag`
- `contains_sensitive_data`
- `total_rows_rounded`

A result derived from sampled or limited data must not be described as exact without qualification.

`accuracy` is explicit in the request helper. The plugin may request full accuracy when justified, but must not force expensive/full accuracy for every query.

Canonical references:

- https://yandex.ru/dev/metrika/ru/stat/openapi/data
- https://yandex.ru/dev/metrika/ru/stat/openapi/bytime
- https://yandex.ru/dev/metrika/ru/stat/openapi/drilldown
- https://yandex.ru/dev/metrika/ru/stat/openapi/comparison_drilldown

## 6. Execution layer

### `scripts/_http.py`
Shared dependency-free HTTP primitives for this plugin only: OAuth header creation, URL encoding, JSON request execution, HTTP error normalization and secret redaction.

### `scripts/ym_api.py`
Generic Management API client. Reads are executable by default; methods marked consequential are preview-only unless `--execute` is explicitly supplied. Preview output redacts Authorization.

### `scripts/ym_report.py`
Builds Reporting API queries and parses quality metadata. Supports `table`, `bytime`, `comparison`, `drilldown` and `comparison-drilldown` modes. It accepts explicit counter, dates, metrics, dimensions, filters, accuracy and attribution-related parameters.

### `scripts/ym_logs.py`
Builds and executes Logs API evaluate/create/status/download/clean calls. `clean` defaults to preview-only; create is also treated as a write requiring an explicit execution flag in the CLI helper.

### `scripts/ym_import.py`
Validates CSV files locally and prepares import requests. Supported initial import kinds:

- `offline-conversions`
- `calls`
- `expenses`

The skill/reference layer documents visitor parameters and CRM imports, but the first executable helper release focuses on the three CSV upload families above. This is an intentional Phase 2 scope boundary, not a placeholder.

For expenses, a guard rejects a source explicitly identified as Yandex Direct.

## 7. Safety model

Repository-wide contract:

```text
read → analyze → preview → explicit approval → write → verify
```

Risk classes:

### Read
- reports
- counters
- goals
- Logs evaluate/status/download metadata
- import-upload status

### Consequential write
- create/update counter
- create/update goal
- create Logs request
- import offline conversions/calls/expenses

### Destructive
- delete counter
- delete goal
- clean Logs request data
- deletion/removal of imported or configured resources when supported

Consequential and destructive actions never execute from recommendation language alone.

## 8. Backend-agnostic behavior

Skill instructions describe capabilities rather than fixed MCP tool names.

Preferred execution order:

1. compatible connected Metrika app/MCP when available;
2. bundled local helpers when executable;
3. user-provided exports/files with a reproducible analysis/change plan.

`theYahia/YaAll` may be referenced as an optional MCP backend and coverage donor, but the plugin must not depend on it.

## 9. Donor projects

### `mkultraaaa/claude-yandex-skills`
MIT. Use as workflow/UX inspiration for counters, goals, traffic, conversions, UTM, ecommerce, Direct cost reconciliation, period comparison, cache/context-window patterns.

Do not copy stale limits, absolute paths or legacy attribution assumptions.

### `theYahia/YaAll`
MIT for its own Metrika MCP implementation. Use as capability/testing reference for counters, goals, reports, logs and convenience wrappers. Do not treat it as the canonical API specification.

Official Yandex documentation is authoritative for API behavior.

## 10. Marketplace and monorepo integration

Root `.agents/plugins/marketplace.json` and `.claude-plugin/marketplace.json` add `yandex-metrika` alongside Direct.

`docs/SERVICE_MATRIX.md` marks Metrika `stable` only when all Phase 2 tests pass. `docs/ROADMAP.md` records Phase 2 completion and keeps Webmaster as the next plugin.

Root CI becomes plugin-aware for both Direct and Metrika. Repository validation remains generic and must validate both marketplace entries.

## 11. Testing and evals

Offline tests must cover at least:

- plugin layout and manifests;
- OAuth header construction and redaction;
- read versus write dry-run behavior;
- reporting URL/parameter construction;
- extraction of sampling/data-quality metadata;
- supported/current attribution values;
- Logs one-year period validation and lifecycle endpoint construction;
- CSV import validation;
- Direct-expense duplication guard;
- upload preview redaction;
- root marketplace validation with two plugins.

Evals must route representative prompts to all ten skills and encode write mode as `false`, `preview-first` or `approval-required`.

Tests must not contact Yandex services or require real credentials.

## 12. Definition of done

Phase 2 is complete when:

- `plugins/yandex-metrika/` version `1.0.0` exists and passes repository validation;
- all ten skills satisfy `docs/PLUGIN_STANDARD.md`;
- API/report/log/import helpers compile and pass offline tests;
- root marketplace exposes Direct and Metrika independently;
- CI detects and tests Metrika changes;
- service matrix marks Metrika stable;
- references are verified against current Yandex docs as of 2026-09-01;
- donor attribution/licensing is explicit;
- no real token, live counter ID or user analytics data is committed;
- Phase 2 changes are isolated in a stacked branch/PR on top of Phase 1 until PR #1 lands.
