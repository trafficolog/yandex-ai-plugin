# Changelog

## 1.1.0 — 2026-09-02

- Added stable evidence roles: `canonical`, `reconciliation_only`, and `enrichment`, with deterministic role derivation and validation.
- Hardened monetary evidence reconciliation so missing currency/VAT/period context remains explicitly incomparable instead of producing unsupported combined metrics.
- Replaced the legacy 18-class priority taxonomy with the nine finding types actually produced by deterministic helpers; deferred/unknown external types are explicitly marked and sort after implemented types.
- Removed dead `NEW_CAMPAIGN_CANDIDATE` delegation and preserved preview-only approval requirements for executable routes.
- Propagated capped Wordstat association coverage as `WORDSTAT_ASSOCIATIONS_CAPPED`.

## 1.0.1 — 2026-09-02

- Aligned Metrika quality consumption with the producer's nested artifact schema and made missing quality explicit.
- Connected canonical source-of-truth selection to metric reconciliation and forbade ambiguous `demand` evidence.
- Required explicit KPI/money context before cross-record comparability or money-derived metrics.
- Added adversarial eval expectations and clarified delegated previews as non-writing orchestration.

## 1.0.0
- Initial cross-service paid-acquisition plugin.