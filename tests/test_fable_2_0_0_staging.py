import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "yandex-direct": "yandex-direct-suite",
    "yandex-metrika": "yandex-metrika",
    "yandex-webmaster": "yandex-webmaster",
}


class Fable200StagingTests(unittest.TestCase):
    def test_target_plugin_manifests_are_staged_at_2_0_0(self):
        for plugin in TARGETS:
            with self.subTest(plugin=plugin):
                base = ROOT / "plugins" / plugin
                for relative in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
                    data = json.loads((base / relative).read_text(encoding="utf-8"))
                    self.assertEqual(data["version"], "2.0.0")

    def test_marketplaces_stage_exact_target_plugins_at_2_0_0(self):
        agents = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        agent_versions = {item["name"]: item["version"] for item in agents["plugins"]}
        claude_versions = {item["name"]: item["version"] for item in claude["plugins"]}
        for plugin, marketplace_name in TARGETS.items():
            with self.subTest(plugin=plugin):
                self.assertEqual(agent_versions[marketplace_name], "2.0.0")
                self.assertEqual(claude_versions[marketplace_name], "2.0.0")

    def test_migration_docs_show_old_and_new_execution_contract(self):
        for plugin in TARGETS:
            base = ROOT / "plugins" / plugin
            for filename in ("README.md", "README.en.md", "CHANGELOG.md", "CHANGELOG.en.md"):
                with self.subTest(plugin=plugin, file=filename):
                    text = (base / filename).read_text(encoding="utf-8")
                    self.assertIn("2.0.0", text)
                    self.assertIn("--execute", text)
                    self.assertIn("--approve <preview_id>", text)

    def test_root_readmes_show_staged_2_0_0_versions(self):
        for filename in ("README.md", "README.en.md"):
            text = (ROOT / filename).read_text(encoding="utf-8")
            for token in ("yandex-direct", "yandex-metrika", "yandex-webmaster"):
                self.assertIn(token, text)
            self.assertGreaterEqual(text.count("2.0.0"), 3)

    def test_service_matrix_stages_three_2_0_0_plugins(self):
        for filename in ("SERVICE_MATRIX.md", "SERVICE_MATRIX.en.md"):
            text = (ROOT / "docs" / filename).read_text(encoding="utf-8")
            for service in ("Yandex Direct", "Yandex Metrika", "Yandex Webmaster"):
                matching = [line for line in text.splitlines() if line.startswith(f"| {service} |")]
                self.assertEqual(len(matching), 1, service)
                self.assertIn("| 2.0.0 |", matching[0])


if __name__ == "__main__":
    unittest.main()
