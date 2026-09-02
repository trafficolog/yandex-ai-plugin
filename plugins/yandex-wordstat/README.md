# Yandex Wordstat

[**Русский**](README.md) · [English](README.en.md)

Версия `1.0.2`. Workflow-first service plugin для demand research через Yandex Cloud Search API Wordstat v2: GetTop, GetDynamics, GetRegionsDistribution, GetRegionsTree.

> `DOCS 1.0.0` меняет только документацию.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Top requests / associations | yes | no | optional | yes | yes |
| Frequency / operator research | yes | no | optional | yes | yes |
| Dynamics, including daily | yes | no | optional | yes | yes |
| Regional distribution / region tree | yes | no | optional | yes | yes |
| Trend classification | yes | no | optional | yes | yes |
| Quota / cost planning | yes | no | optional | yes | yes |

## Interpretation contract

- `results` (nested/popular) и `associations` (similar relation) не смешиваются;
- phrase/association counts перекрываются и **не суммируются** в total market demand;
- seed/operator provenance сохраняется рядом с числами;
- GetTop associations имеют cap `20`; ровно 20 → `associations_truncated=true` и limitation `WORDSTAT_ASSOCIATIONS_CAPPED` downstream;
- weekly/monthly operator restriction — repository compatibility policy, не заявленный официальный запрет Яндекса;
- `PERIOD_DAILY` остаётся supported path для non-`+` operators.

Большие semantic collections сохраняются в files/artifacts.

```bash
python -m unittest discover -s tests -v
```
