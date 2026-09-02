# Reconciliation

Overlapping Direct and Metrika observations are compared, never added. Direct owns paid impressions, clicks and spend; Metrika owns visits, landing behavior and business outcome definitions. Reconciliation states are `ALIGNED`, `EXPLAINABLE_DIFFERENCE`, `REVIEW` and `INCOMPARABLE`. Differences may reflect context rather than tracking defects.

Evidence records preserve roles: `canonical`, `reconciliation_only`, or `enrichment`. Reconciliation returns the role-bearing records, the selected canonical record, status, and compatibility limitations. A reconciliation result does not expose a synthetic summed total for overlapping source views.

For monetary metrics, missing material currency/VAT/period context makes the comparison `INCOMPARABLE` with `MONEY_CONTEXT_UNKNOWN`. Incompatible KPI fingerprints remain explicit rather than being coerced into a numeric comparison.
