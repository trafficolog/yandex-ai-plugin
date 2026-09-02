---
name: yandex-marketing-audit
description: Use when auditing Yandex paid acquisition across Direct, Metrika, Wordstat, and optional Search evidence.
---
# Paid-acquisition audit

Start with source coverage and the business KPI fingerprint. Audit measurement and goal consistency before interpreting campaign efficiency. Then review campaign/criterion/query performance, Direct-versus-Metrika reconciliation, demand coverage, landing evidence, attribution context, maturity, and budget constraints.

Classify evidence as OBSERVED, DERIVED, or HYPOTHESIS and preserve its stable role: `canonical`, `reconciliation_only`, or `enrichment`. Canonical and reconciliation-only observations are compared, never summed. Generic `metric: demand` is invalid; use source-specific evidence such as `wordstat_count`.

Report source limitations and stop cross-source efficiency comparisons when KPI, period, currency, VAT, or attribution context is incomparable. Monetary evidence missing material money context must retain `MONEY_CONTEXT_UNKNOWN`. Propagate capped Wordstat associations as `WORDSTAT_ASSOCIATIONS_CAPPED`.

Finish with findings from the implemented local taxonomy and preview-only delegated actions. Unknown/deferred external finding classes are limitations/context, not silently executable local capabilities.
