# Phase 7 Post-Release Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the four deferred Phase 7 P2 findings from #27 without changing service ownership or adding new semantic-cocoon features.

**Architecture:** Keep Wordstat candidate-only and SEO transport-free. Harden only deterministic normalization/validation boundaries: structural-node field whitelisting, link evidence typing, candidate-topic self-relation rejection, and duplicate seed rejection. Publish the fixes as patch releases for Wordstat and SEO plus a repository Phase 7 patch release.

**Tech Stack:** Python 3.13, `unittest`, GitHub Actions, JSON plugin manifests/marketplaces, Markdown bilingual docs.

**Spec:** `docs/superpowers/specs/2026-09-02-phase-7-topical-architecture-semantic-cocoons-design.md`; follow-up tracker: GitHub issue #27.

## Global Constraints

- Wordstat remains candidate-only; it does not claim final page boundaries, internal links, or completed semantic cocoons.
- Search remains the sole owner of real SERP-overlap/Jaccard clustering and stays at `1.0.2`.
- SEO remains transport-free and preview-only; no Yandex HTTP clients, credentials, or CMS writes are introduced.
- Preserve `OBSERVED`, `DERIVED`, `HYPOTHESIS`, `METHODOLOGY` semantics and all existing Phase 7 reason-code/coverage invariants.
- Do not include legacy OPUS publisher issue #28 in this patch.
- Patch SemVer target: Wordstat `1.1.1`, SEO `1.1.1`, repository `phase-7-topical-architecture-1.0.1`.

---

### Task 1: Strip execution state from structural page records

**Files:**
- Modify: `plugins/yandex-seo/scripts/seo_topical_architecture.py`
- Test: `plugins/yandex-seo/tests/test_phase7_post_release_hardening.py`
- Modify after GREEN: `plugins/yandex-seo/references/topical-architecture.md`

**Interfaces:**
- Consumes: `build_topical_architecture(... structural_nodes=[...])`.
- Produces: `structural_tree.nodes[]` containing only structural contract fields.

- [ ] **Step 1: Write the failing regression**

Create `plugins/yandex-seo/tests/test_phase7_post_release_hardening.py` with a reusable complete coverage fixture and a test that passes a structural node containing `title`, `decision: REDIRECT`, `status: EXECUTED`, `write: true`, and `execution_id`. Assert that the normalized node preserves `title` but omits `decision`, `status`, `write`, and `execution_id`.

```python
import unittest
from scripts import seo_topical_architecture

COVERAGE = {
    "wordstat": "COMPLETE",
    "search": "COMPLETE",
    "webmaster": "MISSING",
    "metrika": "MISSING",
    "site_inventory": "MISSING",
}

class TestPhase7PostReleaseHardening(unittest.TestCase):
    def test_structural_nodes_strip_execution_and_decision_state(self):
        result = seo_topical_architecture.build_topical_architecture(
            mode="GREENFIELD",
            coverage=COVERAGE,
            clusters=[],
            page_decisions=[],
            structural_nodes=[{
                "page_id": "p1",
                "proposed_url": "/topic/",
                "title": "Topic",
                "page_role": "ROOT",
                "canonical_parent_id": None,
                "breadcrumbs": [],
                "cluster_ids": [],
                "evidence": [],
                "confidence": "LOW",
                "decision": "REDIRECT",
                "status": "EXECUTED",
                "write": True,
                "execution_id": "exec-1",
            }],
            semantic_edges=[],
        )
        node = result["structural_tree"]["nodes"][0]
        self.assertEqual(node["title"], "Topic")
        for forbidden in ("decision", "status", "write", "execution_id"):
            self.assertNotIn(forbidden, node)
```

- [ ] **Step 2: Verify RED**

Run the SEO plugin suite through CI or locally with:

```bash
cd plugins/yandex-seo && python -m unittest discover -s tests -v
```

Expected: the new test fails because the current `deepcopy(raw)` retains execution/recommendation fields.

- [ ] **Step 3: Implement the minimal structural whitelist**

In `seo_topical_architecture.py`, introduce:

```python
STRUCTURAL_NODE_FIELDS = {
    "page_id",
    "url",
    "proposed_url",
    "title",
    "page_role",
    "canonical_parent_id",
    "breadcrumbs",
    "cluster_ids",
    "evidence",
    "confidence",
}
```

Replace `node = deepcopy(raw)` with a whitelist copy:

```python
node = {
    key: deepcopy(raw[key])
    for key in STRUCTURAL_NODE_FIELDS
    if key in raw
}
```

Keep the existing normalization/default/cycle/breadcrumb validation unchanged.

- [ ] **Step 4: Verify GREEN**

Run the full SEO plugin suite and repository CI. Expected: new regression passes and no existing structural-tree tests regress.

- [ ] **Step 5: Document the contract**

Update `plugins/yandex-seo/references/topical-architecture.md` to state that structural nodes use an explicit field whitelist and cannot carry decision/execution/write state; page decisions remain the only recommendation-state surface.

---

### Task 2: Require list-typed link-plan evidence

