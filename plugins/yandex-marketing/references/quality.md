# Quality and maturity

Propagate sampling, data lag, conversion maturity, period alignment and source-specific scope limitations. Maturity is `MATURE`, `IMMATURE` or `MATURITY_UNKNOWN`. There is no universal recent-days exclusion window. Search context limitations remain context limitations and do not alter paid economics.

Metrika artifacts without expected quality metadata carry `QUALITY_METADATA_MISSING`; sampled and lagged data preserve their producer metadata. Wordstat GetTop coverage with `associations_truncated=true` propagates `WORDSTAT_ASSOCIATIONS_CAPPED` because a 20-association result can represent the service cap rather than exhaustive semantic coverage.

Missing monetary currency/VAT/period context is `MONEY_CONTEXT_UNKNOWN` and blocks direct economic comparability. Limitations reduce confidence/coverage; they are never silently replaced with guessed values.
