---
name: yandex-marketing-performance
description: Use when comparing paid campaign, criterion, query, spend, conversion, revenue, CPA, ROAS, or funnel performance across Direct and Metrika evidence.
---
# Paid performance

Before comparing economics, state the KPI fingerprint: business objective, goal IDs, attribution context, metric basis, currency, VAT basis, and period. Preserve conversion maturity and data lag.

Direct is canonical for paid impressions, clicks and spend; Metrika is canonical for visits, landing behavior and business outcome definitions. Evidence roles are `canonical`, `reconciliation_only`, and `enrichment`. Reconciliation is comparison, not summation, and returns the selected canonical record together with role-bearing source records and compatibility limitations.

Calculate CPC, CTR, CR, CPA, ROAS, DRR or revenue-per-click only when their inputs exist and are materially compatible. If monetary evidence lacks currency, VAT basis, or period context, mark it `MONEY_CONTEXT_UNKNOWN` / `INCOMPARABLE` rather than deriving economics. If revenue is absent, do not invent ROAS or DRR. If maturity is IMMATURE or unknown, qualify the conclusion.
