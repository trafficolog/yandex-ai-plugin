# Yandex Wordstat Phase 4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `plugins/yandex-wordstat/` version `1.0.0` as the fourth production plugin in the Yandex AI marketplace, with nine workflow skills, seven dependency-free helpers, current Cloud Wordstat v2 behavior, offline tests/evals and monorepo integration.

**Architecture:** Skills own research methodology, interpretation and quota/cost safety. Standard-library Python helpers own Cloud REST request construction and pure normalization/analysis. `GetTop` preserves nested results and associations separately; semantic merging preserves provenance; dynamics/trends and regions are pure-analysis helpers layered over API responses.

**Tech Stack:** Agent Skills Markdown, OpenAI/Codex plugin JSON, Claude plugin JSON, Python 3.13 standard library (`urllib`, `json`, `argparse`, `statistics`, `datetime`, `pathlib`), `unittest`, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-01-yandex-wordstat-plugin-design.md`

## Global Constraints

- Plugin version is exactly `1.0.0`.
- Primary bundled backend is Yandex Cloud Wordstat REST v2; legacy Wordstat v1 is reference-only in 1.0.0.
- Python helpers have no runtime dependency outside the standard library.
- Tests never contact Yandex services or require real credentials.
- Every skill frontmatter description starts with `Use when`.
- No runtime-specific paths such as `~/.claude/`, `~/.codex/` or `~/.openclaw/`.
- `YANDEX_WORDSTAT_API_KEY` and `YANDEX_WORDSTAT_IAM_TOKEN` are mutually exclusive.
- `YANDEX_WORDSTAT_FOLDER_ID`, when supplied, is trimmed and limited to at most 50 characters; never require length 20.
- `GetTop` keeps `results` and `associations` distinct and parses numeric strings to integers.
- Semantic deduplication preserves all seed provenance.
- Never sum overlapping phrase counts and label the sum total demand/market size/unique searches.
- Cloud v2 monthly/weekly Dynamics rejects unsupported operator expressions; only `+` is guaranteed for those granularities.
- Current quota baseline is 10 requests/sec and 100 requests/hour; default planner safety budget is 90/hour.
- Current price baseline verified 2026-09-01: GetTop 20 RUB/1000, GetDynamics 20 RUB/1000, Regions 50 RUB/1000, RegionsTree free.
- Phase 4 is stacked on `phase-3-yandex-webmaster` and must not functionally modify Direct, Metrika or Webmaster.

---

### Task 1: Wordstat package and discovery contract

**Files:**
- Create: `plugins/yandex-wordstat/.codex-plugin/plugin.json`
- Create: `plugins/yandex-wordstat/.claude-plugin/plugin.json`
- Create: `plugins/yandex-wordstat/.env.example`
- Create: `plugins/yandex-wordstat/README.md`
- Create: `plugins/yandex-wordstat/CHANGELOG.md`
- Create: `plugins/yandex-wordstat/THIRD_PARTY_NOTICES.md`
- Create: `plugins/yandex-wordstat/evals/scenarios.json`
- Create: nine `plugins/yandex-wordstat/skills/*/SKILL.md`
- Test: `plugins/yandex-wordstat/tests/test_plugin_layout.py`

**Interfaces:**
- Plugin name `yandex-wordstat`, version `1.0.0`, `skills: "./skills/"`.
- Exact skills: `yandex-wordstat`, `-research`, `-semantics`, `-frequency`, `-dynamics`, `-regions`, `-trends`, `-operators`, `-api`.

- [ ] **Step 1: Write failing layout test**

```python
EXPECTED = {
    "yandex-wordstat", "yandex-wordstat-research", "yandex-wordstat-semantics",
    "yandex-wordstat-frequency", "yandex-wordstat-dynamics", "yandex-wordstat-regions",
    "yandex-wordstat-trends", "yandex-wordstat-operators", "yandex-wordstat-api",
}
```

Assert manifest/version, exact skill set, `description: Use when`, env variables, package docs and at least eight eval scenarios.

- [ ] **Step 2: Run test and verify RED**

Run: `cd plugins/yandex-wordstat && python -m unittest tests.test_plugin_layout -v`
Expected: FAIL because plugin package does not exist.

- [ ] **Step 3: Add minimal package/discovery files**

Create manifests/docs/evals and minimal skill bodies sufficient for discovery. Defer production workflow assertions to Task 6.

- [ ] **Step 4: Run layout test and verify GREEN**

Run same unittest command; expect PASS.

---

### Task 2: Shared HTTP/auth and generic Cloud Wordstat API helper

**Files:**
- Create: `plugins/yandex-wordstat/scripts/__init__.py`
- Create: `plugins/yandex-wordstat/scripts/_http.py`
- Create: `plugins/yandex-wordstat/scripts/ywstat_api.py`
- Test: `plugins/yandex-wordstat/tests/test_ywstat_api.py`

**Interfaces:**
- `_http.auth_headers(*, api_key=None, iam_token=None) -> dict[str, str]`
- `_http.redact_headers(headers) -> dict[str, str]`
- `_http.request_json(method, url, headers, body=None, transport=None) -> object`
- `ywstat_api.validate_folder_id(folder_id: str | None) -> str | None`
- `ywstat_api.build_request(method: str, payload: dict, *, api_key=None, iam_token=None, folder_id=None) -> dict`
- `ywstat_api.execute_request(request, transport=None) -> object`
- `ywstat_api.estimate_cost(request_counts, prices=None) -> dict`
- `ywstat_api.plan_quota(request_counts, hourly_budget=90) -> dict`

- [ ] **Step 1: Write RED tests**

Cover API-Key/Bearer headers, mutual exclusivity, redaction, optional folder ID, `len>50` rejection, endpoint mapping for `top|dynamics|regions|regions_tree`, cost math and one-hour quota fit/overflow.

- [ ] **Step 2: Verify RED**

Run: `cd plugins/yandex-wordstat && python -m unittest tests.test_ywstat_api -v`
Expected: module import failure.

- [ ] **Step 3: Implement minimal standard-library helper**

Use base `https://searchapi.api.cloud.yandex.net/v2/wordstat/` and mappings:

```python
ENDPOINTS = {
    "top": "topRequests",
    "dynamics": "dynamics",
    "regions": "regions",
    "regions_tree": "getRegionsTree",
}
```

Pricing defaults are `{top:20, dynamics:20, regions:50, regions_tree:0}` RUB/1000 and include `verified_at="2026-09-01"` in estimator output.

- [ ] **Step 4: Verify GREEN**

Run same tests; expect PASS.

---

### Task 3: GetTop normalization and provenance-aware semantics

**Files:**
- Create: `plugins/yandex-wordstat/scripts/ywstat_top.py`
- Create: `plugins/yandex-wordstat/scripts/ywstat_semantics.py`
- Test: `plugins/yandex-wordstat/tests/test_ywstat_top.py`
- Test: `plugins/yandex-wordstat/tests/test_ywstat_semantics.py`

**Interfaces:**
- `ywstat_top.build_top_payload(phrase, *, num_phrases=50, regions=None, devices=None, folder_id=None) -> dict`
- `ywstat_top.normalize_top_response(response, *, seed, operator_expression=None) -> dict`
- `ywstat_semantics.merge_records(records: list[dict]) -> list[dict]`
- `ywstat_semantics.build_dataset(seed_results: list[dict], *, backend="yandex-cloud-wordstat-v2") -> dict`
- `ywstat_semantics.assert_no_fake_total_demand(label: str) -> None`

- [ ] **Step 1: Write RED tests**

Assert phrase length <=400, num phrases 1..2000, max 100 regions, max 3 devices; parse `totalCount`, `count` strings; normalize `results` as `nested`, `associations` as `association`; merge duplicate phrase provenance across seeds and relation types; reject aggregate labels such as `total demand`, `market size`, `unique searches`.

- [ ] **Step 2: Verify RED**

Run both modules; expect missing implementations.

- [ ] **Step 3: Implement normalization/merge**

Canonical merged record:

```python
{
    "phrase": phrase,
    "count": max_seen_count,
    "relations": sorted(unique_relations),
    "sources": sorted(unique_seeds),
    "operator_expressions": sorted(unique_non_null_expressions),
}
```

Do not add `sum_counts` or `total_demand` fields.

- [ ] **Step 4: Verify GREEN**

Run both modules; expect PASS.

---

### Task 4: Dynamics, operators and robust trend classification

**Files:**
- Create: `plugins/yandex-wordstat/scripts/ywstat_dynamics.py`
- Create: `plugins/yandex-wordstat/scripts/ywstat_trends.py`
- Test: `plugins/yandex-wordstat/tests/test_ywstat_dynamics.py`
- Test: `plugins/yandex-wordstat/tests/test_ywstat_trends.py`

**Interfaces:**
- `ywstat_dynamics.build_dynamics_payload(phrase, *, period, from_date, to_date, regions=None, devices=None, folder_id=None) -> dict`
- `ywstat_dynamics.validate_expression_for_period(phrase, period) -> None`
- `ywstat_dynamics.normalize_series(response) -> list[dict]`
- `ywstat_trends.classify_trend(points, *, absolute_floor=100, growing_pct=50, explosive_pct=200, seasonal_tolerance_pct=25) -> dict`

- [ ] **Step 1: Write RED tests**

Verify REST camelCase `fromDate`/`toDate`; allowed periods only `PERIOD_MONTHLY|PERIOD_WEEKLY`; reject `!`, quotes, `[]`, `()`, `|`, `-` for Cloud monthly/weekly dynamics while allowing ordinary phrases and `+`; parse numeric strings; classify low-volume 2->20 as `LOW_VOLUME_NOISE`, 1000->1700 as `GROWING`, 1000->3500 as `EXPLOSIVE`, flat series as `STABLE`, and matching same-month prior-year spike as `SEASONAL`.

- [ ] **Step 2: Verify RED**

Run both modules; expect FAIL.

- [ ] **Step 3: Implement pure analysis**

Use median of up to three points immediately preceding latest as baseline. Growth percentage is explicit in result. Seasonality takes precedence over growth when latest month has a prior-year same-month value within configured tolerance of latest and that prior value was itself above its local baseline.

- [ ] **Step 4: Verify GREEN**

Run both modules; expect PASS.

---

### Task 5: Regional distribution and region-tree utilities

**Files:**
- Create: `plugins/yandex-wordstat/scripts/ywstat_regions.py`
- Test: `plugins/yandex-wordstat/tests/test_ywstat_regions.py`

**Interfaces:**
- `build_regions_payload(phrase, *, region="REGION_ALL", devices=None, folder_id=None) -> dict`
- `normalize_regions(response) -> list[dict]`
- `flatten_region_tree(response) -> list[dict]`
- `search_regions(response, query: str) -> list[dict]`
- `rank_regions(records, *, by="volume", limit=None) -> list[dict]`

- [ ] **Step 1: Write RED tests**

Cover region enum validation, numeric parsing for count/share/affinityIndex, recursive tree flattening, case-insensitive label search and different rankings for volume vs affinity.

- [ ] **Step 2: Verify RED**

Run `python -m unittest tests.test_ywstat_regions -v`; expect FAIL.

- [ ] **Step 3: Implement utilities**

Do not maintain hard-coded region ID/name tables; use API tree data.

- [ ] **Step 4: Verify GREEN**

Run test; expect PASS.

---

### Task 6: Production skills, current references and eval methodology

**Files:**
- Modify: all nine `plugins/yandex-wordstat/skills/*/SKILL.md`
- Create: `plugins/yandex-wordstat/references/api-2026.md`
- Create: `plugins/yandex-wordstat/references/auth.md`
- Create: `plugins/yandex-wordstat/references/operators.md`
- Create: `plugins/yandex-wordstat/references/semantics.md`
- Create: `plugins/yandex-wordstat/references/dynamics.md`
- Create: `plugins/yandex-wordstat/references/regions.md`
- Create: `plugins/yandex-wordstat/references/trends.md`
- Create: `plugins/yandex-wordstat/references/quota-pricing.md`
- Create: `plugins/yandex-wordstat/references/safety.md`
- Create: `plugins/yandex-wordstat/references/sources.md`
- Modify: `plugins/yandex-wordstat/tests/test_plugin_layout.py`

**Interfaces:**
- Router explicitly routes to all specialized skills.
- Research/semantics skills contain no-fake-total-demand invariant and file-output guidance.
- Dynamics/operators document Cloud monthly/weekly operator restriction.
- API/research document quota + cost preview.
- Trends document threshold disclosure and low-volume/seasonality guards.

- [ ] **Step 1: Add failing production-contract assertions**

Assert reference set exactly matches the ten files above; router contains all skill names; semantic skill contains `total demand` warning; dynamics contains `PERIOD_MONTHLY`, `PERIOD_WEEKLY`, `fromDate`, `toDate`; trends contains all five classifications; API/research contains `90`, `100`, and cost preview.

- [ ] **Step 2: Verify RED**

Run layout tests; expect failures against minimal skill bodies.

- [ ] **Step 3: Write production skills/references**

Every skill includes purpose, workflow, stop conditions, execution fallback and references. Sources attribute Axel Freeman, mkultraaaa and YaAll and state official docs are source of truth.

- [ ] **Step 4: Verify GREEN**

Run plugin tests and validator-related JSON parsing; expect PASS.

---

### Task 7: Marketplace, docs and path-aware CI integration

**Files:**
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md`
- Modify: `docs/SERVICE_MATRIX.md`
- Modify: `docs/ROADMAP.md`
- Modify: `tests/test_marketplace_layout.py`

