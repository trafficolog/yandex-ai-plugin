# Yandex Wordstat

[Русский](README.md) · [**English**](README.en.md)

Version `1.1.2`. Workflow-first demand-research service plugin over the Wordstat API within Yandex Search API v2: GetTop, GetDynamics, GetRegionsDistribution, GetRegionsTree, plus evidence-first candidate topic maps.

> Phase 7 `1.1.0` added `yandex-wordstat-topic-map` and `wordstat-topic-map/v1`; patch `1.1.1` hardens provenance by rejecting duplicate seed identifiers and candidate self-relations without changing ownership of final SERP clustering or page architecture.

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

## Topic Map ownership boundary

`yandex-wordstat-topic-map` produces `wordstat-topic-map/v1`: normalized query evidence, all source seeds/relations, separate demand observations, candidate topics, and candidate relations.

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

Core contract: **Wordstat does not prove final page boundaries**. Associations/co-occurrence are candidate-discovery signals only. Final SERP clustering belongs to `yandex-search-clustering`; page architecture belongs to `yandex-seo-topical-architecture`.

## Interpretation contract

- `results` (nested/popular) and `associations` (similar relation) remain distinct;
- phrase/association counts overlap and are **never summed** into total market demand;
- seed/operator provenance stays attached to numbers; `seeds[].seed` is unique within one topic-map bundle and duplicate identifiers are rejected;
- candidate relations must connect distinct topic IDs; self-relations are invalid;
- GetTop associations are capped at `20`; exactly 20 means `associations_truncated=true` and downstream `WORDSTAT_ASSOCIATIONS_CAPPED`;
- weekly/monthly operator rejection is repository compatibility policy, not a claimed official Yandex prohibition;
- `PERIOD_DAILY` remains the supported non-`+` operator path;
- topic-map confidence `LOW|MEDIUM|HIGH` is an evidence-quality class, not a probability;
- candidate relations remain `HYPOTHESIS` until downstream evidence supports a stronger claim.

Large semantic collections should be written to files/artifacts.

```bash
python -m unittest discover -s tests -v
```