**Files:**
- Modify: `plugins/yandex-seo/scripts/seo_internal_linking.py`
- Test: `plugins/yandex-seo/tests/test_phase7_post_release_hardening.py`
- Modify after GREEN: `plugins/yandex-seo/references/internal-linking.md`

**Interfaces:**
- Consumes: `build_link_plan(architecture=..., candidate_links=[...])`.
- Produces: preview links where `evidence` is always a list.

- [ ] **Step 1: Write the failing regression**

Add two subtests that use an otherwise valid candidate link and supply `evidence="cluster:c1"` and `evidence={"source": "c1"}`. Both must raise `ValueError`.

```python
    def test_link_plan_rejects_non_list_evidence(self):
        architecture = seo_topical_architecture.build_topical_architecture(
            mode="GREENFIELD",
            coverage=COVERAGE,
            clusters=[],
            page_decisions=[],
            structural_nodes=[
                {"page_id": "p1", "proposed_url": "/a/", "page_role": "ROOT", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"},
                {"page_id": "p2", "proposed_url": "/b/", "page_role": "ROOT", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"},
            ],
            semantic_edges=[],
        )
        base = {
            "from_page_id": "p1",
            "to_page_id": "p2",
            "relation": "SUPPORT",
            "user_need": "Read supporting detail",
            "reason_codes": ["SEMANTIC_HYPOTHESIS"],
            "confidence": "LOW",
            "claim_class": "HYPOTHESIS",
        }
        for malformed in ("cluster:c1", {"source": "c1"}):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                seo_internal_linking.build_link_plan(
                    architecture=architecture,
                    candidate_links=[{**base, "evidence": malformed}],
                )
```

- [ ] **Step 2: Verify RED**

Expected: both subtests fail because `_normalize_candidate_link()` currently deep-copies arbitrary evidence.

- [ ] **Step 3: Implement minimal evidence typing**

Before constructing `item`, add:

```python
evidence = raw.get("evidence", [])
if not isinstance(evidence, list):
    raise ValueError("candidate link evidence must be a list")
```

Then serialize `deepcopy(evidence)`.

- [ ] **Step 4: Verify GREEN**

Run all SEO tests and repository CI. Existing valid list evidence remains accepted.

- [ ] **Step 5: Document the contract**

Update `plugins/yandex-seo/references/internal-linking.md`: `evidence` is list-typed and scalar/object payloads are rejected before serialization.

---

### Task 3: Reject candidate-topic self relations

**Files:**
- Modify: `plugins/yandex-wordstat/scripts/ywstat_topic_map.py`
- Test: `plugins/yandex-wordstat/tests/test_phase7_post_release_hardening.py`
- Modify after GREEN: `plugins/yandex-wordstat/references/topic-map.md`

**Interfaces:**
- Consumes: `candidate_relations[]`.
- Produces: candidate topic graph edges with distinct endpoints.

- [ ] **Step 1: Write the failing regression**

Create `plugins/yandex-wordstat/tests/test_phase7_post_release_hardening.py` and assert a relation `t1 -> t1` raises `ValueError`, while a normal `t1 -> t2` relation remains valid.

```python
import unittest
from scripts import ywstat_topic_map

class TestPhase7PostReleaseHardening(unittest.TestCase):
    def test_candidate_topic_relation_rejects_self_edge(self):
        with self.assertRaises(ValueError):
            ywstat_topic_map.build_topic_map(
                seeds=[{"seed": "seo"}],
                phrase_records=[],
                candidate_topics=[{
                    "topic_id": "t1",
                    "label": "SEO",
                    "query_ids": [],
                    "confidence": "LOW",
                }],
                candidate_relations=[{
                    "from_topic_id": "t1",
                    "to_topic_id": "t1",
                    "relation": "NARROWER",
                    "evidence": [],
                }],
            )
```

- [ ] **Step 2: Verify RED**

Run:

```bash
cd plugins/yandex-wordstat && python -m unittest discover -s tests -v
```

Expected: the new test fails because both endpoints are currently only checked for membership.

- [ ] **Step 3: Implement minimal endpoint guard**

After the known-topic check add:

```python
if source == target:
    raise ValueError("candidate relation source and target must differ")
```

- [ ] **Step 4: Verify GREEN**

Run the full Wordstat suite; existing distinct-topic relation tests must remain green.

- [ ] **Step 5: Document the contract**

Update `plugins/yandex-wordstat/references/topic-map.md`: candidate relations are hypotheses between distinct topics; self-relations are invalid.

---

### Task 4: Reject duplicate Wordstat seed identifiers

**Files:**
- Modify: `plugins/yandex-wordstat/scripts/ywstat_topic_map.py`
- Test: `plugins/yandex-wordstat/tests/test_phase7_post_release_hardening.py`
- Modify after GREEN: `plugins/yandex-wordstat/references/topic-map.md`

**Interfaces:**
- Consumes: `seeds[].seed` and `phrase_records[].source_seed`.
- Produces: unambiguous seed provenance.

