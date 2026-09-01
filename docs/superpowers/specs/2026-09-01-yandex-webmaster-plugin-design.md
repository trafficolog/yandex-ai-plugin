# Yandex Webmaster Plugin Design

**Date:** 2026-09-01
**Phase:** 3
**Plugin:** `yandex-webmaster`
**Target version:** `1.0.0`
**Branch:** `phase-3-yandex-webmaster`
**Base:** `phase-2-yandex-metrika`

## Goal

Ship Yandex Webmaster as the third independent plugin in the Yandex AI marketplace. The plugin must cover practical SEO workflows while keeping API execution separate from reasoning, preserving the repository-wide safety contract and handling the mixed `/v4/` and `/v4.1/` API surface correctly.

## Architecture

The plugin is workflow-first rather than a 1:1 mirror of every REST endpoint. Skills encode SEO reasoning, data interpretation, safety and task routing. Dependency-free Python helpers provide local execution when a connected MCP/app is unavailable. A connected MCP/app is optional and never a correctness dependency.

Execution fallback order:

1. connected Yandex Webmaster MCP/app when available and suitable;
2. bundled Python helpers;
3. user-provided exports/files for read-only analysis.

Official Yandex Webmaster documentation is the source of truth. `mkultraaaa/claude-yandex-skills` is a workflow donor and `theYahia/YaAll` is a capability/MCP reference only.

## Plugin layout

```text
plugins/yandex-webmaster/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── .env.example
├── README.md
├── CHANGELOG.md
├── THIRD_PARTY_NOTICES.md
├── evals/
│   └── scenarios.json
├── references/
│   ├── api-2026.md
│   ├── audit-framework.md
│   ├── endpoint-map.md
│   ├── indexing.md
│   ├── queries.md
│   ├── recrawl.md
│   ├── sitemaps.md
│   ├── feeds.md
│   ├── exports.md
│   ├── safety.md
│   └── sources.md
├── scripts/
│   ├── __init__.py
│   ├── _http.py
│   ├── yw_api.py
│   ├── yw_queries.py
│   ├── yw_indexing.py
│   ├── yw_recrawl.py
│   ├── yw_sitemaps.py
│   ├── yw_feeds.py
│   └── yw_export.py
├── skills/
│   ├── yandex-webmaster/
│   ├── yandex-webmaster-audit/
│   ├── yandex-webmaster-site-management/
│   ├── yandex-webmaster-search-queries/
│   ├── yandex-webmaster-indexing/
│   ├── yandex-webmaster-recrawl/
│   ├── yandex-webmaster-sitemaps/
│   ├── yandex-webmaster-links/
│   ├── yandex-webmaster-feeds/
│   ├── yandex-webmaster-exports/
│   └── yandex-webmaster-api/
└── tests/
```

## Skill boundaries

### `yandex-webmaster`

Router for broad Webmaster requests. It identifies whether the user needs audit, site management, query analytics, indexing, recrawl, sitemaps, links, feeds, exports or raw API work.

### `yandex-webmaster-audit`

Evidence-first SEO health review combining verification, diagnostics, SQI, indexing history, pages in search, search events, sitemap state, link state and search-query trends. Findings use `PASS`, `ISSUE`, `REVIEW`, `N/A`; no universal SEO threshold is invented when Yandex does not provide one.

### `yandex-webmaster-site-management`

Hosts, host metadata, verification state and verification initiation, adding hosts and deleting hosts. Host deletion is destructive and requires explicit confirmation tied to the exact host.

### `yandex-webmaster-search-queries`

Popular queries, query history and Query Analytics. The skill must distinguish limited popular-query views from richer Query Analytics exports, preserve requested periods/regions/devices, and never claim complete query coverage when the endpoint is a top-N view.

### `yandex-webmaster-indexing`

Indexing/crawl history, pages in search, search events, important URLs and full-page archive workflows. It separates observed crawl state from search inclusion state and reports exclusion reasons without inventing causal certainty.

### `yandex-webmaster-recrawl`

Ordinary URL recrawl. Workflow is quota-aware: read quota → inspect queue/state → validate URL host ownership → preview → explicit approval → submit → verify. `URL_ALREADY_ADDED` is treated as an idempotent state rather than a fatal failure.

### `yandex-webmaster-sitemaps`

Discovered and user-added sitemaps, add/delete operations and priority Sitemap recrawl. It distinguishes sources such as robots, Webmaster-added and sitemap indexes. Priority recrawl is routed to `/v4.1/` and is quota-aware.

### `yandex-webmaster-links`

Internal/external links and broken-link analysis. This is read-only in 1.0.0.

### `yandex-webmaster-feeds`

Feed listing, validation, upload/start/status and delete workflows. HTTPS host requirements and asynchronous status are explicit. Delete remains destructive.

### `yandex-webmaster-exports`

Asynchronous archive exports and Webmaster PRO/search exports. The skill checks entitlement/quota/available dates before starting quota-consuming exports, polls status and saves downloads to files rather than dumping large results into context.

### `yandex-webmaster-api`

Low-level endpoint access and debugging. It knows the endpoint version map, OAuth requirements, pagination/query parameters and preview-before-write behavior.

## API version strategy

Do not define one global API version for every resource.

Use an endpoint-aware resolver:

```text
standard/current resources -> /v4/
4.1-only resources         -> /v4.1/
```

Initial 4.1-specific routing includes priority Sitemap recrawl. Other endpoints stay on the version documented for that resource until official documentation says otherwise.

The helper must reject arbitrary API-version strings supplied through endpoint names. Version resolution is controlled by a documented endpoint map.

