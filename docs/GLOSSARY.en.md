# Glossary

[Русский](GLOSSARY.md) · [**English**](GLOSSARY.en.md)

This glossary explains recurring terms in plain language without renaming exact machine tokens used by contracts, artifacts, and tests.

## Service plugin

The plugin that owns one Yandex service. It is responsible for API transport, credentials, service-specific helpers, and volatile API facts. Examples include Direct, Metrika, Webmaster, Wordstat, and Search.

## Cross-service plugin

An orchestrator that combines evidence from several service plugins. `yandex-seo` and `yandex-marketing` own no Yandex credentials or HTTP transport of their own.

## `preview_id`

The identifier of an exact preview for a consequential write. It binds approval to a specific operation and its approval-bound parameters. A changed payload or identity requires a new preview.

## Delegated preview

An action preview a cross-service plugin can prepare for the owning service plugin. It is not a live mutation and does not authorize the cross-service plugin to perform another service's API write.

## Fail-closed

Behavior that stops a risky action when the required condition cannot be proven. For example, if approval cannot be shown to match the exact preview, the write is blocked instead of guessing user intent.

## Provenance

Information about where data came from: service, endpoint/artifact, query, URL, period, attribution context, calculation method, and known limitations. Provenance helps prevent incompatible metrics from being mixed and derived values from being presented as observations.

## `OBSERVED`

A claim obtained directly from a documented evidence source such as an API, export, or report.

## `DERIVED`

A claim calculated from `OBSERVED` data by an explicit, reviewable rule. It is not the same thing as a direct observation.

## `HYPOTHESIS`

An inference for which current evidence does not support a stronger claim. A hypothesis stays explicitly labeled until further validation is available.

## `METHODOLOGY`

A methodological principle or framework. It must not be presented as a verified Yandex/Google ranking mechanism or quantitative API observation merely because a workflow uses it.

## `SERP_VALIDATION_MISSING`

An exact limitation token indicating that required Search/SERP evidence is absent. For example, Wordstat demand alone must not turn a candidate page boundary into a confirmed SERP cluster.

## `canonical`

In Marketing reconciliation, the evidence source selected as primary for a calculation after KPI, money-context, and provenance compatibility checks.

## `reconciliation_only`

Evidence used to cross-check `canonical` but not summed with it. This reduces the risk of double-counting overlapping data.

## `enrichment`

Evidence that adds context to the primary calculation without replacing the `canonical` metric or becoming a hidden contribution to the total.
