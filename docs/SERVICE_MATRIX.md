# Service Matrix

Status reflects what this repository actually ships, not upstream availability.

The first-release feature set is frozen at the seven `available` plugins below. Plugins use independent SemVer, so the current contract-hardening release is intentionally mixed-version. `backlog` means future-release research/design only; it is not a committed next-release promise.

| Service plugin | Tier | Status | Version | Primary scope | Execution sources to evaluate |
|---|---:|---|---|---|---|
| Yandex Direct | 1 | **available** | 1.0.1 | campaigns, audit, reports, optimization, keywords, budget | bundled API helper; future MCP/app adapter |
| Yandex Metrika | 1 | **available** | 1.0.1 | reporting, conversions, ecommerce, attribution, goals, Logs API, imports | bundled API helpers; optional MCP/app backend |
| Yandex Webmaster | 1 | **available** | 1.0.2 | indexing, diagnostics, queries, sitemaps, recrawl, links, feeds, exports; hardened PRO export lifecycle/quota contract | bundled API helpers; optional MCP/app backend |
| Yandex Wordstat | 1 | **available** | 1.0.2 | demand, frequency, semantics, dynamics, regions, trends; explicit 20-association coverage cap | bundled Cloud Wordstat v2 helpers; optional MCP/app backend |
| Yandex Search | 1 | **available** | 1.0.2 | web SERP, batch, rankings, competitors, URL-overlap clustering; strict 250-result depth contract | bundled Search API v2 helpers; optional MCP/app backend |
| Yandex SEO | X | **available** | 1.0.1 | cross-service demand, visibility, performance, gaps, cannibalization, prioritization | pure-data orchestration over Wordstat + Search + Webmaster + Metrika |
| Yandex Marketing | X | **available** | 1.1.0 | cross-service paid performance, KPI reconciliation, stable evidence roles, executable finding taxonomy, demand/query intelligence, landing/budget opportunities | pure-data orchestration over Direct + Metrika + Wordstat with optional Search context |
| Yandex Tracker | 2 | backlog | — | issues, queues, permissions, worklogs, boards | official API first; donor MCP references only after fresh review |
| Yandex 360 | 2 | backlog | — | mail, calendar, disk, organization | official APIs first; donor MCP references only after fresh review |
| Yandex Maps | 2 | backlog | — | geocoding, places, routes | official APIs first; product/licensing boundary must be designed |
| AppMetrica | 3 | backlog | — | mobile analytics, cohorts, crashes, deeplinks, push | official API first; cross-service semantics to be designed |
| YandexGPT | 3 | backlog | — | generation, embeddings, summarization | Yandex Cloud; should remain optional for deterministic service workflows |
| SpeechKit | 3 | backlog | — | speech recognition and synthesis | Yandex Cloud; voice workflow design required |

## Cross-service workflows

Cross-service workflows compose stable service plugins without duplicating their API clients:

- `yandex-seo`: **available 1.0.1** — Wordstat + Search + Webmaster + Metrika.
- `yandex-marketing`: **available 1.1.0** — Direct + Metrika + Wordstat, with Search as optional context; canonical/reconciliation/enrichment roles and implemented/deferred finding taxonomy are explicit.
- `yandex-ecommerce`: backlog idea — Direct + Metrika ecommerce + product/feed data.
- `yandex-mobile-growth`: backlog idea — AppMetrica + advertising/analytics sources where supported.
- `yandex-growth`: backlog idea only; any future design must preserve SEO/Marketing source ownership and safety boundaries.

## Repository controls

High-risk shipped contracts are linked to concrete skills, helpers and regression tests in [`CONTRACT_MATRIX.json`](CONTRACT_MATRIX.json). Freshness-controlled API references use a deterministic 90-day verification gate; this CI check does not make network requests.

See [`ROADMAP.md`](ROADMAP.md) for the future-release backlog and entry requirements.
