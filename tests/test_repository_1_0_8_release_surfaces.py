from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PLUGINS = {
    "yandex-direct": "2.0.1",
    "yandex-metrika": "2.0.0",
    "yandex-webmaster": "2.0.0",
    "yandex-wordstat": "1.1.2",
    "yandex-search": "1.0.2",
    "yandex-seo": "1.1.2",
    "yandex-marketing": "1.1.0",
}


class Repository108ReleaseSurfaceTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_root_readmes_stage_repository_1_0_8(self):
        for filename in ("README.md", "README.en.md"):
            text = self.read(filename)
            with self.subTest(filename=filename):
                self.assertIn("release-1.0.8", text)
                self.assertIn("1.0.8", text)

    def test_bilingual_changelogs_stage_repository_1_0_8(self):
        marker = "## [1.0.8] — 2026-09-05"
        for filename in ("CHANGELOG.md", "CHANGELOG.en.md"):
            with self.subTest(filename=filename):
                self.assertIn(marker, self.read(filename))

    def test_declarative_manifest_is_repository_only_1_0_8(self):
        data = json.loads(self.read(".github/releases/release.json"))
        self.assertEqual(data["repository"]["version"], "1.0.8")
        self.assertEqual(data["repository"]["tag"], "1.0.8")
        self.assertEqual(data["repository"]["title"], "Repository 1.0.8")
        self.assertEqual(data["repository"]["notes_file"], ".github/releases/1.0.8.md")
        self.assertEqual(data["plugins"], [])
        self.assertTrue((ROOT / ".github/releases/1.0.8.md").is_file())

    def test_plugin_versions_remain_unchanged(self):
        for plugin, expected in EXPECTED_PLUGINS.items():
            for relative in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
                data = json.loads(self.read(f"plugins/{plugin}/{relative}"))
                self.assertEqual(data["version"], expected, f"{plugin}/{relative}")


if __name__ == "__main__":
    unittest.main()
