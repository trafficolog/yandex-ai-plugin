from pathlib import Path
import tempfile
import unittest

from scripts.bilingual_docs import _validate_pair, release_markers


class BilingualDocumentationContractTests(unittest.TestCase):
    def test_release_markers_include_all_repository_milestone_prefixes(self):
        text = """# Changelog

## [1.0.4] — 2026-09-04
## [DOCS 1.0.0] — 2026-09-03
## [OPUS 1.1.3] — 2026-09-03
## [PHASE 7 1.0.0] — 2026-09-02
## [PHASE 7 1.0.1] — 2026-09-02
## [FABLE 2.0.0] — 2026-09-04
"""
        self.assertEqual(
            release_markers(text),
            [
                "1.0.4",
                "DOCS 1.0.0",
                "OPUS 1.1.3",
                "PHASE 7 1.0.0",
                "PHASE 7 1.0.1",
                "FABLE 2.0.0",
            ],
        )

    def test_pair_rejects_heading_level_structure_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ru = root / "README.md"
            en = root / "README.en.md"
            ru.write_text(
                "[English](README.en.md)\n\n## Section\n\n### Detail\n",
                encoding="utf-8",
            )
            en.write_text(
                "[Русский](README.md)\n\n## Section\n\n## Detail\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            _validate_pair(ru, en, errors)
            self.assertTrue(any("heading structure" in error for error in errors), errors)

    def test_pair_rejects_semver_set_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ru = root / "README.md"
            en = root / "README.en.md"
            ru.write_text(
                "[English](README.en.md)\n\n## Release\n\nCurrent `1.2.3`, previous `1.2.2`.\n",
                encoding="utf-8",
            )
            en.write_text(
                "[Русский](README.md)\n\n## Release\n\nCurrent `1.2.3`, previous `1.2.1`.\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            _validate_pair(ru, en, errors)
            self.assertTrue(any("SemVer tokens" in error for error in errors), errors)

    def test_phase7_marker_mismatch_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ru = root / "CHANGELOG.md"
            en = root / "CHANGELOG.en.md"
            ru.write_text(
                "[English](CHANGELOG.en.md)\n\n## [PHASE 7 1.0.1] — 2026-09-02\n",
                encoding="utf-8",
            )
            en.write_text(
                "[Русский](CHANGELOG.md)\n\n## [PHASE 7 1.0.0] — 2026-09-02\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            _validate_pair(ru, en, errors, compare_release_markers=True)
            self.assertTrue(any("release markers differ" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
