# Service Matrix

[Русский](SERVICE_MATRIX.md) · [**English**](SERVICE_MATRIX.en.md)

Status reflects what this repository actually ships, not upstream product availability. Production plugins use independent SemVer.

| Service plugin | Tier | Status | Version | Primary scope | Execution sources to evaluate |
|---|---:|---|---|---|---|
| Yandex Direct | 1 | **available** | 1.0.1 | campaigns, audit, reports, optimization, keywords, budget | bundled API helper; future MCP/app adapter |
| Yandex Metrika | 1 | **available** | 1.0.2 | reporting, conversions, ecommerce, attribution, goals, Logs API, imports; two-layer Direct expense duplication guard | bundled API helpers; optional MCP/app backend |
| Yandex Webmaster | 1 | **available** | 1.0.3 | indexing, diagnostics, queries, sitemaps, recrawl, links, feeds, exports; verified indexing archive `state` contract and hardened PRO export contract | bundled API helpers; optional MCP/app backend |
| Yandex Wordstat | 1 | **available** | 1.0.2 | demand, frequency, semantics, dynamics, regions, trends; 20-association cap | bundled Cloud Wordstat v2 helpers; optional MCP/app backend |
| Yandex Search | 1 | **available** | 1.0.2 | web SERP, batch, rankings, competitors, URL-overlap clustering; 250-result depth | bundled Search API v2 helpers; optional MCP/app backend |
| Yandex SEO | X | **available** | 1.0.1 | cross-service demand, visibility, performance, gaps, cannibalization, prioritization | pure-data orchestration over Wordstat + Search + Webmaster + Metrika |
| Yandex Marketing | X | **available** | 1.1.0 | paid performance, KPI reconciliation, evidence roles, demand/query intelligence, landing/budget opportunities | pure-data orchestration over Direct + Metrika + Wordstat with optional Search context |
| Yandex Tracker | 2 | backlog | — | issues, queues, permissions, worklogs, boards | official API first |
| Yandex 360 | 2 | backlog | — | mail, calendar, disk, organization | official APIs first |
| Yandex Maps | 2 | backlog | — | geocoding, places, routes | product/licensing boundary required |
| AppMetrica | 3 | backlog | — | mobile analytics, cohorts, crashes, deeplinks, push | official API first |
| YandexGPT | 3 | backlog | — | generation, embeddings, summarization | optional Yandex Cloud backend |
| SpeechKit | 3 | backlog | — | speech recognition and synthesis | Yandex Cloud |

## Cross-service workflows

- `yandex-seo`: **available 1.0.1** — Wordstat + Search + Webmaster + Metrika; no own transport, delegated previews only.
- `yandex-marketing`: **available 1.1.0** — Direct + Metrika + Wordstat, Search optional; `canonical` / `reconciliation_only` / `enrichment` roles are explicit.
- `yandex-ecommerce`, `yandex-mobile-growth`, `yandex-growth`: backlog ideas only.

Cross-service `.agents` entries use `authentication: ON_USE` as schema-compatible deferred-auth metadata; SEO/Marketing still own no Yandex credentials or HTTP transport.

## Repository controls

High-risk contracts map to concrete skills/helpers/tests in [`CONTRACT_MATRIX.json`](CONTRACT_MATRIX.json). The matrix is a traceability index, not semantic proof. On PR/push, the 90-day age gate blocks only a changed freshness-controlled reference; the weekly scheduled strict check evaluates the complete controlled set and synchronizes a freshness issue.

See [`ROADMAP.en.md`](ROADMAP.en.md) · [Русский](ROADMAP.md).
