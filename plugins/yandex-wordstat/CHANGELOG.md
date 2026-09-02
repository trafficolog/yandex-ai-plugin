# Changelog

## 1.0.2 — 2026-09-02

- Added the verified 20-association GetTop cap and explicit coverage metadata so downstream workflows can detect truncated association coverage.
- Clarified weekly/monthly Dynamics operator handling as a repository compatibility guard rather than an asserted Yandex prohibition while preserving `PERIOD_DAILY` support.
- Updated Wordstat semantics guidance to propagate `WORDSTAT_ASSOCIATIONS_CAPPED` and preserve no-sum demand semantics.

## 1.0.1 — 2026-09-02

- Added documented `PERIOD_DAILY` Dynamics support while retaining weekly/monthly operator restrictions.
- Removed raw authorization secrets from serializable request artifacts.
- Added adversarial eval coverage against summing overlapping phrase counts as total market demand.
- Added the required capability matrix.

## 1.0.0 — 2026-09-01

- Initial Yandex Wordstat marketplace plugin.