# Yandex Wordstat

[**Русский**](README.md) · [English](README.en.md)

Версия `1.0.2`. Workflow-first service plugin для demand research через Yandex Cloud Search API Wordstat v2: GetTop, GetDynamics, GetRegionsDistribution, GetRegionsTree.

> Phase 7 implementation добавляет candidate topic-map capability; release version будет обновлена отдельно после полного contract/doc gate.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Top requests / associations | yes | no | optional | yes | yes |
| Frequency / operator research | yes | no | optional | yes | yes |
| Dynamics, including daily | yes | no | optional | yes | yes |
| Regional distribution / region tree | yes | no | optional | yes | yes |
| Trend classification | yes | no | optional | yes | yes |
| Candidate demand/topic map | yes | no | optional | yes | yes |
| Quota / cost planning | yes | no | optional | yes | yes |

## Topic Map: граница ответственности

`yandex-wordstat-topic-map` формирует `wordstat-topic-map/v1`: нормализованные query evidence, все source seeds/relations, отдельные demand observations, candidate topics и candidate relations.

Pipeline:

```text
Wordstat: yandex-wordstat-topic-map
  ↓ candidate-only wordstat-topic-map/v1
Search: yandex-search-clustering
  ↓ real SERP-overlap validation
SEO: yandex-seo-topical-architecture
  ↓ page decisions / structural_tree / semantic_graph
SEO: yandex-seo-internal-linking
  ↓ preview-only link plan / audit
```

Ключевой контракт: **Wordstat не доказывает финальные page boundaries**. Associations/co-occurrence используются только для candidate discovery. Финальный SERP clustering принадлежит `yandex-search-clustering`, а архитектура страниц — `yandex-seo-topical-architecture`.

## Interpretation contract

- `results` (nested/popular) и `associations` (similar relation) не смешиваются;
- phrase/association counts перекрываются и **не суммируются** в total market demand;
- seed/operator provenance сохраняется рядом с числами;
- GetTop associations имеют cap `20`; ровно 20 → `associations_truncated=true` и limitation `WORDSTAT_ASSOCIATIONS_CAPPED` downstream;
- weekly/monthly operator restriction — repository compatibility policy, не заявленный официальный запрет Яндекса;
- `PERIOD_DAILY` остаётся supported path для non-`+` operators;
- topic-map confidence `LOW|MEDIUM|HIGH` — quality class, не вероятность;
- candidate relations остаются `HYPOTHESIS`, пока downstream evidence не подтверждает более сильный claim.

Большие semantic collections сохраняются в files/artifacts.

```bash
python -m unittest discover -s tests -v
```
