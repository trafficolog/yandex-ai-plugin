# Yandex Marketing

Cross-service paid-acquisition analysis over structured outputs from Yandex Direct, Metrika, Wordstat and optional Search. Version `1.1.0` is read/analyze/recommend/preview only and contains no Yandex credentials or HTTP clients.

Direct evidence is required for full acquisition analysis; when it is absent the bundle/capability layer returns `routing_required` / `ROUTING_REQUIRED` rather than guessing a substitute source. Metrika and Wordstat are primary enrichments; Search is optional intent/competitive context.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Direct/Metrika performance reconciliation | yes | no | via source plugins | no | yes |
| Wordstat demand coverage | yes | no | via source plugins | no | yes |
| Search-query intelligence | yes | delegated preview only | via source plugins | no | yes |
| Landing/conversion hypotheses | yes | no | via source plugins | no | yes |
| Budget/query/goal delegated actions | yes | approval in owning plugin | via source plugins | no | yes |

## Evidence contract

Evidence uses stable roles:

- `canonical` — source-of-truth record for the metric under repository policy;
- `reconciliation_only` — overlapping comparison evidence that must not be summed with canonical values;
- `enrichment` — contextual evidence that does not replace the canonical metric.

Roles may be supplied explicitly only when valid or derived deterministically from metric/source ownership. Generic `metric: demand` remains forbidden. Monetary evidence missing currency, VAT basis or period context carries `MONEY_CONTEXT_UNKNOWN` and is not treated as comparable economics.

Capped Wordstat association coverage propagates `WORDSTAT_ASSOCIATIONS_CAPPED`.

## Finding taxonomy

The local executable taxonomy contains only finding types actually produced by deterministic helpers. `IMPLEMENTED_FINDING_TYPES` is authoritative for local production; future/unsupported classes live in `DEFERRED_FINDING_TYPES`. Unknown/deferred external findings sort after implemented findings and carry `UNKNOWN_OR_DEFERRED_TYPE`. Dead `NEW_CAMPAIGN_CANDIDATE` delegation is not executable.

## Safety

The plugin never mutates campaigns, budgets, bids, keywords, negatives, strategies, goals, counters, or other live settings. It emits delegated previews that identify the owning plugin and require that plugin's own approval flow before any consequential write.
