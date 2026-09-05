from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Repository107ReleaseSurfaceTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_repository_1_0_7_release_notes_remain_historical(self):
        notes = ROOT / ".github/releases/1.0.7.md"
        self.assertTrue(notes.is_file())
        text = notes.read_text(encoding="utf-8")
        self.assertIn("Repository 1.0.7", text)
        self.assertIn("repository-only", text.lower())
        self.assertIn("no plugin tags are published", text.lower())

    def test_bilingual_changelogs_preserve_repository_1_0_7(self):
        marker = "## [1.0.7] — 2026-09-05"
        for filename in ("CHANGELOG.md", "CHANGELOG.en.md"):
            with self.subTest(filename=filename):
                self.assertIn(marker, self.read(filename))


if __name__ == "__main__":
    unittest.main()
