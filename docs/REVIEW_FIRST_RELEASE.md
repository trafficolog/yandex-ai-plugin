# First Release Independent Review Guide

**Release candidate:** repository first release / plugin set `1.0.0`  
**Review target:** final `main` after Phase 1–6B + release finalization  
**Primary goal:** verify architecture boundaries, API correctness assumptions, safety contracts, data semantics, and implementation-vs-spec consistency before broader use.

This document is intentionally written for an independent reviewer — human or model — that did not participate in the implementation.

## 1. What is being reviewed

The first release contains seven independently installable plugins:

1. `plugins/yandex-direct/`
2. `plugins/yandex-metrika/`
3. `plugins/yandex-webmaster/`
4. `plugins/yandex-wordstat/`
5. `plugins/yandex-search/`
6. `plugins/yandex-seo/`
7. `plugins/yandex-marketing/`

The first five are service plugins. The last two are cross-service reasoning/orchestration plugins.

Operations / AI / Mobile plugins are **not** part of this release and should not be treated as missing release requirements.

## 2. Recommended review order

A useful independent review sequence is:

### A. Repository contracts

Read first:

- `README.md`
- `docs/PLUGIN_STANDARD.md`
- `docs/SERVICE_MATRIX.md`
- `docs/ROADMAP.md`
- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `.github/workflows/ci.yml`
- `scripts/validate_repo.py`
- `tests/`

Questions:

- Are plugin boundaries actually independent?
- Does marketplace metadata expose only production-ready plugins?
- Does CI isolate plugin-specific work while still rerunning regressions after shared changes?
- Are version declarations consistent?
- Are any credentials or runtime-specific absolute paths leaked into content?

### B. Service plugins

Review in this order because later cross-service plugins depend on their semantics:

1. Direct
2. Metrika
3. Webmaster
4. Wordstat
5. Search

For each service plugin inspect:

- `.codex-plugin/plugin.json`
- `.claude-plugin/plugin.json`
- `skills/*/SKILL.md`
- `references/`
- `scripts/`
- `tests/`
- `evals/`
- `THIRD_PARTY_NOTICES.md`

### C. Cross-service plugins

Then inspect:

- `plugins/yandex-seo/`
- `plugins/yandex-marketing/`

The main review question is not merely whether calculations are correct. It is whether source-specific semantics and limitations remain intact after composition.

### D. Design-vs-implementation consistency

Approved designs live under:

- `docs/superpowers/specs/`

Implementation plans live under:

- `docs/superpowers/plans/`

Compare each plugin's implementation with its design. Flag capabilities silently omitted, semantics changed, or extra behavior introduced without an approved design rationale.

---

## 3. Architecture invariants to challenge

Treat these as claims to verify, not assumptions to accept.

### 3.1 Plugin is the installation/version boundary

Expected:

- each plugin has its own manifests/version;
- users can install service plugins independently;
- service-specific volatile logic stays inside the owning plugin;
- shared packages are not introduced prematurely.

Look for hidden imports or assumptions that accidentally make one service plugin depend on another.

### 3.2 Skill is the workflow/knowledge boundary

Expected:

- router skills direct to focused workflows;
- specialized skills do not become generic catch-all documents;
- skills describe interpretation and safety, not just endpoint lists.

### 3.3 Cross-service plugins do not duplicate Yandex API clients

Expected in `yandex-seo` and `yandex-marketing`:

- no OAuth/API-Key/IAM credential surface;
- no `api.*.yandex.*` transport clients;
- no duplicated Direct/Metrika/Webmaster/Search/Wordstat endpoint implementations;
- helpers operate on structured input data/artifacts only.

This is a high-priority review item.

### 3.4 Official documentation beats donor repositories

Review `references/sources.md` and `THIRD_PARTY_NOTICES.md`.

Check that donor code was used as a capability/methodology reference rather than as an unquestioned source of current API truth.

---

## 4. Safety review

The global mutation contract is:

```text
read → analyze → preview → explicit approval → write → verify
```

### Verify service writes

Search for any code path capable of:

- changing Direct campaigns/budgets/keywords/strategies;
- creating or modifying Metrika goals/imports;
- deleting Webmaster hosts/sitemaps/feeds;
- submitting recrawl or quota-consuming operations.

For each path confirm:

1. the current state/target is read first where needed;
2. an exact preview can be generated;
3. user approval is a separate step;
4. execution does not happen simply because a recommendation exists;
5. verification/response handling is defined after write.

