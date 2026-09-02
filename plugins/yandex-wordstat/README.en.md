# Yandex Wordstat

[Русский](README.md) · [**English**](README.en.md)

Version `1.0.2`. Workflow-first demand-research service plugin over Yandex Cloud Search API Wordstat v2: GetTop, GetDynamics, GetRegionsDistribution and GetRegionsTree.

> `DOCS 1.0.0` changes documentation only.

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

- `results` (nested/popular) and `associations` (similar relation) remain distinct;
- phrase/association counts overlap and are **never summed** into total market demand;
- seed/operator provenance stays attached to numbers;
- GetTop associations are capped at `20`; exactly 20 means `associations_truncated=true` and downstream `WORDSTAT_ASSOCIATIONS_CAPPED`;
- weekly/monthly operator rejection is repository compatibility policy, not a claimed official Yandex prohibition;
- `PERIOD_DAILY` remains the supported non-`+` operator path.

Large semantic collections should be written to files/artifacts.

```bash
python -m unittest discover -s tests -v
```
