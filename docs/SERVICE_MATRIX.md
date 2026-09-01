# Service Matrix

Status reflects what this repository actually ships, not upstream availability.

| Service plugin | Tier | Status | Version | Primary scope | Execution sources to evaluate |
|---|---:|---|---|---|---|
| Yandex Direct | 1 | **available** | 1.0.0 | campaigns, audit, reports, optimization, keywords, budget | bundled API helper; future MCP/app adapter |
| Yandex Metrika | 1 | **available** | 1.0.0 | reporting, conversions, ecommerce, attribution, goals, Logs API, imports | bundled API helpers; optional MCP/app backend |
| Yandex Webmaster | 1 | planned | — | indexing, diagnostics, queries, sitemaps, recrawl, links | official API; YaAll MCP reference |
| Yandex Wordstat | 1 | planned | — | demand, frequency, dynamics, regions, semantics | official API/Search infrastructure; donor implementations |
| Yandex Search | 1 | planned | — | SERP/search workflows | Yandex Cloud Search API / official MCP where applicable |
| Yandex Tracker | 2 | planned | — | issues, queues, permissions, worklogs, boards | official API; YaAll MCP reference |
| Yandex 360 | 2 | planned | — | mail, calendar, disk, organization | official APIs; YaAll MCP reference |
| Yandex Maps | 2 | planned | — | geocoding, places, routes | official APIs; YaAll MCP reference |
| AppMetrica | 3 | planned | — | mobile analytics, cohorts, crashes, deeplinks, push | official API; YaAll MCP reference |
| YandexGPT | 3 | planned | — | generation, embeddings, summarization | Yandex Cloud / YaAll MCP reference |
| SpeechKit | 3 | planned | — | speech recognition and synthesis | Yandex Cloud / YaAll MCP reference |

## Cross-service workflows

Cross-service workflows are planned only after their component plugins are stable:

- `yandex-marketing`: Direct + Metrika + Wordstat.
- `yandex-seo`: Wordstat + Search + Webmaster + Metrika.
- `yandex-ecommerce`: Direct + Metrika ecommerce + product/feed data.
- `yandex-mobile-growth`: AppMetrica + advertising/analytics sources where supported.