### Verify cross-service delegation

`yandex-seo` and `yandex-marketing` must never execute delegated mutations themselves.

Expected flow:

```text
cross-service finding
→ delegated preview descriptor
→ owning service skill
→ owning service preview
→ explicit approval
→ write
```

Try to find any shortcut that bypasses this.

### Activation should remain separate

Where creation and activation/publication are different actions, check that creating an object does not silently activate it unless explicitly requested.

---

## 5. Secret-handling review

Search the repository for:

```text
Authorization:
OAuth 
Api-Key 
Bearer 
YANDEX_
~/.claude
~/.codex
~/.openclaw
```

Expected:

- example env variable names are acceptable in service plugins;
- no real secret values exist;
- preview/log helpers redact credential values;
- cross-service plugins do not require Yandex credentials;
- no runtime-specific home-directory assumptions leak into plugin workflows.

---

## 6. Direct-specific review targets

High-risk assumptions to verify against current Yandex Direct documentation:

- Reports API version/path used by the release;
- HTTP 201/202 report queue semantics;
- `retryIn` behavior;
- preserving report payload and `ReportName` across retries;
- criterion fields and autotargeting semantics;
- currency/VAT interpretation in reports;
- conversion goal and attribution handling;
- write-operation preview/approval boundaries.

Adversarial tests:

- report queued twice before success;
- revenue absent but user asks for ROAS/DRR;
- multiple goals with different business meaning;
- keyword and autotargeting criteria mixed in one report;
- user asks to increase budget without providing objective/constraints;
- zero conversions on a small sample and user asks to disable everything.

Expected behavior: no invented business target and no universal kill rule.

---

## 7. Metrika-specific review targets

Verify:

- current attribution models in references/helpers;
- sampling metadata propagation;
- data-lag metadata propagation;
- sensitive-data/rounding metadata where returned;
- Logs lifecycle and date constraints;
- import formats/guards;
- Direct expense duplication protection;
- goal semantics are not collapsed into one generic conversion without disclosure.

Adversarial tests:

- sampled report used in cross-service analysis;
- goal definitions changed between periods;
- legacy attribution requested;
- Direct expense import requested when native Direct expenses already exist;
- incomplete Logs request is described as complete data.

---

## 8. Webmaster-specific review targets

Verify against current documentation:

- mixed v4/v4.1 endpoint routing;
- OAuth scopes;
- Query Analytics/history routes;
- indexing/search-presence distinction;
- recrawl quota/queue behavior;
- same-host/scheme/default-port validation;
- `URL_ALREADY_ADDED` handling;
- priority Sitemap recrawl version/limits;
- feed HTTPS and batch constraints;
- archive/PRO export lifecycle.

Adversarial tests:

- `https://example.com` host with `http://example.com/page` recrawl;
- implicit HTTPS 443 vs explicit `:443`;
- cross-domain recrawl request;
- quota exhausted;
- popular-query top-N treated as all site queries;
- user expects recrawl to guarantee indexing/ranking.

Expected behavior: strong distinction between submission, crawling, indexing and ranking.

---

## 9. Wordstat-specific review targets

Verify current Cloud Wordstat v2 assumptions:

- auth modes and roles/scopes;
- endpoint/request schemas;
- REST camelCase field names;
- GetTop results vs associations;
- dynamics granularity/operator restrictions;
- region tree handling;
- rate/cost assumptions in references;
- trend classification edge cases.

Most important analytical invariant:

> overlapping phrase counts must not be summed and labeled total market demand.

Adversarial tests:

- one phrase appears from multiple seeds;
- association and nested result have same text;
- demand rises from 2 to 20 (+900%);
- repeated seasonal spike appears year over year;
- high absolute region volume but low affinity vs a smaller high-affinity region;
- user asks for the "total market" by summing all returned phrases.

---

## 10. Search-specific review targets

Verify current Search API v2 behavior:

- sync/deferred endpoint contracts;
- auth/role/scope assumptions;
- XML parsing assumptions;
- HTML is not treated as a stable structured contract;
- request limits/index/region/search settings;
- async lifecycle/result retention assumptions;
- pricing/quotas in references.

SERP analytics review:

- structured clustering should use flat semantics;
- snapshots must preserve configuration fingerprint;
- rank comparisons should reject materially incompatible snapshots;
- URL normalization should not collapse semantically different parameterized URLs;
- clustering threshold must be explicit;
- bridge-risk must expose transitive weak clusters.