- [ ] **Step 1: Write the failing regression**

Add a test with two seed records sharing `seed="seo"` but carrying different operators/coverage; expect `ValueError` before phrase normalization.

```python
    def test_duplicate_seed_identifiers_are_rejected(self):
        with self.assertRaises(ValueError):
            ywstat_topic_map.build_topic_map(
                seeds=[
                    {"seed": "seo", "operators": ["exact"]},
                    {"seed": "seo", "operators": ["broad"]},
                ],
                phrase_records=[],
                candidate_topics=[],
            )
```

- [ ] **Step 2: Verify RED**

Expected: the test fails because the released implementation stores seeds in a set without rejecting duplicates.

- [ ] **Step 3: Implement minimal duplicate rejection**

Inside the seed-validation loop:

```python
if seed_name in declared_seeds:
    raise ValueError(f"duplicate seed identifier: {seed_name}")
declared_seeds.add(seed_name)
```

Do not introduce a new seed-ID schema in this patch.

- [ ] **Step 4: Verify GREEN**

Run the full Wordstat suite and repository CI.

- [ ] **Step 5: Document the contract**

Update `topic-map.md` to state that `seeds[].seed` is unique within one bundle so `source_seed` remains an unambiguous provenance key.

---

### Task 5: Patch SemVer, bilingual docs, and publisher

**Files:**
- Modify: `plugins/yandex-wordstat/.codex-plugin/plugin.json`
- Modify: `plugins/yandex-wordstat/.claude-plugin/plugin.json`
- Modify: `plugins/yandex-seo/.codex-plugin/plugin.json`
- Modify: `plugins/yandex-seo/.claude-plugin/plugin.json`
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `plugins/yandex-wordstat/README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`
- Modify: `plugins/yandex-seo/README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`
- Modify: `README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`
- Modify: `docs/SERVICE_MATRIX.md`, `docs/SERVICE_MATRIX.en.md`
- Modify: `tests/test_bilingual_docs.py`, `tests/test_marketplace_layout.py`
- Create: `.github/workflows/publish-phase-7-topical-architecture-1.0.1.yml`
- Create: `tests/test_phase7_patch_publisher.py`

**Interfaces:**
- Publishes immutable tags only after successful push-triggered CI on `main`.
- Target versions: Wordstat `1.1.1`, SEO `1.1.1`, repository tag `phase-7-topical-architecture-1.0.1`.

- [ ] **Step 1: Add RED release assertions**

Update version tests to require only Wordstat/SEO patch bumps, and add a publisher test requiring exactly these tags:

```text
phase-7-topical-architecture-1.0.1
yandex-wordstat-v1.1.1
yandex-seo-v1.1.1
```

Require the workflow to derive its release target from the successful push CI `workflow_run.head_sha`, require same-repository `push` to `main`, and support complete-set no-op plus partial-set recovery at the common immutable SHA.

- [ ] **Step 2: Verify RED**

Expected: repository tests fail while manifests/marketplaces still advertise `1.1.0` and the patch publisher does not exist.

- [ ] **Step 3: Apply patch versions and bilingual docs**

Set Wordstat and SEO to `1.1.1` in both manifests and both marketplaces. Add matching RU/EN changelog sections describing only the four #27 hardening fixes. Update root/service matrices to the new patch versions; all other plugin versions remain unchanged.

- [ ] **Step 4: Add patch publisher**

Create `.github/workflows/publish-phase-7-topical-architecture-1.0.1.yml` by reusing the Phase 7 immutable-release state machine but changing only the three patch tags/titles/notes. It must be idempotent and recover partial publication at a common ancestor SHA.

- [ ] **Step 5: Verify GREEN**

Run repository validation/tests and all affected Wordstat/SEO plugin tests. Then require full exact-head CI success before merge.

---

### Task 6: PR, merge, post-merge CI, and release verification

**Files:**
- No production-code changes; verification/integration only.

- [ ] **Step 1: Open/update a PR from `fix/phase-7-post-release-hardening` to `main`**

PR body must close #27 only after merge and publication and must explicitly state that #28 is out of scope.

- [ ] **Step 2: Verify exact-head CI and review state**

Require full CI success on the exact PR head and `behind_by=0`. Address substantive review findings only if they concern this four-item hardening scope.

- [ ] **Step 3: Squash merge with expected-head guard**

Use the exact verified PR SHA. Do not force-update the branch or retarget historical Phase 7 tags.

- [ ] **Step 4: Verify post-merge `main` CI**

Require the push-triggered CI on the squash SHA to complete successfully before claiming release readiness.

- [ ] **Step 5: Verify patch publisher and tags**

Require publisher success and confirm all three releases/tags resolve to the exact squash merge SHA:

```text
phase-7-topical-architecture-1.0.1
yandex-wordstat-v1.1.1
yandex-seo-v1.1.1
```

- [ ] **Step 6: Close #27 only after release verification**

Record the merge SHA, main CI run, publisher run, and release URLs in the issue. Keep #28 open for the independent legacy OPUS publisher fix.