**Interfaces:**
- Marketplace adds `./plugins/yandex-wordstat` version `1.0.0` category `SEO`.
- `changes` job exposes `wordstat` output and detects `plugins/yandex-wordstat/` plus shared paths.
- `wordstat` job runs plugin tests and compiles all seven helpers plus `_http.py`.

- [ ] **Step 1: Write RED root tests**

Expect four marketplace plugin paths; `wordstat:` CI job; service matrix row `Yandex Wordstat | 1 | **available** | 1.0.0`; roadmap Phase 4 implemented and Phase 5 Yandex Search next.

- [ ] **Step 2: Verify RED**

Run root tests; expect failures because Wordstat is not integrated.

- [ ] **Step 3: Update root metadata/docs/CI**

Keep all existing plugin jobs unchanged except adding Wordstat output/detection/job.

- [ ] **Step 4: Full verification gate**

Run:

```bash
python -m unittest discover -s tests -v
python scripts/validate_repo.py
(cd plugins/yandex-direct && python -m unittest discover -s tests -v)
(cd plugins/yandex-metrika && python -m unittest discover -s tests -v)
(cd plugins/yandex-webmaster && python -m unittest discover -s tests -v)
(cd plugins/yandex-wordstat && python -m unittest discover -s tests -v)
python -m py_compile \
  plugins/yandex-wordstat/scripts/_http.py \
  plugins/yandex-wordstat/scripts/ywstat_api.py \
  plugins/yandex-wordstat/scripts/ywstat_top.py \
  plugins/yandex-wordstat/scripts/ywstat_semantics.py \
  plugins/yandex-wordstat/scripts/ywstat_dynamics.py \
  plugins/yandex-wordstat/scripts/ywstat_regions.py \
  plugins/yandex-wordstat/scripts/ywstat_trends.py
```

Also parse every JSON manifest/eval and compare Direct/Metrika/Webmaster directory hashes against the Phase 3 baseline.

- [ ] **Step 5: Publish feature branch and open stacked PR**

Compare `phase-3-yandex-webmaster...phase-4-yandex-wordstat`; assert no changed file lives under previous plugin directories. Open PR to `phase-3-yandex-webmaster` with verification evidence and API baseline.
