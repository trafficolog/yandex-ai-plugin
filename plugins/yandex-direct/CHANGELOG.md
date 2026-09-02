# Changelog

## 1.0.1 — 2026-09-02

- Made API method safety allowlist-based: unknown and mutating methods are preview-first by default.
- Made Reports attribution/goals explicit, removed obsolete `IncludeDiscount`, and retry the first HTTP 500 once.
- Added KPI provenance metadata sidecars for TSV reports without inventing currency.
- Added regression eval expectations for write safety and report context.

## 1.0.0 — 2026-09-01

- Split monolithic Yandex Direct knowledge into 8 discoverable skills.
- Updated core API workflow to v501 and EPK-first mental model.
- Added safe dependency-free API helper with write preview by default.
- Added Reports v501 helper with stable offline polling request and `retryIn` support.
- Added autotargeting and shared-negative-set guidance.
- Reworked audit/optimization rules to avoid universal PPC folklore thresholds.
- Added OpenAI Codex plugin and GitHub marketplace manifests.
- Added Claude-compatible metadata for portability.
- Added offline unit tests and third-party attribution.
