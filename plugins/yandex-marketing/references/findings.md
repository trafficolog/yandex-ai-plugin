# Finding taxonomy

Findings are OBSERVED, DERIVED or HYPOTHESIS and include confidence, evidence, limitations and next step. No hidden numeric Marketing Score is defined.

The local executable taxonomy is defined by `IMPLEMENTED_FINDING_TYPES` and contains exactly the types produced by tested deterministic helpers:

- `MEASUREMENT_RISK`
- `KPI_CONTEXT_MISMATCH`
- `ATTRIBUTION_MISMATCH`
- `BUDGET_CONSTRAINT_CANDIDATE`
- `BUDGET_REALLOCATION_CANDIDATE`
- `DEMAND_EXPANSION_CANDIDATE`
- `SEARCH_TERM_EXPANSION_CANDIDATE`
- `SEARCH_TERM_EXCLUSION_REVIEW`
- `LANDING_MISMATCH_HYPOTHESIS`

Future or externally supplied classes belong to `DEFERRED_FINDING_TYPES` unless explicitly approved as an external delegated type. Deferred/unknown findings sort after implemented types and receive `UNKNOWN_OR_DEFERRED_TYPE` metadata.

`NEW_CAMPAIGN_CANDIDATE` is not an executable local or approved external route in 1.1.0. Do not infer campaign-creation delegation merely from demand expansion or another nearby finding class.
