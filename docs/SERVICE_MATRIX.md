# Матрица сервисов

[**Русский**](SERVICE_MATRIX.md) · [English](SERVICE_MATRIX.en.md)

Статус отражает то, что реально поставляется этим репозиторием, а не всю доступность продуктов Яндекса. Production plugins используют independent SemVer.

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
- `yandex-marketing`: **available 1.1.0** — Direct + Metrika + Wordstat, Search optional; `canonical` / `reconciliation_only` / `enrichment` roles explicit.
- `yandex-ecommerce`, `yandex-mobile-growth`, `yandex-growth`: backlog ideas only.

Cross-service `.agents` entries use `authentication: ON_USE` as schema-compatible deferred-auth metadata; SEO/Marketing still own no Yandex credentials or HTTP transport.

## Repository controls

High-risk contracts привязаны к реальным skills/helpers/tests в [`CONTRACT_MATRIX.json`](CONTRACT_MATRIX.json). Матрица является traceability index, а не semantic proof. В PR/push 90-day age блокирует изменённый controlled reference; weekly scheduled strict check проверяет весь контролируемый набор и синхронизирует freshness issue.

См. [`ROADMAP.md`](ROADMAP.md) · [English](ROADMAP.en.md).
