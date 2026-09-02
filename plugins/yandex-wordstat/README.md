# Yandex Wordstat 1.0.0

Workflow-first plugin for Yandex Wordstat demand research. The bundled standard-library Python backend targets Yandex Cloud Search API Wordstat v2 and supports GetTop, GetDynamics, GetRegionsDistribution and GetRegionsTree.

Highlights:

- nine focused skills instead of one monolith;
- API-Key or IAM auth with redacted previews;
- separate nested results and associations;
- provenance-aware multi-seed semantics;
- no fake sum-of-frequency "market size";
- operator-aware monthly/weekly Dynamics;
- regional volume/share/affinity analysis;
- robust trend labels with low-volume and seasonality guards;
- quota/cost planning before large research batches.

Large research results should be written to JSON/files rather than injected wholesale into agent context.
