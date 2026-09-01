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

    def test_repository_foundation_docs_exist(self):
        for path in [
            "docs/PLUGIN_STANDARD.md",
            "docs/SERVICE_MATRIX.md",
            "docs/ROADMAP.md",
            "packages/README.md",
            "workflows/README.md",
        ]:
            self.assertTrue((ROOT / path).is_file(), path)

    def test_plugin_standard_contains_safety_contract(self):
        standard = (ROOT / "docs/PLUGIN_STANDARD.md").read_text(encoding="utf-8")
        self.assertIn(
            "read → analyze → preview → explicit approval → write → verify",
            standard,
        )

    def test_path_aware_ci_is_present(self):
        workflow = ROOT / ".github/workflows/ci.yml"
        self.assertTrue(workflow.is_file())
        content = workflow.read_text(encoding="utf-8")
        self.assertIn("scripts/validate_repo.py", content)
        self.assertIn("plugins/yandex-direct", content)

    def test_marketplace_exposes_direct_and_metrika(self):
        data = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        paths = {item["source"]["path"] for item in data["plugins"]}
        self.assertEqual(paths, {"./plugins/yandex-direct", "./plugins/yandex-metrika", "./plugins/yandex-webmaster", "./plugins/yandex-wordstat", "./plugins/yandex-search", "./plugins/yandex-seo"})

    def test_ci_has_metrika_plugin_job(self):
        content = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("metrika:", content)
        self.assertIn("plugins/yandex-metrika", content)

    def test_ci_has_webmaster_plugin_job(self):
        content = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("webmaster:", content)
        self.assertIn("plugins/yandex-webmaster", content)
        self.assertIn("steps.detect.outputs.webmaster", content)

    def test_service_matrix_marks_webmaster_available(self):
        content = (ROOT / "docs/SERVICE_MATRIX.md").read_text(encoding="utf-8")
        self.assertIn("| Yandex Webmaster | 1 | **available** | 1.0.0 |", content)

    def test_ci_has_wordstat_plugin_job(self):
        content = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("wordstat:", content)
        self.assertIn("plugins/yandex-wordstat", content)
        self.assertIn("steps.detect.outputs.wordstat", content)

    def test_service_matrix_marks_wordstat_available(self):
        content = (ROOT / "docs/SERVICE_MATRIX.md").read_text(encoding="utf-8")
        self.assertIn("| Yandex Wordstat | 1 | **available** | 1.0.0 |", content)

    def test_roadmap_marks_phase4_implemented_and_phase5_search_next(self):
        content = (ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn("## Phase 4 — Yandex Wordstat", content)
        self.assertIn("Implemented as plugin `1.0.0`", content)
        self.assertIn("## Phase 5 — Yandex Search", content)

    def test_ci_has_search_plugin_job(self):
        content=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('search:',content)
        self.assertIn('plugins/yandex-search',content)
        self.assertIn('steps.detect.outputs.search',content)

    def test_service_matrix_marks_search_available(self):
        content=(ROOT/'docs/SERVICE_MATRIX.md').read_text(encoding='utf-8')
        self.assertIn('| Yandex Search | 1 | **available** | 1.0.0 |',content)

    def test_roadmap_marks_phase5_implemented_and_phase6_next(self):
        content=(ROOT/'docs/ROADMAP.md').read_text(encoding='utf-8')
        self.assertIn('## Phase 5 — Yandex Search',content)
        self.assertIn('## Phase 6A — Yandex SEO',content)
        self.assertIn('Implemented as plugin `1.0.0`',content)

    def test_marketplace_exposes_yandex_seo(self):
        data=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
        paths={item['source']['path'] for item in data['plugins']}
        self.assertIn('./plugins/yandex-seo',paths)

    def test_ci_has_seo_plugin_job(self):
        content=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('seo:',content)
        self.assertIn('plugins/yandex-seo',content)
        self.assertIn('steps.detect.outputs.seo',content)

    def test_service_matrix_marks_seo_available(self):
        content=(ROOT/'docs/SERVICE_MATRIX.md').read_text(encoding='utf-8')
        self.assertIn('| Yandex SEO | X | **available** | 1.0.0 |',content)

    def test_roadmap_marks_phase6a_and_phase6b(self):
        content=(ROOT/'docs/ROADMAP.md').read_text(encoding='utf-8')
        self.assertIn('## Phase 6A — Yandex SEO',content)
        self.assertIn('Implemented as plugin `1.0.0`',content)
        self.assertIn('## Phase 6B — Yandex Marketing',content)


if __name__ == "__main__":
    unittest.main()
