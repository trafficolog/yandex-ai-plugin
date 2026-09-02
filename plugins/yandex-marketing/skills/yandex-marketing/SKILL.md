---
name: yandex-marketing
description: Use when the user asks for cross-service Yandex paid-acquisition analysis, campaign performance context, demand coverage, or marketing prioritization.
---
# Yandex Marketing router

Direct is required for this plugin because paid-acquisition identity, spend, impressions, clicks, campaigns, criteria, and actual paid search queries originate there. If Direct evidence is unavailable, return/route `ROUTING_REQUIRED` to the relevant source workflow instead of pretending to perform paid-acquisition analysis.

Detect coverage first: Direct-only, Direct+Metrika performance, Direct+Wordstat demand/query intelligence, full acquisition, or optional competitive context. Search is optional and may enrich intent or competitor context; it never determines paid efficiency.

Preserve source provenance, KPI context, maturity, limitations and evidence role (`canonical`, `reconciliation_only`, `enrichment`). Overlapping source views are reconciled, not summed. Missing monetary context remains explicitly incomparable. Capped Wordstat association coverage propagates as a limitation.

Use read → reconcile → diagnose → recommend → preview. Local findings come from the implemented deterministic taxonomy; deferred/unknown finding classes are not silently upgraded to executable capabilities. Consequential changes are delegated to the owning plugin and require that plugin's approval flow.
