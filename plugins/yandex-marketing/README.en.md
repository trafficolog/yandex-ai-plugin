# Yandex Marketing

[Русский](README.md) · [**English**](README.en.md)

Version `1.1.0`. Read/analyze/recommend/preview cross-service paid-acquisition plugin over Direct, Metrika, Wordstat and optional Search. It has no Yandex credentials or HTTP clients.

> `DOCS 1.0.0` changes documentation only.

## Orchestration

```mermaid
flowchart LR
  D[Direct<br/>campaign / spend / clicks] --> B[Marketing Evidence Bundle]
  M[Metrika<br/>goals / attribution / quality] --> B
  W[Wordstat<br/>external demand] --> B
  S[Search<br/>optional SERP context] --> B
  B --> R[Reconciliation Layer]
  R --> C[canonical]
  R --> X[reconciliation_only]
  R --> E[enrichment]
  C --> O[Marketing Orchestrator]
  X --> O
  E --> O
  O --> F[Findings / opportunities]
  O --> P[delegated previews]
  P --> OWN[Direct / Metrika owning skills]
  OWN --> A[preview → approval → write]
```

Direct evidence is required for full acquisition analysis. Metrika and Wordstat are primary enrichments; Search is optional intent/competitive context. Missing Direct returns `routing_required` / `ROUTING_REQUIRED` rather than invented substitute facts.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Direct/Metrika performance reconciliation | yes | no | via source plugins | no | yes |
| Wordstat demand coverage | yes | no | via source plugins | no | yes |
| Search-query intelligence | yes | delegated preview only | via source plugins | no | yes |
| Landing/conversion hypotheses | yes | no | via source plugins | no | yes |
| Budget/query/goal delegated actions | yes | approval in owning plugin | via source plugins | no | yes |

## Evidence contract 1.1.0

- `canonical` — source-of-truth record under repository policy;
- `reconciliation_only` — overlapping comparison evidence, never summed with canonical;
- `enrichment` — context that does not replace the canonical metric.

Generic `metric: demand` is forbidden. Money evidence without currency/VAT/period carries `MONEY_CONTEXT_UNKNOWN` and remains incomparable. Capped Wordstat associations propagate `WORDSTAT_ASSOCIATIONS_CAPPED`.

## Finding taxonomy

`IMPLEMENTED_FINDING_TYPES` contains only the nine deterministic classes actually produced locally. Future classes live in `DEFERRED_FINDING_TYPES`; unknown/deferred findings sort after implemented types with `UNKNOWN_OR_DEFERRED_TYPE`. Dead `NEW_CAMPAIGN_CANDIDATE` routing is removed.

```bash
python -m unittest discover -s tests -v
python -m py_compile scripts/marketing_prioritize.py
```
