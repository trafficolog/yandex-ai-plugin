# Phase 1 Marketplace Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the existing root-level Yandex Direct plugin into the first independently installable plugin inside a Yandex AI marketplace monorepo without changing Direct runtime behavior.

**Architecture:** Keep repository-level marketplace metadata, CI, standards, and roadmap at the root. Move all Direct-specific manifests, skills, references, helpers, tests, changelog, environment template, and attribution into `plugins/yandex-direct/`. Root validation enforces marketplace/plugin layout and lets future plugins follow the same contract.

**Tech Stack:** GitHub marketplace metadata, OpenAI/Codex plugin manifests, Claude-compatible plugin metadata, Python 3 standard library, unittest, GitHub Actions YAML.

**Spec:** `docs/superpowers/specs/2026-09-01-yandex-ai-marketplace-design.md`

## Global Constraints

- Preserve Yandex Direct plugin version `1.0.0` during structural migration.
- Preserve existing Direct tests and executable behavior.
- Root marketplace must reference `./plugins/yandex-direct`.
- Repository root owns `LICENSE`, root `README.md`, marketplace metadata, architecture/standards docs, CI, roadmap, shared packages, and cross-service workflows.
- Direct-specific `.env.example`, manifests, references, scripts, skills, tests, changelog, README, and third-party notices live under `plugins/yandex-direct/`.
- Every consequential write follows `read → analyze → preview → explicit approval → write → verify`.
- No committed secrets or runtime-specific absolute filesystem paths in skills.
- Shared packages are created only after duplication is proven across two or more plugins.

---

### Task 1: Add migration contract tests before moving files

**Files:**
- Create: `tests/test_marketplace_layout.py`

**Interfaces:**
- Consumes: current repository tree and the target paths from the approved architecture spec.
- Produces: executable structural contract for root marketplace, Direct plugin location, Direct manifest version, skill discovery, and removal of obsolete root Direct manifests.

- [ ] **Step 1: Write the failing structural tests**

Create `tests/test_marketplace_layout.py` with tests that assert:

```python
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "yandex-direct"


class MarketplaceLayoutTests(unittest.TestCase):
    def test_root_marketplace_points_to_direct_plugin(self):
        data = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        direct = next(item for item in data["plugins"] if item["name"] == "yandex-direct-suite")
        self.assertEqual(direct["source"], {"source": "local", "path": "./plugins/yandex-direct"})

    def test_direct_plugin_preserves_version(self):
        data = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(data["version"], "1.0.0")
        self.assertEqual(data["skills"], "./skills/")

    def test_direct_router_and_specialized_skills_moved(self):
        expected = {
            "yandex-direct",
            "yandex-direct-api",
            "yandex-direct-audit",
            "yandex-direct-budget",
            "yandex-direct-create",
            "yandex-direct-keywords",
            "yandex-direct-optimize",
            "yandex-direct-reporting",
        }
        actual = {path.parent.name for path in (PLUGIN / "skills").glob("*/SKILL.md")}
        self.assertEqual(actual, expected)

    def test_obsolete_root_direct_plugin_manifest_is_absent(self):
        self.assertFalse((ROOT / ".codex-plugin/plugin.json").exists())
        self.assertFalse((ROOT / ".claude-plugin/plugin.json").exists())

    def test_direct_plugin_has_required_reference_directories(self):
        for path in ["references", "scripts", "tests", "evals"]:
            self.assertTrue((PLUGIN / path).is_dir(), path)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
python -m unittest tests.test_marketplace_layout -v
```

Expected: failures because `plugins/yandex-direct/` does not exist and root marketplace still points to `./`.

- [ ] **Step 3: Commit only the failing test**

```bash
git add tests/test_marketplace_layout.py
git commit -m "test: define marketplace migration contract"
```

---

### Task 2: Move the Direct implementation into `plugins/yandex-direct`

**Files:**
- Move: `.codex-plugin/plugin.json` → `plugins/yandex-direct/.codex-plugin/plugin.json`
- Move: `.claude-plugin/plugin.json` → `plugins/yandex-direct/.claude-plugin/plugin.json`
- Move: `.env.example` → `plugins/yandex-direct/.env.example`
- Move: `CHANGELOG.md` → `plugins/yandex-direct/CHANGELOG.md`
- Move: `THIRD_PARTY_NOTICES.md` → `plugins/yandex-direct/THIRD_PARTY_NOTICES.md`
- Move: existing Direct `README.md` → `plugins/yandex-direct/README.md`
- Move: `references/` → `plugins/yandex-direct/references/`
- Move: `scripts/` → `plugins/yandex-direct/scripts/`
- Move: `skills/` → `plugins/yandex-direct/skills/`
- Move: existing Direct tests → `plugins/yandex-direct/tests/`
- Create: `plugins/yandex-direct/evals/scenarios.json`
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: root Direct plugin version `1.0.0` and existing Direct runtime code.
- Produces: independently installable plugin at `plugins/yandex-direct/` with unchanged Direct helper APIs and test behavior.

- [ ] **Step 1: Implement the minimal structural move**

Root OpenAI marketplace must become:

