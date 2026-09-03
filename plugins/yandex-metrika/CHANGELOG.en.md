# Changelog — Yandex Metrika

[Русский](CHANGELOG.md) · [**English**](CHANGELOG.en.md)

## [1.0.3] — 2026-09-03

- Closed the residual Direct expense-guard gap for CSV files without `UTMSource` / `UTMMedium`.
- Added `DIRECT` / `NON_DIRECT` / `UNVERIFIED` provenance classification from UTM and `TrafficSource` / `TrafficSourceDetail` evidence.
- Official `TrafficSourceDetail=yandex_direct_star` is now detected as `DIRECT_DUPLICATION_RISK` independently of UTM fields.
- Insufficient source provenance, such as generic `TrafficSource=ad` without source detail, fails closed as `DIRECT_SOURCE_UNVERIFIED` and requires explicit `--allow-direct-risk` after review.
- Explicit non-Direct details such as `google_adwords` remain allowed; an arbitrary provider label like `MyDirect` is not declared Direct from substring matching alone.

## [1.0.2] — 2026-09-02

- Hardened the Direct expense duplication guard: explicit tokenized labels (`Yandex Direct RU`, `direct_ads`, `Яндекс Директ агентство`) are rejected in addition to exact aliases.
- The CSV-content `UTMSource` / `UTMMedium` guard remains an independent second layer with the explicit `--allow-direct-risk` override.
- Arbitrary substrings such as `MyDirect` are not declared Direct provenance without additional evidence.
- Added the guard to the repository contract matrix as a high-risk traceability contract.

## [1.0.1] — 2026-09-02

- Strengthened Yandex Direct expense duplicate-risk detection.
- Preserved explicit Reporting API attribution metadata without inventing a default when attribution is omitted.
- Preserved producer-shaped nested quality metadata for cross-service consumers.
- Added verifiable eval expectations for reporting, imports, Logs and write safety.

## [1.0.0] — 2026-09-01

- Initial Yandex Metrika plugin with specialized analytics/data-quality/goals/Logs/import skills and dependency-light preview-before-write helpers.
