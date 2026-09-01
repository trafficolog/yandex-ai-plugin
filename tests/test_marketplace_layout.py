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


if __name__ == "__main__":
    unittest.main()
