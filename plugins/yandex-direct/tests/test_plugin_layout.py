import json
import pathlib
import re
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]


class TestPluginLayout(unittest.TestCase):
    def test_codex_manifest_points_to_skills(self):
        data = json.loads((PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(data["skills"], "./skills/")
        self.assertIn("interface", data)

    def test_marketplace_points_to_local_plugin(self):
        data = json.loads((REPO_ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(data["plugins"][0]["source"], {"source": "local", "path": "./plugins/yandex-direct"})

    def test_every_skill_has_discoverable_frontmatter(self):
        skill_files = sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md"))
        self.assertGreaterEqual(len(skill_files), 6)
        for path in skill_files:
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            name = re.search(r"^name:\s*([a-z0-9-]+)\s*$", text, re.M)
            desc = re.search(r"^description:\s*(.+)$", text, re.M)
            self.assertIsNotNone(name, path)
            self.assertIsNotNone(desc, path)
            self.assertTrue(desc.group(1).startswith("Use when"), path)


if __name__ == "__main__":
    unittest.main()
