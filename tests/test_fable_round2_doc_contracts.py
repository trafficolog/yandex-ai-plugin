from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FableRound2DocContractTests(unittest.TestCase):
    def test_plugin_readmes_do_not_depend_on_superpowers_specs(self):
        for path in sorted((ROOT / "plugins").glob("*/README*.md")):
            with self.subTest(path=path):
                self.assertNotIn("docs/superpowers/", path.read_text(encoding="utf-8"))

    def test_current_wordstat_naming_is_canonical(self):
        pairs = (
            (ROOT / "docs/ROADMAP.md", "Wordstat API в составе Yandex Search API v2"),
            (ROOT / "docs/ROADMAP.en.md", "Wordstat API within Yandex Search API v2"),
            (ROOT / "docs/SERVICE_MATRIX.md", "Wordstat API в составе Yandex Search API v2"),
            (ROOT / "docs/SERVICE_MATRIX.en.md", "Wordstat API within Yandex Search API v2"),
        )
        for path, phrase in pairs:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn(phrase, text)
                self.assertNotIn("Cloud Wordstat v2", text)


if __name__ == "__main__":
    unittest.main()
