# Changelog

All notable repository-level changes are documented here. Individual plugins also keep their own changelogs where service-specific detail is useful.

This project uses independent SemVer per plugin. The initial marketplace release shipped the seven available plugins at `1.0.0`; the current reviewed maintenance release is `1.0.1`.

## [1.0.1] — 2026-09-02

Review-driven maintenance release that hardens API correctness, cross-service evidence semantics, validation and regression coverage without changing the seven-plugin marketplace boundary.

### Service correctness and provenance

- Yandex Direct Reports now write a JSON metadata sidecar next to TSV output, preserving report type, period, goal/attribution/VAT context when supplied and request provenance without inventing unknown currency.
- Yandex Metrika strengthened import safety for Direct-like expense data and preserved producer-shaped nested quality metadata for downstream consumers.
- Yandex Webmaster tightened preview/export URL redaction and HTTPS-only download handling.
- Yandex Wordstat added supported daily Dynamics handling while keeping weekly/monthly operator restrictions explicit, and added adversarial protection against presenting overlapping phrase-count sums as total market demand.
- Yandex Search corrected absolute ranking across result pages and strengthened bridge-risk/adversarial coverage for URL-overlap clustering.

### Cross-service evidence contracts

- Yandex SEO now requires explicit `site`, `analysis_period` and `search_region_id` in its Evidence Bundle and materializes independent period, geography, Search-configuration and device alignment states.
- SEO geography alignment now distinguishes Search ranking region, Wordstat query region, Webmaster query region and Metrika visitor geography even when numeric region IDs happen to match.
- Yandex Marketing consumes the actual nested Metrika `quality` shape, returns the selected canonical reconciliation record and rejects ambiguous generic `demand` evidence in favor of source-specific metrics such as `wordstat_count`.
- Marketing missing-Direct coverage now returns `ROUTING_REQUIRED` consistently instead of raising in one helper while routing in another.
- Empty Marketing priority lists now use the documented default categorical order rather than being mislabeled as a user-supplied order.
- SEO and Marketing use the same `QUALITY_METADATA_MISSING` limitation marker when Metrika quality metadata is absent.

### URL identity semantics

- Cross-service page/landing joins now remove only tracking parameters (`utm_*`, `yclid`, `_openstat`) from canonical `url_key` identity while preserving functional query parameters such as product/page IDs.
- Stripped tracking values are retained separately as `tracking_params`, so attribution metadata is not discarded while equivalent landing pages no longer fragment into separate identity buckets.

### Evals, validation and CI

- All seven plugin eval fixtures now include machine-checkable `expect` contracts with routing, refusal, required-mention and forbidden-claim assertions, plus adversarial scenarios for the highest-risk semantics.
- Repository validation now checks both marketplace formats, both plugin manifest formats, SemVer consistency, capability matrices, eval expectations, folded YAML frontmatter, runtime-specific paths, credential-like literals and the no-transport boundary for cross-service plugins.
- Path-aware CI now models producer-to-consumer dependencies: source-plugin changes trigger the relevant SEO and/or Marketing regression suites instead of testing only the directly changed plugin.
- Package/version regression assertions were synchronized with `1.0.1` while preserving historical `1.0.0` roadmap assertions.

### Release metadata

- All Codex and Claude plugin manifests plus root marketplace metadata are synchronized at `1.0.1`.
- Plugin READMEs expose capability matrices and current version/state; `docs/SERVICE_MATRIX.md` reports all seven shipped plugins at `1.0.1`.
- `docs/PLUGIN_STANDARD.md` now makes eval expectations, capability/version consistency, secret/path checks and cross-service transport boundaries part of the repository contract.

## [1.0.0] — 2026-09-02

First complete marketplace release covering Yandex advertising, analytics, technical SEO, demand research, web search, and two cross-service orchestration layers.

### Repository foundation