Adversarial clustering example:

```text
A shares 4 URLs with B
B shares 4 URLs with C
A shares 0 URLs with C
```

Expected: if one connected cluster is produced, bridge risk is visible.

Also check that competitor SERP presence is not mislabeled as market share.

---

## 11. SEO cross-service review targets

This is one of the highest-value review areas.

### Source semantics

Confirm these remain distinct:

- Wordstat demand;
- Webmaster demand-like/query metrics;
- Search point-in-time ranking context;
- Metrika visitor/landing/conversion context.

### Time alignment

Try mixing:

- Wordstat rolling 30-day evidence;
- Webmaster fixed calendar range;
- Metrika fixed calendar range;
- Search point-in-time snapshot.

Expected: `EXACT`, `APPROXIMATE` or `MISMATCHED` limitations rather than one falsely uniform time range.

### Geographic alignment

Do not allow:

```text
Metrika visitor city = Moscow
```

to silently imply:

```text
Search SERP region = Moscow
```

### Query and URL joins

Try near-synonyms and parameterized landing URLs. Expected: conservative joins by default.

### Content gaps

Wordstat-only evidence should produce a discovery candidate, not a high-confidence validated content gap.

### Cannibalization

Two URLs or two keywords alone are insufficient. Look for real Search/Webmaster evidence of competing own URLs/visibility split.

### CTR/conversion findings

Look for hidden universal CTR/CR expectations. There should be none.

### Score review

There should be no opaque magic SEO score. If user weights are supported, formula/weights should be explicit.

---

## 12. Marketing cross-service review targets

This is the other highest-value review area.

### Mandatory Direct evidence

Verify the router does not pretend to perform paid-acquisition analysis without Direct evidence.

### Direct/Metrika double-counting

Try supplying the same paid activity through both systems.

Forbidden:

```text
total cost = Direct cost + Metrika Direct cost
```

or equivalent conversion/revenue addition.

Expected: source-of-truth + reconciliation roles.

### KPI fingerprint

Test campaigns with:

- different goal IDs;
- purchase vs micro-conversion;
- different attribution models;
- different currencies;
- different VAT basis;
- different/noncomparable periods.

Expected: incompatible context blocks direct efficiency ranking.

### Conversion maturity

Test recent data with known lag and recent data with unknown lag.

Expected:

- `IMMATURE` when evidence says it is incomplete;
- `MATURITY_UNKNOWN` when maturity cannot be established;
- no arbitrary "ignore last 7 days" rule.

### Wordstat demand

High demand + low Direct coverage should produce an expansion/coverage candidate, not a numeric lost-impression claim.

### Search terms

Zero conversions should not automatically create a negative keyword. Objective, maturity, spend and sufficiency matter.

### Landing hypotheses

Observational query→landing→conversion differences should remain hypotheses unless stronger evidence exists.

### Budget safety

Budget reallocation findings should require compatible KPI evidence and remain delegated previews.

### Score review

There should be no hidden marketing score or universal CPA/ROAS benchmark.

---

## 13. Data-quality propagation review

Trace a limitation from source to final cross-service output.

Examples:

- Metrika `sampled=true`;
- Metrika data lag;
- Webmaster popular-query top-N coverage;
- Search bridge risk;
- Wordstat trailing-window timing;
- conversion maturity.

Expected: the final finding preserves or surfaces the limitation. A cross-service helper must not "clean" the evidence by dropping caveats.

---

## 14. Numerical/adversarial checks

Useful independent property-style checks:

### Division/zero handling

For CTR/CR/CPC/CPA/ROAS/DRR helpers:

- zero impressions;
- zero clicks;
- zero conversions;
- zero spend;
- missing revenue.

Expected: no divide-by-zero, no fabricated metric.

### Money context

- RUB vs another currency;
- VAT included vs excluded;
- different date basis;
- different goal basis.

Expected: no silent arithmetic across incompatible values.

### URL normalization

Test:

```text
HTTPS://Example.com:443/path?a=1&b=2#x
https://example.com/path?b=2&a=1
https://example.com/path?id=1
https://example.com/path?id=2
```

Expected: first two can normalize compatibly; last two remain distinct unless an explicit policy says otherwise.

### Query normalization

Test:

```text
Купить   зубную пасту
купить зубную пасту
купить пасту
```

Expected: the first two may share a normalized key; the third is not automatically merged by stemming/fuzzy semantics.

---

## 15. CI and test review

Run or inspect:

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