```json
{
  "name": "yandex-ai-plugin",
  "interface": {"displayName": "Yandex AI Plugins"},
  "plugins": [
    {
      "name": "yandex-direct-suite",
      "source": {"source": "local", "path": "./plugins/yandex-direct"},
      "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
      "category": "Marketing"
    }
  ]
}
```

Root Claude marketplace must reference `./plugins/yandex-direct` and must not pretend the repository root is itself the Direct plugin.

Create `plugins/yandex-direct/evals/scenarios.json` with at least these offline routing/safety fixtures:

```json
{
  "version": 1,
  "scenarios": [
    {"prompt": "Проведи аудит кампаний Яндекс Директа", "skill": "yandex-direct-audit", "write": false},
    {"prompt": "Создай новую ЕПК до состояния черновика", "skill": "yandex-direct-create", "write": "approval-required"},
    {"prompt": "Сделай отчет по CPA и расходу", "skill": "yandex-direct-reporting", "write": false},
    {"prompt": "Оптимизируй работающие кампании", "skill": "yandex-direct-optimize", "write": "approval-required"},
    {"prompt": "Разбери поисковые запросы и минус-фразы", "skill": "yandex-direct-keywords", "write": "approval-required"},
    {"prompt": "Проверь темп расхода бюджета", "skill": "yandex-direct-budget", "write": false},
    {"prompt": "Собери payload campaigns.update", "skill": "yandex-direct-api", "write": "preview-first"}
  ]
}
```

- [ ] **Step 2: Run the migration contract tests**

```bash
python -m unittest tests.test_marketplace_layout -v
```

Expected: PASS.

- [ ] **Step 3: Run Direct's existing tests from its new working directory**

```bash
cd plugins/yandex-direct
python -m unittest discover -s tests -v
```

Expected: all previously existing Direct tests pass unchanged.

- [ ] **Step 4: Compile Direct helpers**

```bash
python -m py_compile scripts/yd_api.py scripts/yd_report.py
```

Expected: exit code 0.

- [ ] **Step 5: Commit the structural migration**

```bash
git add .agents .claude-plugin plugins/yandex-direct tests
git commit -m "refactor: move Direct into marketplace plugin"
```

---

### Task 3: Add repository-wide plugin standard and service roadmap

**Files:**
- Replace: `README.md`
- Create: `docs/PLUGIN_STANDARD.md`
- Create: `docs/SERVICE_MATRIX.md`
- Create: `docs/ROADMAP.md`
- Create: `workflows/README.md`
- Create: `packages/README.md`

**Interfaces:**
- Consumes: mandatory standard from the architecture spec.
- Produces: documented contract that future Metrika/Webmaster/Wordstat/Search plugins must satisfy.

- [ ] **Step 1: Extend the failing layout test with documentation assertions**

Add tests asserting these files exist and that `PLUGIN_STANDARD.md` contains the exact safety sequence:

```python
self.assertIn(
    "read → analyze → preview → explicit approval → write → verify",
    (ROOT / "docs/PLUGIN_STANDARD.md").read_text(),
)
```

- [ ] **Step 2: Run the test and verify RED**

```bash
python -m unittest tests.test_marketplace_layout -v
```

Expected: failure because standard/roadmap files do not exist yet.

- [ ] **Step 3: Write the root docs**

`docs/PLUGIN_STANDARD.md` must formalize all 18 mandatory requirements from the approved spec, plugin folder conventions, capability matrix fields, safety classes, independent SemVer, source/freshness requirements, eval fixture format, and fallback order `MCP/app → bundled API helper → file/export`.

`docs/SERVICE_MATRIX.md` must list Direct as `1.0.0 / available` and Metrika, Webmaster, Wordstat, Search, Tracker, 360, Maps, AppMetrica, YandexGPT, SpeechKit as planned with their tiers and intended execution sources.

`docs/ROADMAP.md` must describe Phase 1 through Phase 6 and make Metrika the next implementation target.

Root `README.md` must explain that this repository is a marketplace, not a single plugin, show the `plugins/` structure, list current availability, explain installation/import, and link to Direct plugin documentation.

`packages/README.md` must state that shared code is introduced only after proven duplication across at least two plugins.

`workflows/README.md` must state that cross-service workflows orchestrate stable service plugins and do not duplicate API clients.

- [ ] **Step 4: Run structural tests and verify GREEN**

```bash
python -m unittest tests.test_marketplace_layout -v
```

Expected: PASS.

- [ ] **Step 5: Commit documentation foundation**

```bash
git add README.md docs packages workflows tests/test_marketplace_layout.py
git commit -m "docs: define Yandex plugin standard and roadmap"
```

---

### Task 4: Add repository validator and tests

**Files:**
- Create: `scripts/validate_repo.py`
- Create: `tests/test_validate_repo.py`

**Interfaces:**
- Consumes: root marketplace and plugin folders.
- Produces: `validate_repository(root: Path) -> list[str]`; empty list means repository contract is valid.

- [ ] **Step 1: Write failing validator tests**

Tests must verify that the validator catches:

