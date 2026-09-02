# Yandex Wordstat 1.0.2

Workflow-first plugin for Yandex Wordstat demand research. The bundled standard-library Python backend targets Yandex Cloud Search API Wordstat v2 and supports GetTop, GetDynamics, GetRegionsDistribution and GetRegionsTree.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Top requests / associations | yes | no | optional | yes | yes |
| Frequency / operator research | yes | no | optional | yes | yes |
| Dynamics, including daily | yes | no | optional | yes | yes |
| Regional distribution / region tree | yes | no | optional | yes | yes |
| Trend classification | yes | no | optional | yes | yes |
| Quota / cost planning | yes | no | optional | yes | yes |

Highlights:

- nine focused skills instead of one monolith;
- API-Key or IAM auth with redacted previews and secret-safe request artifacts;
- separate nested results and associations;
- GetTop association coverage cap of 20 with explicit `associations_truncated` metadata;
- provenance-aware multi-seed semantics;
- no fake sum-of-frequency "market size";
- operator-aware daily/monthly/weekly Dynamics, with monthly/weekly restrictions described as plugin compatibility policy rather than an asserted Yandex prohibition;
- regional volume/share/affinity analysis;
- robust trend labels with low-volume and seasonality guards;
- quota/cost planning before large research batches.

Large research results should be written to JSON/files rather than injected wholesale into agent context. When exactly 20 associations are returned, downstream workflows must surface capped coverage instead of claiming an exhaustive semantic set.
