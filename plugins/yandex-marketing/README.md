# Yandex Marketing

Cross-service paid-acquisition analysis over structured outputs from Yandex Direct, Metrika, Wordstat and optional Search. Version 1.0.0 is read/analyze/recommend/preview only and contains no Yandex credentials or HTTP clients.

Direct evidence is required. Metrika and Wordstat are primary enrichments; Search is optional intent/competitive context.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Direct/Metrika performance reconciliation | yes | no | via source plugins | no | yes |
| Wordstat demand coverage | yes | no | via source plugins | no | yes |
| Search-query intelligence | yes | preview only | via source plugins | no | yes |
| Landing/conversion hypotheses | yes | no | via source plugins | no | yes |
| Budget/query/goal delegated actions | yes | approval in owning plugin | via source plugins | no | yes |

## Safety

The plugin never mutates campaigns, budgets, bids, keywords, negatives, strategies, goals, counters, or other live settings. It emits delegated previews that identify the owning plugin and require that plugin's own approval flow before any consequential write.