Then each plugin suite and compile command documented in root `README.md`.

Review questions:

- Do tests assert real behavior rather than only file existence?
- Are safety invariants covered by tests/evals?
- Can a mutation path be added without a test noticing?
- Are cross-service double-counting guards tested?
- Are failure/edge cases present, not just happy paths?
- Does path-aware CI correctly trigger shared regressions?

Do not treat a green test suite as proof that current external API documentation is still unchanged; freshness review is separate.

---

## 16. Documentation freshness review

Because Yandex APIs can change independently of this repository, check dated/current official documentation for all externally significant assumptions.

Particular freshness hotspots:

- Direct Reports/API versions and attribution behavior;
- Metrika attribution/Logs/import constraints;
- Webmaster API versions/scopes/quotas;
- Wordstat Cloud API schemas, limits and pricing;
- Search API quotas/pricing/async lifecycle and index types.

If current docs differ from a release reference, classify whether the mismatch is:

1. documentation-only;
2. helper validation mismatch;
3. runtime-breaking API mismatch;
4. safety-impacting mismatch.

---

## 17. Known intentional limitations of 1.0.0

These should not be reported as bugs unless the implementation contradicts its documentation:

- no Tracker plugin;
- no Yandex 360 plugin;
- no Maps plugin;
- no AppMetrica plugin;
- no YandexGPT plugin;
- no SpeechKit plugin;
- no generic all-channel growth super-agent;
- no persistent cross-service warehouse;
- no scheduler/background monitor;
- no built-in universal SEO/marketing score;
- no universal campaign optimization thresholds;
- no live writes from `yandex-seo` or `yandex-marketing`;
- no claim that Wordstat equals total market size;
- no claim that SERP presence equals market share;
- no claim that recrawl/sitemap submission guarantees indexing/ranking.

These items are backlog/design choices, not unfinished 1.0.0 requirements.

---

## 18. Suggested independent-review output format

For a model such as Claude Opus, ask for findings in this structure:

```text
Severity: BLOCKER | HIGH | MEDIUM | LOW | NOTE
Area: architecture | API correctness | safety | data semantics | testing | docs | maintainability
File(s): exact paths
Finding: concise statement
Why it matters: concrete failure mode
Evidence: code/reference lines
Recommended change: minimal precise fix
Regression test: suggested test if applicable
```

Also request a final section:

```text
Release recommendation:
- APPROVE
- APPROVE WITH FOLLOW-UPS
- HOLD

Top 5 residual risks
Top 5 strongest design decisions
API assumptions requiring fresh documentation verification
```

---

## 19. Ready-to-use review prompt

The following can be used as a starting prompt for an independent model review:

> Perform an adversarial first-release review of this repository. Do not assume the implementation is correct because CI is green. Start with `README.md`, `docs/PLUGIN_STANDARD.md`, `docs/REVIEW_FIRST_RELEASE.md`, `docs/SERVICE_MATRIX.md`, `docs/ROADMAP.md`, then compare every plugin against its approved spec under `docs/superpowers/specs/`. Review service plugins before `yandex-seo` and `yandex-marketing`. Focus on API freshness/correctness, safety boundaries, secret handling, double counting, incompatible metric contexts, temporal/geographic alignment, query/URL joins, quota/cost semantics, destructive operations, and tests that could allow false confidence. Verify current Yandex documentation independently for volatile external assumptions. Report only concrete findings with severity, exact files, evidence, impact, recommended fix and regression test. Distinguish actual bugs from documented first-release limitations. End with APPROVE / APPROVE WITH FOLLOW-UPS / HOLD and the top residual risks.

---

## 20. Release acceptance criteria for this review

A strong independent review should be able to answer "yes" to all of the following before unconditional approval:

- Are plugin boundaries coherent and independently installable?
- Are all service API assumptions current enough for release use?
- Are consequential mutations always approval-gated?
- Can cross-service plugins operate without credentials and without executing writes?
- Are overlapping metrics reconciled instead of double-counted?
- Are period/geo/attribution/KPI mismatches exposed rather than hidden?
- Are heuristic classifications clearly distinguished from source observations?
- Are user/business targets required where no platform-universal target exists?
- Are sampling, lag, top-N and similar quality limitations propagated?
- Do tests meaningfully cover the dangerous paths?
- Is Phase 7 clearly backlog rather than implied first-release functionality?

If any answer is "no", the finding should state whether it blocks release or is safe as a documented follow-up.
