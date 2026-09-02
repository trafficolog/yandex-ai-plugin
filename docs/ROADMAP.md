# Roadmap

The first-release scope is frozen after Phase 6B. Phases 1–6B are the shipped `1.0.0` marketplace baseline. Everything below **Future release backlog** is intentionally outside the first release and has no committed delivery date.

## First release — completed

### Phase 1 — Marketplace foundation

- Moved the existing Yandex Direct implementation into `plugins/yandex-direct/`.
- Kept Direct at version `1.0.0` during the structural move.
- Established root marketplace metadata, plugin standard, service matrix, repository validator, and path-aware CI.
- Preserved Direct runtime behavior/API helper intent while introducing the marketplace boundary.

### Phase 2 — Yandex Metrika

Implemented as plugin `1.0.0` with ten specialized skills, quality-aware Reporting API support, safe Management/Logs/Data Import helpers, offline tests/evals and optional MCP/app execution fallback.

Key correctness rules include current attribution handling, sampling/data-lag disclosure, Logs lifecycle/date constraints, preview-before-write and a guard against duplicate Yandex Direct expense imports.

### Phase 3 — Yandex Webmaster

Implemented as plugin `1.0.0` with eleven specialized skills, mixed v4/v4.1 endpoint routing, query/indexing helpers, quota-aware recrawl, priority Sitemap recrawl, feeds, async archive/PRO exports and destructive-write guards.

### Phase 4 — Yandex Wordstat

Implemented as plugin `1.0.0` with nine workflow skills, Cloud Wordstat v2 helpers, provenance-aware semantics, operator-safe dynamics, regional affinity, trend classification, and quota/cost planning.

### Phase 5 — Yandex Search

Implemented as plugin `1.0.0` with ten workflow skills, Search API v2 sync/deferred helpers, XML SERP snapshots, cost-aware batch planning, ranking/competitor analytics and explicit-threshold URL-overlap clustering with bridge-risk diagnostics.

### Phase 6A — Yandex SEO

Implemented as plugin `1.0.0` with a versioned SEO Evidence Bundle, partial/full capability modes, provenance-preserving joins, quality/alignment propagation, content-gap/cannibalization/CTR/conversion/technical findings, transparent prioritization and preview-only delegated actions.

The plugin contains no Yandex API clients and performs no live writes.

### Phase 6B — Yandex Marketing

Implemented as plugin `1.0.0` with Direct-required paid-acquisition orchestration, a versioned Marketing Evidence Bundle, KPI/attribution/maturity reconciliation, demand and query intelligence, landing/budget findings, transparent prioritization and preview-only delegated actions.

The plugin contains no Yandex API clients and performs no live writes.

---

# Future release backlog

The backlog is a direction-of-development list, not a release promise. Items can be reprioritized, split into separate plugins/phases, or removed after design review and API research.

## Operations / collaboration

### Yandex Tracker

Potential scope:

- issues and queues;
- comments/attachments;
- permissions;
- worklogs;
- boards and project workflows;
- agent-safe issue mutation contracts.

Likely execution sources: official API first, with donor MCP implementations used only as capability/workflow references.

### Yandex 360

Potentially separate plugins rather than one monolith depending on API/security boundaries:

- Mail;
- Calendar;
- Disk;
- organization/directory administration where appropriate.

High-priority design concern: separation between personal productivity actions and organization-level administrative mutations.

## Maps / local

### Yandex Maps

Potential scope:

- geocoding/reverse geocoding;
- places/business search;
- routes;
- distance/time context;
- local/geo enrichment for other plugins.

A future design should explicitly separate search/geocoding/navigation products and their licensing/usage constraints.

## Mobile

### AppMetrica

Potential scope:

- mobile analytics;
- cohorts/retention;
- crashes;
- deeplinks;
- push analytics;
- acquisition/source analysis.

Possible future cross-service workflow: `yandex-mobile-growth` using AppMetrica plus advertising/analytics sources where the semantics are compatible.

## AI / speech

### YandexGPT

Potential scope:

- text generation;
- structured generation;
- embeddings;
- summarization/classification;
- optional model backend for workflows that explicitly need generation rather than deterministic analysis.

The marketplace should not make YandexGPT a mandatory dependency for service plugins whose current behavior is deterministic.

### SpeechKit

Potential scope:

- speech recognition;
- speech synthesis;
- transcription workflows;
- voice-oriented agent integrations.

## Possible cross-service extensions

These are exploratory backlog items, not approved architecture:

- `yandex-ecommerce` — Direct + Metrika ecommerce + product/feed data;
- `yandex-mobile-growth` — AppMetrica + acquisition/analytics sources;
- `yandex-growth` — higher-level coordination between SEO and Marketing only if a future design can preserve source ownership and safety boundaries;
- persistent evidence/history storage for longitudinal SEO/marketing analysis;
- scheduled monitoring/alerts as a separate execution concern rather than silently embedding background behavior into current plugins;
- additional execution adapters/MCP integrations while preserving existing skill semantics.

## Backlog entry requirements

Before any backlog item becomes an implementation phase it should go through the same process used for the first release:

1. current official API/product research;
2. donor/capability research where useful;
3. explicit plugin boundary decision;
4. written architecture/design approval;
5. implementation plan;
6. TDD/offline evals;
7. path-aware CI;
8. independent release review.