- Established a marketplace monorepo rather than a single monolithic skill.
- Defined plugin as the installation/version boundary and skill as the workflow/knowledge boundary.
- Added root marketplace manifests for agent/Claude-compatible discovery.
- Added `docs/PLUGIN_STANDARD.md`, service matrix, roadmap, repository validator and path-aware CI.
- Standardized safety lifecycle: `read → analyze → preview → explicit approval → write → verify`.
- Standardized backend-agnostic skill execution: connected backend when available → bundled helper → file/export fallback where supported.
- Standardized independent plugin SemVer and third-party notices.

### Yandex Direct 1.0.0

- Moved the initial Direct implementation into `plugins/yandex-direct/` without changing its intended runtime behavior during marketplace restructuring.
- Added eight focused advertising skills covering routing, API, audit, reporting, creation, keywords, budgets and optimization.
- Implemented Reports API v501 behavior including correct 201/202 retry semantics that preserve request payload and `ReportName` while respecting `retryIn`.
- Preserved criterion type/ID/text context and first-class autotargeting/shared-negative workflows.
- Added safe write contracts for campaign/keyword/budget/optimization operations.
- Explicitly rejected arbitrary universal CTR/CPC/CPA/ROAS/kill-rule assumptions.

### Yandex Metrika 1.0.0

- Added ten analytics/data-quality skills.
- Added Management, Reporting, Logs and import helpers using dependency-light Python.
- Added table/by-time/comparison/drilldown reporting modes.
- Preserved sampling, sample share/space/size, data lag, sensitive-data and rounded-row quality metadata.
- Added current attribution handling and rejected obsolete attribution assumptions.
- Added Logs evaluate → create → status → download → clean lifecycle.
- Added offline conversion, call and expense import workflows with a guard against duplicate native Direct expenses.
- Kept visitor parameters/CRM-related capabilities documented but outside the executable 1.0.0 import surface where appropriate.

### Yandex Webmaster 1.0.0

- Added eleven Webmaster workflow skills.
- Added mixed v4/v4.1 routing rather than assuming one API version for every resource.
- Added host/site, diagnostics, search-query, indexing, recrawl, sitemap, link, feed and export workflows.
- Added current OAuth scope assumptions to release references.
- Added Query Analytics/history, indexing/search-presence history and archive lifecycle support.
- Added quota-aware recrawl with same-host/scheme/port validation and graceful `URL_ALREADY_ADDED` handling.
- Added standard Sitemap operations and priority Sitemap recrawl on v4.1.
- Added feed async/batch operations and destructive-operation guards.
- Added PRO/search-result export lifecycle and file-oriented output.
- Preserved the distinctions between crawl, indexing and search presence and avoided claims that recrawl/sitemaps guarantee ranking or inclusion.

### Yandex Wordstat 1.0.0

- Added nine demand-research skills.
- Added Yandex Cloud Wordstat v2 as the primary execution surface for 1.0.0.
- Added API-Key/IAM authentication helpers, quota handling and cost planning.
- Added GetTop, GetDynamics, GetRegionsDistribution and GetRegionsTree support.
- Preserved `results` and `associations` as different relation types.
- Added provenance-aware semantic collection and deduplication that retains all contributing seed phrases.
- Added operator-aware frequency/dynamics rules.
- Added regional count/share/affinity analysis without hard-coded region-name maps.
- Added trend classification that separates growth, explosive growth, seasonality and low-volume percentage noise.
- Added a hard analytical invariant against summing overlapping Wordstat phrase counts and calling the result total market demand.

### Yandex Search 1.0.0

- Added ten web-search/SERP skills.
- Added Search API v2 sync and deferred retrieval helpers.
- Added XML as the canonical structured SEO-analysis format while allowing raw HTML artifact preservation.
- Added reproducible SERP snapshots with configuration fingerprints.
- Added conservative URL normalization and rank comparison guards for incompatible snapshots.
- Added competitor SERP-presence metrics without mislabeling them as market share.
- Added exact shared-URL/Jaccard clustering with an explicit user/workflow threshold.
- Added bridge-risk diagnostics for connected-component clusters created through transitive overlap.
- Added resumable deferred-operation manifests instead of indefinite polling.
- Added workload/cost planning to distinguish small interactive searches from large batch research.

