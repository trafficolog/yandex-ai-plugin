# Матрица сервисов

[**Русский**](SERVICE_MATRIX.md) · [English](SERVICE_MATRIX.en.md)

Статус отражает то, что реально поставляется этим репозиторием, а не всю доступность продуктов Яндекса. Production plugins используют independent SemVer.

| Service plugin | Tier | Status | Version | Primary scope | Execution sources to evaluate |
|---|---:|---|---|---|---|
| Yandex Direct | 1 | **available** | 1.0.1 | campaigns, audit, reports, optimization, keywords, budget | bundled API helper; future MCP/app adapter |
| Yandex Metrika | 1 | **available** | 1.0.3 | reporting, conversions, ecommerce, attribution, goals, Logs API, imports; provenance-aware Direct expense duplication guard | bundled API helpers; optional MCP/app backend |
| Yandex Webmaster | 1 | **available** | 1.0.3 | indexing, diagnostics, queries, sitemaps, recrawl, links, feeds, exports; verified indexing archive `state` contract and hardened PRO export contract | bundled API helpers; optional MCP/app backend |
| Yandex Wordstat | 1 | **available** | 1.1.1 | demand, frequency, semantics, dynamics, regions, trends; candidate topic maps; 20-association cap; unambiguous seed/topic relation provenance | bundled Cloud Wordstat v2 helpers; optional MCP/app backend |
| Yandex Search | 1 | **available** | 1.0.2 | web SERP, batch, rankings, competitors, URL-overlap clustering; 250-result depth | bundled Search API v2 helpers; optional MCP/app backend |
| Yandex SEO | X | **available** | 1.1.1 | cross-service demand, visibility, performance, gaps, cannibalization, topical architecture, internal-link planning, prioritization; hardened structural/link artifact validation | pure-data orchestration over Wordstat + Search + Webmaster + Metrika |
| Yandex Marketing | X | **available** | 1.1.0 | paid performance, KPI reconciliation, evidence roles, demand/query intelligence, landing/budget opportunities | pure-data orchestration over Direct + Metrika + Wordstat with optional Search context |
| Yandex Tracker | 2 | backlog | — | issues, queues, permissions, worklogs, boards | official API first |
| Yandex 360 | 2 | backlog | — | mail, calendar, disk, organization | official APIs first |
| Yandex Maps | 2 | backlog | — | geocoding, places, routes | product/licensing boundary required |
| AppMetrica | 3 | backlog | — | mobile analytics, cohorts, crashes, deeplinks, push | official API first |
| YandexGPT | 3 | backlog | — | generation, embeddings, summarization | optional Yandex Cloud backend |
| SpeechKit | 3 | backlog | — | speech recognition and synthesis | Yandex Cloud |

## Cross-service workflows

- `yandex-seo`: **available 1.1.1** — Wordstat + Search + Webmaster + Metrika; Topical Architecture и Internal Linking; no own transport, delegated previews only.
- `yandex-marketing`: **available 1.1.0** — Direct + Metrika + Wordstat, Search optional; `canonical` / `reconciliation_only` / `enrichment` roles explicit.
- `yandex-ecommerce`, `yandex-mobile-growth`, `yandex-growth`: backlog ideas only.

Cross-service `.agents` entries use `authentication: ON_USE` as schema-compatible deferred-auth metadata; SEO/Marketing still own no Yandex credentials or HTTP transport.

## Phase 7 — Topical Architecture & Semantic Cocoons

Phase 7 разделяет semantic-cocoon workflow по существующим service boundaries:

```text
Wordstat: yandex-wordstat-topic-map
    ↓  wordstat-topic-map/v1 (candidate-only)
Search: yandex-search-clustering
    ↓  реальный SERP-overlap / Jaccard / bridge_risk
SEO: yandex-seo-topical-architecture
    ↓  seo-topical-architecture/v1
SEO: yandex-seo-internal-linking
    ↓  preview-only link plan / audit
```

Ownership contract:

- **Wordstat** собирает demand evidence и candidate topics; Wordstat associations/co-occurrence не доказывают финальные границы страниц. Patch `1.1.1` дополнительно запрещает duplicate seed identifiers и candidate self-relations.
- **Search** остаётся единственным владельцем SERP-overlap clustering. Phase 7 не создаёт альтернативный fuzzy-text clustering в Wordstat или SEO и не меняет Search `1.0.2`.
- **SEO Topical Architecture** принимает Search-owned clusters и optional Webmaster/Metrika/site-inventory evidence, затем валидирует page decisions, `structural_tree` и `semantic_graph`. Patch `1.1.1` whitelist-нормализует structural nodes и не допускает execution-state leakage.
- **Internal Linking** строит и аудирует только preview-артефакты; CMS writes отсутствуют. Candidate-link `evidence` list-typed.
- `OBSERVED`, `DERIVED`, `HYPOTHESIS`, `METHODOLOGY` не смешиваются. Methodology из semantic-cocoon/TGA/QBST материалов не становится ranking fact без независимого authoritative evidence.

Поддерживаются `GREENFIELD` и `EXISTING_SITE` режимы. При отсутствии Search evidence архитектура обязана сообщить `SERP_VALIDATION_MISSING`, а page boundaries остаются гипотезами.

## Repository controls

High-risk contracts привязаны к реальным skills/helpers/tests в [`CONTRACT_MATRIX.json`](CONTRACT_MATRIX.json). Матрица является traceability index, а не semantic proof. В PR/push 90-day age блокирует изменённый controlled reference; weekly scheduled strict check проверяет весь контролируемый набор и синхронизирует freshness issue.

Shared runtime promotion требует не только повторения и стабильного interface, но и безопасного installability/distribution contract для независимо устанавливаемых plugins; hidden repo-root dependencies запрещены.

См. [`ROADMAP.md`](ROADMAP.md) · [English](ROADMAP.en.md).
