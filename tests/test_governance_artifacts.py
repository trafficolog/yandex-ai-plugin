from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class GovernanceArtifactTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        path = ROOT / relative
        self.assertTrue(path.is_file(), relative)
        return path.read_text(encoding="utf-8")

    def test_review_and_security_pairs_exist(self):
        for relative in (
            "docs/reviews/README.md",
            "docs/reviews/README.en.md",
            "docs/reviews/2026-09-05-opus-codex-governance.md",
            "docs/reviews/2026-09-05-opus-codex-governance.en.md",
            "SECURITY.md",
            "SECURITY.en.md",
        ):
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_review_artifact_records_exact_pr56_evidence_and_quota_limitation(self):
        for relative in (
            "docs/reviews/2026-09-05-opus-codex-governance.md",
            "docs/reviews/2026-09-05-opus-codex-governance.en.md",
        ):
            text = self.read(relative).lower()
            with self.subTest(relative=relative):
                for token in (
                    "#56",
                    "130050f11b2612a01ca6909215dbf30952a89d45",
                    "23a14d9b9e51825b96286bf6f9a8d4244d035ebe",
                    "88d2f45e63308a476cbe456402bf17dc847436cb",
                    "33953946792",
                    "33954164035",
                    "33954198278",
                    "quota",
                ):
                    self.assertIn(token, text)
                self.assertIn("ci", text)
                self.assertIn("human", text)
                self.assertIn("review", text)

    def test_security_policies_cover_repository_specific_sensitive_categories(self):
        for relative in ("SECURITY.md", "SECURITY.en.md"):
            text = self.read(relative).lower()
            with self.subTest(relative=relative):
                for token in ("approval", "secret", "prompt", "immutable", "private"):
                    self.assertIn(token, text)
                self.assertTrue("public issue" in text or "публич" in text)

    def test_review_guidance_marks_superpowers_as_historical_non_normative_context(self):
        ru = self.read("docs/REVIEW_FIRST_RELEASE.md").lower()
        en = self.read("docs/REVIEW_FIRST_RELEASE.en.md").lower()
        self.assertIn("docs/superpowers/", ru)
        self.assertIn("историческ", ru)
        self.assertIn("docs/superpowers/", en)
        self.assertIn("historical implementation", en)

    def test_root_readmes_link_review_index_and_latest_dated_artifact(self):
        latest_stem = "docs/reviews/2026-09-05-opus-codex-governance"
        for relative in ("README.md", "README.en.md"):
            text = self.read(relative)
            with self.subTest(relative=relative):
                self.assertIn("docs/reviews/README", text)
                self.assertIn(latest_stem, text)


if __name__ == "__main__":
    unittest.main()
