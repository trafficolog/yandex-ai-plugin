from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Repository106ReleaseSurfaceTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_root_readmes_stage_repository_1_0_6(self):
        for filename in ("README.md", "README.en.md"):
            text = self.read(filename)
            with self.subTest(filename=filename):
                self.assertIn("release-1.0.6", text)
                self.assertIn("1.0.6", text)

    def test_bilingual_changelogs_stage_repository_1_0_6(self):
        marker = "## [1.0.6] — 2026-09-05"
        for filename in ("CHANGELOG.md", "CHANGELOG.en.md"):
            with self.subTest(filename=filename):
                self.assertIn(marker, self.read(filename))

    def test_release_policy_names_manifest_and_single_publisher(self):
        for filename in ("docs/RELEASE_POLICY.md", "docs/RELEASE_POLICY.en.md"):
            text = self.read(filename)
            with self.subTest(filename=filename):
                self.assertIn(".github/releases/release.json", text)
                self.assertIn("publish-current-release.yml", text)

    def test_release_policy_requires_new_repository_semver_for_every_release_set(self):
        ru = self.read("docs/RELEASE_POLICY.md").lower()
        en = self.read("docs/RELEASE_POLICY.en.md").lower()
        self.assertIn("каждый новый release set", ru)
        self.assertIn("новый repository semver", ru)
        self.assertIn("every new release set", en)
        self.assertIn("new repository semver", en)

    def test_release_policy_archives_historical_publishers_in_git_history(self):
        ru = self.read("docs/RELEASE_POLICY.md")
        en = self.read("docs/RELEASE_POLICY.en.md")
        for token in ("Git history", "immutable"):
            self.assertIn(token, ru)
            self.assertIn(token, en)
        self.assertIn("historical publisher", ru.lower())
        self.assertIn("historical publisher", en.lower())

    def test_release_policy_defines_empty_plugins_as_repository_only(self):
        for filename in ("docs/RELEASE_POLICY.md", "docs/RELEASE_POLICY.en.md"):
            text = self.read(filename)
            with self.subTest(filename=filename):
                self.assertIn("plugins: []", text)
                self.assertIn("plugin tag", text.lower())


if __name__ == "__main__":
    unittest.main()