### Yandex SEO 1.0.0

- Added the first cross-service plugin with ten workflow skills and seven pure-data helpers.
- Added a versioned SEO Evidence Bundle consuming Wordstat, Search, Webmaster and Metrika artifacts without implementing new Yandex API clients.
- Added partial capability modes for discovery, visibility, performance and full SEO analysis.
- Added `OBSERVED`, `DERIVED` and `HYPOTHESIS` evidence semantics.
- Added `EXACT`, `APPROXIMATE` and `MISMATCHED` time-alignment semantics.
- Preserved separate geo contexts for SERP ranking, Wordstat demand, Webmaster search data and Metrika visitor data.
- Preserved Wordstat demand and Webmaster demand as separate metrics rather than silently substituting one for the other.
- Added conservative query/URL joins and quality-limitation propagation.
- Added content-gap, cannibalization, CTR, conversion and technical-impact findings.
- Added transparent categorical prioritization without an opaque universal SEO score.
- Added delegated action previews; the plugin itself performs no live writes.

### Yandex Marketing 1.0.0

- Added the paid-acquisition cross-service plugin with eleven workflow skills and eight pure-data helpers.
- Made Direct evidence mandatory for the marketing router; Metrika and Wordstat are primary enrichments and Search is optional context.
- Added a versioned Marketing Evidence Bundle.
- Added KPI fingerprints covering business objective, goal IDs, attribution model, metric basis, currency, VAT basis and period.
- Added source-of-truth rules and reconciliation for overlapping Direct/Metrika cost, click, conversion and revenue views.
- Added `ALIGNED`, `EXPLAINABLE_DIFFERENCE`, `REVIEW` and `INCOMPARABLE` reconciliation states.
- Added `MATURE`, `IMMATURE` and `MATURITY_UNKNOWN` outcome-maturity semantics.
- Added conservative campaign/criterion/goal/query/landing identity handling.
- Added demand/query intelligence without treating Wordstat frequency as guaranteed advertising inventory or numeric missed traffic.
- Added landing/traffic hypotheses, measurement risks and mature KPI-compatible budget candidates.
- Added transparent prioritization without universal CPA/ROAS/CTR/CR thresholds or a magic marketing score.
- Added preview-only delegation to Direct/Metrika owning skills; the plugin performs no live writes.

### CI, validation and testing

- Added repository-level architecture/marketplace tests and repository validation.
- Added dedicated path-aware jobs for Direct, Metrika, Webmaster, Wordstat, Search, SEO and Marketing.
- Added Python compile gates for shipped helper modules.
- Added offline test/eval contracts for each plugin.
- Verified each phase through stacked pull requests and GitHub Actions before first-release finalization.

### Documentation

- Added detailed architecture/design specs under `docs/superpowers/specs/`.
- Added implementation plans under `docs/superpowers/plans/`.
- Added plugin-level README/CHANGELOG/third-party notices.
- Expanded the root README into installation, architecture, safety, capability, testing and operational documentation.
- Added `docs/REVIEW_FIRST_RELEASE.md` for independent architecture/code review.
- Moved Operations / AI / Mobile integrations to the future-release backlog; they are not part of 1.0.0.

### Intentional first-release limitations

- No Yandex Tracker, Yandex 360, Maps, AppMetrica, YandexGPT or SpeechKit plugin is shipped in 1.0.0.
- No generic cross-channel `yandex-growth`/super-agent layer is shipped.
- `yandex-seo` and `yandex-marketing` are read/analyze/recommend/preview orchestration layers and do not own live Yandex mutation clients.
- No persistent SEO/marketing warehouse is included.
- No scheduler/monitoring daemon is included.
- No universal optimization benchmark or opaque scoring model is treated as platform truth.
