# Changelog — Yandex Wordstat

[Русский](CHANGELOG.md) · [**English**](CHANGELOG.en.md)

## [1.1.0] — 2026-09-02

- Added `yandex-wordstat-topic-map` and the deterministic `wordstat-topic-map/v1` helper for candidate demand/topic mapping.
- Equivalent query text is deduplicated without summing overlapping demand; all source seeds, Wordstat relation types, and separate demand observations are preserved.
- Candidate topics remain `CANDIDATE` and candidate relations remain `HYPOTHESIS`; Wordstat does not claim final page boundaries.
- `WORDSTAT_ASSOCIATIONS_CAPPED` propagates into topic-map limitations.
- Final SERP clustering is explicitly delegated to `yandex-search-clustering`, while page architecture belongs to `yandex-seo-topical-architecture`.

## [1.0.2] — 2026-09-02

- Added the verified 20-association cap and explicit coverage metadata.
- Clarified weekly/monthly operator handling as repository compatibility policy while preserving `PERIOD_DAILY`.
- Propagated `WORDSTAT_ASSOCIATIONS_CAPPED` and the no-sum demand invariant.

## [1.0.1] — 2026-09-02

- Added daily Dynamics, secret-safe requests, adversarial no-sum evals and the capability matrix.

## [1.0.0] — 2026-09-01

- Initial Yandex Wordstat marketplace plugin.