## Authentication

Use Yandex OAuth via:

```text
Authorization: OAuth <token>
```

Environment variable:

```text
YANDEX_WEBMASTER_TOKEN
```

Relevant current permissions documented by Yandex include `webmaster:hostinfo` and `webmaster:verify`. The plugin does not hard-code a claim that every operation needs exactly the same scope; it reports permission errors and points to current docs.

Tokens are never committed, printed or included in previews. Previews display `OAuth ***`.

`user_id` should normally be resolved through the API rather than requested from the human if the connected execution backend can obtain it.

## Helper interfaces

### `_http.py`

Shared `urllib` request construction, OAuth headers, JSON decoding, redaction and HTTP error normalization.

### `yw_api.py`

Generic Management API helper for hosts, verification, diagnostics and lower-level operations. Consequential methods preview by default and require `--execute`.

### `yw_queries.py`

Builds popular/history/query-analytics requests and normalizes pagination/top-N metadata so outputs do not imply completeness incorrectly.

### `yw_indexing.py`

Builds indexing history, in-search/search-event/important-page requests and archive task status/download helpers.

### `yw_recrawl.py`

Quota/queue inspection and ordinary recrawl submission. Validates that submitted URLs belong to the selected host. Maps `URL_ALREADY_ADDED` to a non-fatal already-queued result.

### `yw_sitemaps.py`

Lists discovered/user-added sitemaps, previews add/delete and resolves priority-recrawl to `/v4.1/`. Priority-recrawl availability and nearest allowed day are represented in output when returned by the API.

### `yw_feeds.py`

Feed list/start/status/delete helpers. Write/delete operations preview by default.

### `yw_export.py`

Async task start/status/download helpers for archive and supported PRO/search exports. Large files are written to disk.

## Safety model

Repository-wide contract:

```text
read → analyze → preview → explicit approval → write → verify
```

Risk classes:

- read: diagnostics, SQI, indexing, queries, links, sitemap/feed state;
- low-risk write: verification start, ordinary recrawl;
- consequential: add host, add sitemap, add feed, initiate quota-consuming export;
- destructive: delete host, sitemap or feed;
- quota-consuming: ordinary recrawl, priority Sitemap recrawl, PRO/archive exports where applicable.

Recommendation is not authorization. “Fix indexing” may generate a recrawl proposal but must not submit it without explicit approval.

Delete approval must name the exact target and operation. Bulk delete is not part of 1.0.0 helper convenience commands.

## Data-quality rules

- Preserve Yandex diagnostic severity/state rather than replacing them with arbitrary SEO scores.
- Distinguish crawl/indexing/search-inclusion concepts.
- Do not treat a popular-query top-N endpoint as complete query coverage.
- Report requested period, region/device filters and pagination context for query analysis.
- Do not infer that recrawl guarantees indexing or ranking.
- Do not infer that adding a sitemap guarantees crawl/index inclusion.
- Treat queue/quota state as current operational state, not as long-lived facts.

## Audit framework

Recommended sequence:

1. resolve user and host;
2. verification state;
3. diagnostics by severity/state;
4. SQI/history when useful;
5. crawl/indexing history;
6. pages in search and search events;
7. sitemap coverage/state;
8. internal/external/broken links where available;
9. popular queries/query analytics trends;
10. produce prioritized findings with evidence and next action.

Audit output contains evidence, impact, confidence, reversibility and whether a proposed next action consumes quota or mutates state.

## Evals

Offline eval fixtures cover at minimum:

- routing a general Webmaster audit;
- explaining a query drop without inventing full coverage;
- proposing recrawl but stopping at preview;
- handling an already-queued URL;
- selecting `/v4.1/` for priority Sitemap recrawl;
- refusing destructive host deletion without exact approval;
- async archive export lifecycle;
- feed delete safety;
- fallback to export/file when live execution is unavailable.

## Tests

All tests are offline and use fake transports/fixtures.

Required coverage:

- manifest/layout discovery;
- token redaction and generic request construction;
- endpoint version resolver (`v4` vs `v4.1`);
- query request construction and top-N metadata;
- recrawl host validation, quota and already-added handling;
- sitemap add/delete preview and priority-recrawl routing;
- feed write/delete preview;
- async export status/download behavior;
- repository marketplace/CI integration.

## Monorepo integration

Add `yandex-webmaster` to both marketplace manifests, root README, service matrix and roadmap. Extend path-aware CI with a Webmaster output/job. Shared marketplace/validator/test changes may trigger all affected plugins; Webmaster-only changes trigger Webmaster tests only.

Phase 3 must not functionally modify Direct or Metrika.

## Stacking

```text
main
  └─ Phase 1 PR #1
      └─ Phase 2 PR #2
          └─ Phase 3 PR #3
```

PR #3 targets `phase-2-yandex-metrika` until earlier PRs land. It can then be retargeted to `main` after the preceding stack has merged.

## Definition of Done

Phase 3 is complete when:

- `yandex-webmaster` 1.0.0 is independently discoverable/installable;
- all 11 skills satisfy `PLUGIN_STANDARD.md`;
- 8 dependency-free helpers exist and compile;
- mixed `/v4/` and `/v4.1/` routing is tested;
- OAuth previews redact tokens;
- recrawl/sitemap/feed/export lifecycle and safety tests pass;
- offline eval scenarios pass repository validation;
- root validator and all Direct/Metrika/Webmaster regression suites pass;
- remote diff against Phase 2 contains no changes under Direct or Metrika plugin directories;
- PR #3 is opened against `phase-2-yandex-metrika`.
