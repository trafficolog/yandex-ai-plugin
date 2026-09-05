# Руководство независимого review первого релиза

[**Русский**](REVIEW_FIRST_RELEASE.md) · [English](REVIEW_FIRST_RELEASE.en.md)

> Compatibility title: **First Release Independent Review Guide**

Цель review — независимо проверить architecture boundaries, API assumptions, safety contracts, evidence semantics и соответствие implementation ↔ canonical production contracts для семи shipped plugins.

Release responsibilities определены в [`RELEASE_POLICY.md`](RELEASE_POLICY.md): AI audit является advisory input, CI — mechanical evidence, independent review — отдельным semantic/safety gate, а human maintainer принимает решение о merge/release. Ни один из этих сигналов не должен молча подменять другой. Датированные артефакты выполненных проверок хранятся в [`docs/reviews/`](reviews/README.md).

## 1. Порядок review

1. Repository contracts: `README.md`, `docs/PLUGIN_STANDARD.md`, `docs/SERVICE_MATRIX.md`, `docs/ROADMAP.md`, marketplaces, CI, validator, tests.
2. Service plugins: Direct → Metrika → Webmaster → Wordstat → Search.
3. Cross-service plugins: SEO → Marketing.
4. Исторический implementation context под `docs/superpowers/` можно использовать для понимания design intent и решений конкретного PR, но эти specs/plans **не являются normative/canonical production source**. При расхождении приоритет имеют текущие canonical governance docs, executable validators/tests, plugin contracts и machine-owned registries/matrices.

## 2. Главные invariants

- Plugin является независимой installation/version boundary.
- Skills — focused workflow units, не catch-all документы.
- `yandex-seo` и `yandex-marketing` не имеют Yandex API clients/credentials.
- Official Yandex docs выше donor repositories по API truth.
- Global writes: `read → analyze → preview → explicit approval → write → verify`.
- Cross-service finding → delegated preview → owning service skill → owning preview → approval → write.

## 3. Service checks

**Direct:** report queue/retry semantics, goal/attribution/VAT provenance, criteria/autotargeting, mutation gates, отсутствие universal CPA/CTR kill rules.

**Metrika:** attribution omission provenance, sampling/data lag, Logs lifecycle, import duplication guards, goal semantics.

**Webmaster:** v4/v4.1 routing, crawl/index/search distinction, recrawl quotas, sitemap/feed safety, PRO export lifecycle и 24h URL semantics.

**Wordstat:** GetTop relation distinction, overlap no-sum invariant, 20-association cap, Dynamics operator policy, regions/trends.

**Search:** sync/deferred contracts, strict 250-result depth, snapshot compatibility, conservative URL identity, bridge-risk clustering, presence ≠ market share.

## 4. Cross-service checks

**SEO:** Wordstat demand, Webmaster visibility, Search snapshot и Metrika visitor context remain distinct. Period/geo/device alignment must surface mismatches. Wordstat-only candidate is not automatically a validated content gap. No magic SEO score.

**Marketing:** Direct evidence is required. Direct/Metrika values are reconciled, not summed. KPI fingerprint/money context controls comparability. Evidence roles `canonical`, `reconciliation_only`, `enrichment` remain explicit. Delegated actions stay preview-only. No universal marketing score.

## 5. Adversarial checks

Проверить divide-by-zero/missing revenue, incompatible currency/VAT/period, parameterized URL identity, sampled/lagged source data, top-N coverage, Search bridge risk, immature conversions и missing evidence.

## 6. Verification commands

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

Затем запустить plugin-local suites из соответствующих README. Green CI подтверждает internal contracts, но не заменяет fresh verification внешних API facts. Если independent review недоступен из-за quota/tool limitation, это ограничение фиксируется явно; отсутствие review не считается clean review.

## 7. Intentional limitations

В первом release отсутствуют Tracker, 360, Maps, AppMetrica, YandexGPT, SpeechKit, persistent warehouse и background scheduler. SEO/Marketing не выполняют live writes; Wordstat не объявляется total market size; SERP presence не объявляется market share; recrawl/sitemap не гарантируют indexing/ranking.