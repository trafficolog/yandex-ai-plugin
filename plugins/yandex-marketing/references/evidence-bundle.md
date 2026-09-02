# Marketing Evidence Bundle

Version 1 stores context, source coverage, campaigns, criteria, actual paid queries, landings, goals, demand evidence, findings and limitations. Every metric retains source provenance and the relevant KPI/period/money context. Direct is required for paid-acquisition analysis. Search is optional enrichment.

Every evidence record uses one stable role:

- `canonical` — source-of-truth record for that metric under repository policy;
- `reconciliation_only` — overlapping evidence used to compare against canonical data, never to be added to it;
- `enrichment` — contextual evidence that does not replace the canonical metric.

A valid explicit role is preserved; otherwise the role is derived deterministically from metric/source ownership. Invalid roles fail. Generic `metric: demand` is rejected in favor of source-specific evidence such as `wordstat_count`.

Monetary evidence requires material currency, VAT-basis and period context for comparability. Missing context remains explicit as `MONEY_CONTEXT_UNKNOWN` rather than being inferred.
