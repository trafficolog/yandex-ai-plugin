from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SuperpowersNormativeBoundaryTests(unittest.TestCase):
    def test_canonical_governance_docs_do_not_treat_superpowers_as_normative_source(self):
        for relative in (
            "docs/PLUGIN_STANDARD.md",
            "docs/PLUGIN_STANDARD.en.md",
            "docs/RELEASE_POLICY.md",
            "docs/RELEASE_POLICY.en.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8").lower()
            with self.subTest(relative=relative):
                self.assertNotIn("canonical source: docs/superpowers/", text)
                self.assertNotIn("normative source: docs/superpowers/", text)

    def test_review_guidance_explicitly_marks_superpowers_as_historical(self):
        ru = (ROOT / "docs/REVIEW_FIRST_RELEASE.md").read_text(encoding="utf-8").lower()
        en = (ROOT / "docs/REVIEW_FIRST_RELEASE.en.md").read_text(encoding="utf-8").lower()
        self.assertIn("docs/superpowers/", ru)
        self.assertIn("историческ", ru)
        self.assertIn("docs/superpowers/", en)
        self.assertIn("historical implementation", en)


if __name__ == "__main__":
    unittest.main()
