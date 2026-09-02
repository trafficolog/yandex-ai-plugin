---
name: yandex-marketing
description: Use when the user asks for cross-service Yandex paid-acquisition analysis, campaign performance context, demand coverage, or marketing prioritization.
---
# Yandex Marketing router

Direct is required for this plugin because paid-acquisition identity, spend, impressions, clicks, campaigns, criteria, and actual paid search queries originate there. If Direct evidence is unavailable, route the request to Metrika, Wordstat, Search, or another plugin instead of pretending to perform paid-acquisition analysis.

Detect coverage first: Direct-only, Direct+Metrika performance, Direct+Wordstat demand/query intelligence, full acquisition, or optional competitive context. Search is optional and may enrich intent or competitor context; it never determines paid efficiency.

Preserve source provenance, KPI context, maturity and limitations. Use read → reconcile → diagnose → recommend → preview. Consequential changes are delegated to the owning plugin.
