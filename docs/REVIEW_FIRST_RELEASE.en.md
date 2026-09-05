# First Release Independent Review Guide

[Русский](REVIEW_FIRST_RELEASE.md) · [**English**](REVIEW_FIRST_RELEASE.en.md)

The goal is an independent challenge of architecture boundaries, API assumptions, safety contracts, evidence semantics, and implementation-vs-canonical-contract consistency across the seven shipped plugins.

Release responsibilities are defined in [`RELEASE_POLICY.en.md`](RELEASE_POLICY.en.md): AI audit is advisory input, CI is mechanical evidence, independent review is a separate semantic/safety gate, and a human maintainer decides whether to merge/release. None of these signals silently replaces another. Dated evidence from completed reviews lives under [`docs/reviews/`](reviews/README.en.md).

## 1. Review order

1. Repository contracts: `README.en.md`, plugin standard, service matrix, roadmap, marketplaces, CI, validator and root tests.
2. Service plugins: Direct → Metrika → Webmaster → Wordstat → Search.
3. Cross-service plugins: SEO → Marketing.
4. Historical implementation context under `docs/superpowers/` may be used to understand design intent and decisions from a particular PR, but those specs/plans are **not normative or canonical production sources**. When they differ from the current repository, current governance docs, executable validators/tests, plugin contracts, and machine-owned registries/matrices take precedence.

## 2. Core invariants

- Plugin is the independent installation/version boundary.
- Skills are focused workflow units, not catch-all documents.
- `yandex-seo` and `yandex-marketing` have no Yandex API clients or credentials.
- Official Yandex documentation outranks donor repositories for API truth.
- Global writes follow `read → analyze → preview → explicit approval → write → verify`.
- Cross-service finding → delegated preview → owning service skill → owning preview → approval → write.

## 3. Service checks

**Direct:** report queue/retry semantics, goal/attribution/VAT provenance, criteria/autotargeting, mutation gates, no universal CPA/CTR kill rules.

**Metrika:** attribution omission provenance, sampling/data lag, Logs lifecycle, import duplication guards, goal semantics.

**Webmaster:** v4/v4.1 routing, crawl/index/search distinction, recrawl quotas, sitemap/feed safety, PRO export lifecycle and 24-hour URL semantics.

**Wordstat:** GetTop relation distinction, overlap no-sum invariant, 20-association cap, Dynamics operator policy, regions/trends.

**Search:** sync/deferred contracts, strict 250-result depth, snapshot compatibility, conservative URL identity, bridge-risk clustering, presence ≠ market share.

## 4. Cross-service checks

**SEO:** Wordstat demand, Webmaster visibility, Search snapshots and Metrika visitor context remain distinct. Period/geo/device mismatches must surface. Wordstat-only evidence is not automatically a validated content gap. No magic SEO score.

**Marketing:** Direct evidence is required. Direct/Metrika values are reconciled, not summed. KPI fingerprint/money context gates comparability. Roles `canonical`, `reconciliation_only`, `enrichment` remain explicit. Delegated actions stay preview-only. No universal marketing score.

## 5. Adversarial checks

Exercise divide-by-zero/missing revenue, incompatible currency/VAT/period, parameterized URL identity, sampled/lagged source data, top-N coverage, Search bridge risk, immature conversions and missing evidence.

## 6. Verification

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

Then run plugin-local suites documented in each README. Green CI validates internal contracts but does not replace fresh verification of external API facts. If independent review is unavailable because of a quota/tool limitation, record that limitation explicitly; absence of review is not a clean review.

## 7. Intentional limitations

The first release excludes Tracker, 360, Maps, AppMetrica, YandexGPT, SpeechKit, a persistent warehouse and a background scheduler. SEO/Marketing perform no live writes; Wordstat is not total market size; SERP presence is not market share; recrawl/sitemap submission does not guarantee indexing/ranking.