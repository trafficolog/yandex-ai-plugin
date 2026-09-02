# Phase 7 — Topical Architecture & Semantic Cocoons Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an evidence-first Wordstat topic-map capability and SEO topical-architecture/internal-linking capabilities while preserving Search ownership of SERP clustering and existing cross-service safety boundaries.

**Architecture:** Wordstat produces a deterministic `wordstat-topic-map/v1` bundle from observed Wordstat evidence plus explicitly supplied candidate assignments. Search remains the owner of SERP-overlap clustering. SEO validates and assembles a `seo-topical-architecture/v1` bundle with separate structural-tree and semantic-graph contracts, then derives preview-only internal-link plans and audits. No new transport or credentials are added to SEO.

**Tech Stack:** Python 3 standard library, `unittest`, Markdown skills/references, JSON eval fixtures, existing repository validators and GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-02-phase-7-topical-architecture-semantic-cocoons-design.md`

## Global Constraints

- `yandex-wordstat` target version: `1.1.0`.
- `yandex-seo` target version: `1.1.0`.
- `yandex-search` remains `1.0.2`; all other plugin SemVer remains unchanged.
- Repository release tag: `phase-7-topical-architecture-1.0.0`.
- Wordstat must not emit final page, canonical-parent, internal-link, or completed-cocoon claims.
- Search remains the only owner of SERP-overlap clustering; Phase 7 must not create a second clustering algorithm.
- SEO remains transport-free and read-only; no cross-service HTTP clients or credentials are introduced.
- Every architectural recommendation retains provenance, evidence class, confidence class, and limitations.
- `METHODOLOGY` and `HYPOTHESIS` claims must never be silently upgraded to `OBSERVED` or `DERIVED`.
- No universal thresholds for Jaccard, overlap, demand, tree depth, content length, or internal-link count.

---

### Task 1: Wordstat Topic Map contract

**Files:**
- Create: `plugins/yandex-wordstat/scripts/ywstat_topic_map.py`
- Create: `plugins/yandex-wordstat/tests/test_ywstat_topic_map.py`
- Create: `plugins/yandex-wordstat/skills/yandex-wordstat-topic-map/SKILL.md`
- Create: `plugins/yandex-wordstat/references/topic-map.md`
- Modify: `plugins/yandex-wordstat/skills/yandex-wordstat/SKILL.md`
- Modify: `plugins/yandex-wordstat/skills/yandex-wordstat-semantics/SKILL.md`
- Modify: `plugins/yandex-wordstat/evals/scenarios.json`
- Modify: `plugins/yandex-wordstat/tests/test_plugin_layout.py`

**Interfaces:**
- Produces: `build_topic_map(*, seeds, phrase_records, candidate_topics, candidate_relations=None, scope=None, limitations=None) -> dict`.
- Produces schema `wordstat-topic-map/v1` with `seeds`, deduplicated `queries`, `candidate_topics`, `candidate_relations`, and `limitations`.
- Candidate topic records require `topic_id`, `label`, `query_ids`, `candidate_intents`, `reasons`, `confidence` (`LOW|MEDIUM|HIGH`) and emit `status="CANDIDATE"`.
- Candidate relations require known topic IDs and relation `RELATED|NARROWER|BROADER|COMPLEMENTARY`; emit `status="HYPOTHESIS"`.

- [ ] **Step 1: Write failing contract tests**

Add tests that require: case/space-normalized query deduplication while preserving all `source_seeds` and relation types; rejection of unknown query IDs/topic IDs; no summing of overlapping demand observations; propagation of `WORDSTAT_ASSOCIATIONS_CAPPED`; candidate-only status; and absence of page/link fields.

```python
from scripts.ywstat_topic_map import build_topic_map


def test_topic_map_preserves_provenance_and_candidate_boundary():
    result = build_topic_map(
        seeds=[{"seed": "seo", "operators": "", "filters": {}, "coverage": {"associations_truncated": True}}],
        phrase_records=[
            {"query_id": "q1", "text": "SEO аудит", "source_seed": "seo", "relation": "nested", "demand": {"count": 100}},
            {"query_id": "q2", "text": " seo аудит ", "source_seed": "аудит сайта", "relation": "association", "demand": {"count": 80}},
        ],
        candidate_topics=[{
            "topic_id": "audit", "label": "SEO-аудит", "query_ids": ["q1", "q2"],
            "candidate_intents": ["informational"], "reasons": ["WORDSTAT_NESTED_RELATION"],
            "confidence": "MEDIUM"
        }],
    )
    assert result["schema"] == "wordstat-topic-map/v1"
    assert len(result["queries"]) == 1
    assert set(result["queries"][0]["source_seeds"]) == {"seo", "аудит сайта"}
    assert set(result["queries"][0]["relations"]) == {"nested", "association"}
    assert len(result["queries"][0]["demand_observations"]) == 2
    assert "WORDSTAT_ASSOCIATIONS_CAPPED" in result["limitations"]
    assert result["candidate_topics"][0]["status"] == "CANDIDATE"
    assert "page" not in result["candidate_topics"][0]
