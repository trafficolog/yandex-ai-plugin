from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "yandex-direct": "2.0.1",
    "yandex-metrika": "2.0.0",
    "yandex-webmaster": "2.0.0",
    "yandex-wordstat": "1.1.2",
    "yandex-search": "1.0.2",
    "yandex-seo": "1.1.2",
    "yandex-marketing": "1.1.0",
}


class RepositoryOnlyScopeTests(unittest.TestCase):
    def test_all_plugin_manifest_versions_remain_unchanged(self):
        for plugin, version in EXPECTED.items():
            for relative in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
                data = json.loads((ROOT / "plugins" / plugin / relative).read_text(encoding="utf-8"))
                self.assertEqual(data["version"], version, f"{plugin}/{relative}")


if __name__ == "__main__":
    unittest.main()
