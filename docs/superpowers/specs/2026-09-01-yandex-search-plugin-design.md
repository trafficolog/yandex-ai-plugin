# Yandex Search Plugin Design

**Status:** Approved on 2026-09-01

## Purpose

Ship `plugins/yandex-search` as the fifth independent Yandex AI marketplace plugin. The plugin is SEO-first: it retrieves classic Yandex web SERPs, normalizes reproducible snapshots, supports cost-aware sync/deferred batch execution, compares rankings/competitor presence, and clusters query intent by real URL overlap. Wordstat remains a separate demand-statistics plugin.

## API baseline

Verified against current Yandex AI Studio documentation on 2026-09-01.

- Sync endpoint: `POST https://searchapi.api.cloud.yandex.net/v2/web/search`.
- Deferred endpoint: `POST https://searchapi.api.cloud.yandex.net/v2/web/searchAsync`.
- REST request fields use CamelCase.
- API-key auth uses `Authorization: Api-Key ...`; IAM uses `Authorization: Bearer ...`.
- Service account role: `search-api.webSearch.user`; API-key scope: `yc.search-api.execute`.
- Search types: RU, TR, COM, KK, BE, UZ.
- XML is the canonical structured analytics format. HTML is kept only as a raw artifact because HTML may contain ads/quick answers and is not a stable structured contract.
- `GROUP_MODE_FLAT`, `docsInGroup=1` is mandatory for rank and clustering workflows.
- Up to 250 results per query; query text max 400 chars / 40 words.
- Sync quota: 10 rps / 10,000 requests per hour. Deferred quota: 10 rps / 35,000 requests per hour; result polling 10 rps.
- Deferred minimum processing time is 5 minutes; result retention is 12 hours.
- Pricing is dated metadata, never a billing guarantee. Current RUB baseline: daytime sync 488 RUB/1000; daytime deferred 30.5 RUB/1000; nighttime sync 366 RUB/1000; nighttime deferred 25.41 RUB/1000.

## Plugin boundary

`yandex-search` owns classic Web Search retrieval and SERP analytics. It does not own Wordstat demand data, Image Search, Generative Search, infocontexts, HTML SERP scraping, or scheduling.

## Skills

The approved capability set contains router plus nine specialized skills:

1. `yandex-search` router
2. `yandex-search-web`
3. `yandex-search-batch`
4. `yandex-search-serp`
5. `yandex-search-competitors`
6. `yandex-search-rankings`
7. `yandex-search-clustering`
8. `yandex-search-operators`
9. `yandex-search-research`
10. `yandex-search-api`

The approved design text called this “9 skills” while enumerating router plus nine specialized skills. As with Phase 4, implementation preserves the explicitly enumerated capability set: **10 discoverable skills**.

## Execution helpers

- `_http.py`: dependency-free JSON/raw HTTP and auth header helpers.
- `ys_api.py`: endpoints, auth, query limits, quota/cost planning, mode recommendation.
- `ys_request.py`: validated REST request builder and canonical config fingerprint.
- `ys_parse.py`: Base64 decode and tolerant XML normalization; HTML returned as raw text artifact.
- `ys_async.py`: operation manifest, submit/status/collect primitives; no endless polling.
- `ys_batch.py`: workload plan, cost preview, sync/deferred recommendation.
- `ys_serp.py`: URL normalization, snapshot construction, domain extraction.
- `ys_overlap.py`: overlap matrix, Jaccard, threshold-required clustering, bridge-risk diagnostics.
- `ys_compare.py`: compatible-snapshot rank deltas and competitor SERP-presence metrics.

All helpers use the Python standard library only.

## Snapshot contract

Every SERP snapshot records query, search type, region, page, grouping, result count, freshness/sort/family/fix-typos options, response format, collection time and a deterministic configuration fingerprint. Rank comparisons must reject snapshots with incompatible search configuration.

URL comparison normalization lowercases scheme/host, removes default ports/fragments, ensures a path, and sorts query parameters. It does not drop query parameters automatically.

## Clustering contract

Clustering consumes FLAT XML snapshots and an explicit `min_shared_urls`; no hidden universal threshold is allowed. The result includes pairwise shared URL count, Jaccard, representative query, weakest pair, and `bridge_risk` when connected-components transitivity joins queries whose direct overlap is below the configured threshold.

SERP overlap is an intent signal, not a semantic truth. The plugin must not call SERP presence “market share”. Weighted visibility belongs to future cross-service `yandex-seo` and may combine Wordstat demand with Search presence.

## Sync/deferred policy

Interactive single/few-query work may use sync. Larger batches receive a cost preview and execution recommendation; deferred is preferred when economically meaningful. The helper never automatically spends money simply because a quota is available.

Deferred execution is resumable: submit, save operation IDs, inspect status, and collect results as separate actions. Manifests retain submission timestamps so callers can flag results approaching the documented 12-hour retention limit.

## Region integration

Standalone Search accepts a numeric Yandex region ID. If Wordstat is also installed, agents may resolve human place names through Wordstat `GetRegionsTree`, but Search does not duplicate a static region-name map.

## Donors

Official Yandex AI Studio documentation is the source of truth. `mkultraaaa/claude-yandex-skills` is a workflow/cache/resume donor. `oleg-cat/yandex-search-mcp` is a structured-output/retry/capability donor. Donor hard-coded paths, roles or stale prices are not copied blindly. Attribution is retained in `THIRD_PARTY_NOTICES.md` and `references/sources.md`.

## Testing and CI

Offline tests cover package layout, auth/request validation, XML parsing, Base64 handling, URL normalization, snapshot fingerprints, async manifests, cost/mode planning, overlap/Jaccard/bridge risk, comparison compatibility and competitor presence. Root tests require marketplace registration, service-matrix availability and a path-aware Search CI job. Previous plugin trees must remain unchanged.