```

- [ ] **Step 2: Run Wordstat tests and verify RED**

Run: `python -m unittest discover -s plugins/yandex-wordstat/tests -v`
Expected: FAIL because `scripts.ywstat_topic_map` and the new skill do not exist.

- [ ] **Step 3: Implement the deterministic builder**

Implement query normalization/deduplication, provenance merging, enum validation, candidate-reference validation, limitation propagation, and schema assembly. Do not infer candidate groups from fuzzy text and do not aggregate demand observations into a total.

- [ ] **Step 4: Add skill/reference/eval routing**

Document that the skill prepares pre-SERP candidate topic maps only, routes final page-boundary work to Search + SEO, and keeps methodology separate from observed Wordstat evidence. Add at least three eval scenarios: multi-seed provenance, capped associations, and refusal to call Wordstat relations final page clusters.

- [ ] **Step 5: Run Wordstat tests and compile helpers**

Run: `python -m unittest discover -s plugins/yandex-wordstat/tests -v`
Run: `python -m py_compile plugins/yandex-wordstat/scripts/*.py`
Expected: PASS.

- [ ] **Step 6: Commit**

Commit message: `feat(wordstat): add candidate topic map contract`

---

### Task 2: SEO Topical Architecture validator/builder

**Files:**
- Create: `plugins/yandex-seo/scripts/seo_topical_architecture.py`
- Create: `plugins/yandex-seo/tests/test_seo_topical_architecture.py`
- Create: `plugins/yandex-seo/skills/yandex-seo-topical-architecture/SKILL.md`
- Create: `plugins/yandex-seo/references/topical-architecture.md`
- Modify: `plugins/yandex-seo/skills/yandex-seo/SKILL.md`
- Modify: `plugins/yandex-seo/skills/yandex-seo-clusters/SKILL.md`
- Modify: `plugins/yandex-seo/evals/scenarios.json`
- Modify: `plugins/yandex-seo/tests/test_plugin_layout.py`

**Interfaces:**
- Produces: `build_topical_architecture(*, mode, coverage, clusters, page_decisions, structural_nodes, semantic_edges, fact_sets=None, limitations=None) -> dict`.
- Allowed modes: `GREENFIELD|EXISTING_SITE`.
- Allowed page decisions: `PRESERVE|CREATE|EXPAND|MERGE|SPLIT|REDIRECT|SECTION_ONLY|BRIDGE|NO_PAGE|MANUAL_REVIEW`.
- Allowed claim classes: `OBSERVED|DERIVED|HYPOTHESIS|METHODOLOGY`.
- Allowed confidence classes: `LOW|MEDIUM|HIGH`.
- Structural nodes have unique `page_id`, optional unique URL/proposed URL, at most one `canonical_parent_id`, and no cycles.
- Semantic edges reference known pages and one of the spec relation types.

- [ ] **Step 1: Write failing architecture tests**

Cover: valid greenfield bundle; `SERP_VALIDATION_MISSING` when Search coverage is `MISSING`; duplicate proposed URL rejection; unknown parent rejection; structural cycle rejection; semantic edge unknown page rejection; invalid claim-class rejection; methodology-only edge remains `METHODOLOGY`; existing-site decisions preserve evidence and mode.

```python
from scripts.seo_topical_architecture import build_topical_architecture


def test_missing_search_keeps_page_boundaries_hypothetical():
    result = build_topical_architecture(
        mode="GREENFIELD",
        coverage={"wordstat": "COMPLETE", "search": "MISSING", "webmaster": "MISSING", "metrika": "MISSING", "site_inventory": "MISSING"},
        clusters=[],
        page_decisions=[{"page_id": "p1", "decision": "CREATE", "cluster_ids": ["c1"], "evidence": [], "confidence": "LOW", "claim_class": "HYPOTHESIS"}],
        structural_nodes=[{"page_id": "p1", "proposed_url": "/seo/", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": ["c1"], "evidence": [], "confidence": "LOW"}],
        semantic_edges=[],
    )
    assert "SERP_VALIDATION_MISSING" in result["limitations"]
```

- [ ] **Step 2: Run SEO tests and verify RED**

Run: `python -m unittest discover -s plugins/yandex-seo/tests -v`
Expected: FAIL because the architecture module/skill are missing.

- [ ] **Step 3: Implement minimal schema validation and graph integrity**

Implement deterministic validators for enums, unique IDs/URLs, parent existence, cycle detection, semantic-edge references, fact-set canonical owner references, and limitation injection. Do not choose a page split/merge automatically; validate decisions supplied by the orchestration layer.

- [ ] **Step 4: Add skill/reference/evals**

Document evidence priority: explicit business constraints → Search clusters → existing-site Webmaster/Metrika/inventory evidence → Wordstat demand context → semantic hypothesis → manual review. Add evals for greenfield without Search, existing-site preserve/merge, cycle rejection, and methodology-vs-observed separation.

- [ ] **Step 5: Run SEO tests/compile**

Run: `python -m unittest discover -s plugins/yandex-seo/tests -v`
Run: `python -m py_compile plugins/yandex-seo/scripts/*.py`
Expected: PASS.

- [ ] **Step 6: Commit**

Commit message: `feat(seo): add topical architecture contract`

---

### Task 3: SEO Internal Linking design/audit

**Files:**
- Create: `plugins/yandex-seo/scripts/seo_internal_linking.py`
- Create: `plugins/yandex-seo/tests/test_seo_internal_linking.py`
- Create: `plugins/yandex-seo/skills/yandex-seo-internal-linking/SKILL.md`
- Create: `plugins/yandex-seo/references/internal-linking.md`
- Modify: `plugins/yandex-seo/evals/scenarios.json`

**Interfaces:**
- Produces: `build_link_plan(*, architecture, candidate_links) -> list[dict]`.
- Produces: `audit_link_inventory(*, architecture, existing_links) -> dict`.
- Candidate links require known source/target pages, allowed relation, non-empty `user_need`, `reason_codes`, `evidence`, confidence, and claim class.
- Audit emits deterministic findings such as `ORPHAN_PAGE`, `MISSING_JUSTIFIED_LINK`, `STRUCTURAL_PARENT_LINK_MISSING`, `UNKNOWN_LINK_ENDPOINT`; graph cycles are not errors by themselves.

- [ ] **Step 1: Write failing internal-link tests**

Test unknown endpoints, methodology-only link labeling, refusal of forced exact-match anchor requirements, orphan detection, missing canonical-parent link detection, and acceptance of benign semantic cycles.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest plugins/yandex-seo/tests/test_seo_internal_linking.py -v`
Expected: FAIL because the module is missing.

- [ ] **Step 3: Implement preview-only link plan and deterministic audit**

The builder validates and normalizes candidate links; it does not invent universal counts/anchors. The audit compares known architecture nodes/edges with supplied existing links and reports only contract-supported gaps.

- [ ] **Step 4: Add skill/reference/evals and run full SEO suite**

Run: `python -m unittest discover -s plugins/yandex-seo/tests -v`
Run: `python -m py_compile plugins/yandex-seo/scripts/*.py`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `feat(seo): add evidence-first internal linking workflow`

---

### Task 4: Cross-plugin contracts and documentation

**Files:**
- Modify: `docs/CONTRACT_MATRIX.json`
- Modify: `docs/SERVICE_MATRIX.md`
- Modify: `docs/SERVICE_MATRIX.en.md`
- Modify: `plugins/yandex-wordstat/README.md`
- Modify: `plugins/yandex-wordstat/README.en.md`
- Modify: `plugins/yandex-seo/README.md`
- Modify: `plugins/yandex-seo/README.en.md`
- Modify: root `README.md`
- Modify: root `README.en.md`
- Test: `tests/test_contract_controls.py`
- Test: `tests/test_bilingual_docs.py`

**Interfaces:**
- Add implemented contract IDs: `wordstat.topic-map-candidate-boundary`, `seo.topical-architecture-structural-tree`, `seo.topical-architecture-evidence-classes`, `seo.internal-linking-preview-only`.
- Matrix entries must point at real skill/helper/test paths and preserve Search clustering ownership.

- [ ] **Step 1: Add failing repository contract assertions**

Require the four IDs, real paths, bilingual README references, and explicit statements that Wordstat is candidate-only and Search owns SERP clustering.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL on missing Phase 7 contracts/docs.

- [ ] **Step 3: Update matrix and bilingual docs**

Explain the complete pipeline `Wordstat Topic Map → Search SERP Validation → SEO Topical Architecture → Internal Linking`, greenfield/existing-site modes, evidence classes, and methodology limitations.

- [ ] **Step 4: Verify GREEN**

Run: `python scripts/validate_repo.py`
Run: `python -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `docs: document Phase 7 topical architecture contracts`

---

### Task 5: Independent SemVer and release integration

**Files:**
- Modify Wordstat `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `CHANGELOG.md`, `CHANGELOG.en.md`, layout tests.
- Modify SEO `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `CHANGELOG.md`, `CHANGELOG.en.md`, layout tests.
- Modify `.agents/plugins/marketplace.json` and `.claude-plugin/marketplace.json`.
- Modify root `README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`.
- Create: `.github/workflows/publish-phase-7-topical-architecture.yml`.
- Modify root release/version regression tests.

**Interfaces:**
- Wordstat `1.1.0`; SEO `1.1.0`; Search `1.0.2`; Direct `1.0.1`; Metrika `1.0.2`; Webmaster `1.0.3`; Marketing `1.1.0`.
- Publisher creates `phase-7-topical-architecture-1.0.0`, `yandex-wordstat-v1.1.0`, and `yandex-seo-v1.1.0` only after successful `main` CI, targeting the exact merged commit.

- [ ] **Step 1: Write/update version assertions first**

Update tests to require the exact mixed-version matrix and bilingual changelog entries before changing manifests.

- [ ] **Step 2: Verify version RED**

Run repository + Wordstat + SEO tests; expect failures on old `1.0.2`/`1.0.1` versions.

- [ ] **Step 3: Update manifests/marketplaces/changelogs and publisher**

Release notes must describe new capabilities without claiming runtime Search changes or ranking guarantees.

- [ ] **Step 4: Verify all local repository suites**

Run:
`python scripts/validate_repo.py`
`python -m unittest discover -s tests -v`
`python -m unittest discover -s plugins/yandex-wordstat/tests -v`
`python -m unittest discover -s plugins/yandex-seo/tests -v`
`python -m py_compile plugins/yandex-wordstat/scripts/*.py plugins/yandex-seo/scripts/*.py`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `release: prepare Phase 7 topical architecture`

---

### Task 6: PR, full CI, merge, post-merge verification and releases

**Files:** no runtime files unless CI/review finds a defect.

- [ ] **Step 1: Compare branch with base and open non-draft PR**

PR title: `feat: add Phase 7 topical architecture and semantic cocoons`
PR body must reference #23, approved spec/plan, exact version matrix, evidence boundaries, and release tags.

- [ ] **Step 2: Require exact-head full CI**

Accept only a run where validator/repository tests and all seven plugin jobs are successful on the exact PR head SHA.

- [ ] **Step 3: Inspect reviews/comments/threads and compare surface**

Resolve every substantive thread and rerun exact-head CI after any code change.

- [ ] **Step 4: Squash merge with expected-head guard**

Merge only if PR remains mergeable and `main` has not advanced incompatibly.

- [ ] **Step 5: Verify post-merge `main` CI**

Require the full 9-job CI to pass on the actual squash commit in `main`.

- [ ] **Step 6: Verify publisher and tag targets**

Require successful publisher workflow and confirm all three GitHub releases/tags are non-draft/non-prerelease and target the exact Phase 7 merge SHA.

- [ ] **Step 7: Close issue #23 as completed**

Only after post-merge CI and release verification.

## Plan self-review

- Spec coverage: Wordstat topic map, Search ownership, SEO architecture, internal linking, greenfield/existing-site modes, structural tree, semantic graph, consistency fact sets, evidence classes, cannibalization reuse, methodology restrictions, evals, contracts, bilingual docs, SemVer and release gates are all mapped to tasks.
- Placeholder scan: no TBD/TODO/"implement later" steps remain.
- Type consistency: `wordstat-topic-map/v1` and `seo-topical-architecture/v1` names, confidence/evidence enums, page decisions and relation ownership match the approved spec.
