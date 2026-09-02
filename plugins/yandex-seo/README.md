# Yandex SEO

Read-only cross-service SEO orchestration version `1.0.1` over structured outputs from Yandex Wordstat, Search, Webmaster and Metrika. The plugin contains no Yandex API client and executes no live writes.

The Evidence Bundle requires explicit `site`, `analysis_period` and `search_region_id`. Period, geography, Search configuration and device context are aligned independently; Metrika visitor geography is never treated as a Search ranking region without explicit evidence.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Cross-service SEO audit / evidence bundle | yes | no | optional | pure-data | yes |
| Demand + visibility + SERP enrichment | yes | no | optional | pure-data | yes |
| Content gaps / cannibalization / CTR / conversion analysis | yes | no | optional | pure-data | yes |
| Period / geo / search / device alignment | yes | no | optional | pure-data | yes |
| Technical finding action preview | yes | delegated preview only | optional | no transport | yes |
| Transparent finding prioritization | yes | delegated preview only | optional | pure-data | yes |