1. marketplace source path that does not exist;
2. plugin missing `.codex-plugin/plugin.json`;
3. plugin manifest `skills` target missing;
4. `SKILL.md` missing YAML frontmatter;
5. skill description not starting with `Use when`;
6. runtime-specific absolute paths such as `~/.openclaw/` or `~/.claude/` in skill files;
7. malformed `evals/scenarios.json`;
8. valid repository returns no errors.

Use only `tempfile`, `json`, `pathlib`, and `unittest`.

- [ ] **Step 2: Run validator tests and verify RED**

```bash
python -m unittest tests.test_validate_repo -v
```

Expected: import failure because `scripts.validate_repo` does not yet exist.

- [ ] **Step 3: Implement minimal standard-library validator**

Create:

```python
def validate_repository(root: Path) -> list[str]:
    ...
```

The CLI must exit 0 on success, print `Repository validation passed`, and exit 1 after printing each validation error on its own line when invalid.

- [ ] **Step 4: Run validator unit tests**

```bash
python -m unittest tests.test_validate_repo -v
```

Expected: PASS.

- [ ] **Step 5: Run validator on the real repository**

```bash
python scripts/validate_repo.py
```

Expected: `Repository validation passed` and exit 0.

- [ ] **Step 6: Commit validator**

```bash
git add scripts/validate_repo.py tests/test_validate_repo.py
git commit -m "feat: validate marketplace plugin contracts"
```

---

### Task 5: Add path-aware GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `tests/test_marketplace_layout.py`

**Interfaces:**
- Consumes: root validator and `plugins/yandex-direct` test suite.
- Produces: root validation on every relevant change and Direct-specific test execution only when Direct/shared contract paths change.

- [ ] **Step 1: Add a failing CI-layout assertion**

Extend `tests/test_marketplace_layout.py` to require `.github/workflows/ci.yml` and assert it contains both `scripts/validate_repo.py` and `plugins/yandex-direct`.

- [ ] **Step 2: Run test and verify RED**

```bash
python -m unittest tests.test_marketplace_layout -v
```

Expected: failure because CI workflow is absent.

- [ ] **Step 3: Add CI workflow**

Workflow requirements:

- triggers: pull requests, pushes to `main`, manual dispatch;
- checkout with full enough history for diff detection;
- Python 3.13;
- root validation job always runs `python scripts/validate_repo.py` and root tests;
- a change-detection job marks Direct changed when files under `plugins/yandex-direct/**` or shared contract paths (`.agents/**`, `.claude-plugin/**`, `scripts/validate_repo.py`, `docs/PLUGIN_STANDARD.md`) change;
- Direct job runs only when that output is true;
- Direct job executes:

```bash
cd plugins/yandex-direct
python -m unittest discover -s tests -v
python -m py_compile scripts/yd_api.py scripts/yd_report.py
```

Use shell/git for change detection; do not add third-party path-filter dependencies.

- [ ] **Step 4: Run layout tests and YAML text sanity checks**

```bash
python -m unittest tests.test_marketplace_layout -v
python scripts/validate_repo.py
```

Expected: PASS and validator exit 0.

- [ ] **Step 5: Commit CI**

```bash
git add .github/workflows/ci.yml tests/test_marketplace_layout.py
git commit -m "ci: add path-aware marketplace validation"
```

---

### Task 6: Full Phase 1 verification and integration readiness

**Files:**
- Review all files changed since `main`.

**Interfaces:**
- Consumes: all prior tasks.
- Produces: verified feature branch ready for merge/PR decision.

- [ ] **Step 1: Run the complete root test suite**

```bash
python -m unittest discover -s tests -v
```

Expected: 0 failures.

- [ ] **Step 2: Run repository validation**

```bash
python scripts/validate_repo.py
```

Expected: `Repository validation passed`.

- [ ] **Step 3: Run complete Direct regression suite**

```bash
cd plugins/yandex-direct
python -m unittest discover -s tests -v
python -m py_compile scripts/yd_api.py scripts/yd_report.py
```

Expected: existing Direct tests all pass and compilation exits 0.

- [ ] **Step 4: Validate JSON manifests explicitly**

From repository root:

```bash
python - <<'PY'
import json
from pathlib import Path
for path in [
    Path('.agents/plugins/marketplace.json'),
    Path('.claude-plugin/marketplace.json'),
    Path('plugins/yandex-direct/.codex-plugin/plugin.json'),
    Path('plugins/yandex-direct/.claude-plugin/plugin.json'),
    Path('plugins/yandex-direct/evals/scenarios.json'),
]:
    json.loads(path.read_text())
    print('OK', path)
PY
```

Expected: every file prints `OK`.

- [ ] **Step 5: Review migration diff against the approved spec**

Confirm:

- Direct version remains `1.0.0`;
- Direct runtime code is unchanged except relative location;
- Direct root-level plugin artifacts are gone;
- root marketplace points to `plugins/yandex-direct`;
- root standards, roadmap, service matrix, validator, and CI exist;
- no future service is falsely marked available;
- no secret material or cache artifacts are tracked.

- [ ] **Step 6: Commit any verification-only corrections, then use the finishing-a-development-branch workflow**

Do not claim Phase 1 complete until all commands above have been run fresh on the final tree and report zero failures.