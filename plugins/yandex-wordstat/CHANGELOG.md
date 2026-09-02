# Журнал изменений — Yandex Wordstat

[**Русский**](CHANGELOG.md) · [English](CHANGELOG.en.md)

## [1.1.0] — 2026-09-02

- Добавлен `yandex-wordstat-topic-map` и deterministic helper `wordstat-topic-map/v1` для candidate demand/topic mapping.
- Equivalent query text дедуплицируется без суммирования overlapping demand; сохраняются все source seeds, Wordstat relation types и отдельные demand observations.
- Candidate topics остаются `CANDIDATE`, candidate relations — `HYPOTHESIS`; Wordstat не утверждает финальные page boundaries.
- `WORDSTAT_ASSOCIATIONS_CAPPED` propagates в topic-map limitations.
- Final SERP clustering явно делегирован `yandex-search-clustering`, а page architecture — `yandex-seo-topical-architecture`.

## [1.0.2] — 2026-09-02

- Добавлен verified 20-association cap и explicit coverage metadata.
- Weekly/monthly operator handling уточнён как repository compatibility guard, `PERIOD_DAILY` сохранён.
- Semantics guidance распространяет `WORDSTAT_ASSOCIATIONS_CAPPED` и no-sum demand invariant.

## [1.0.1] — 2026-09-02

- Добавлен daily Dynamics, secret-safe requests, adversarial no-sum eval и capability matrix.

## [1.0.0] — 2026-09-01

- Первый Yandex Wordstat marketplace plugin.
