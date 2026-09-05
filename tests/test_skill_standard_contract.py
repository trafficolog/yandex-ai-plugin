from pathlib import Path
import re
import unittest

from scripts import validate_repo


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ID = "REQ-SKILL-CONTENT"


class SkillStandardContractTests(unittest.TestCase):
    def test_ru_en_requirement_tables_include_skill_content_id(self):
        for relative in ("docs/PLUGIN_STANDARD.md", "docs/PLUGIN_STANDARD.en.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(relative=relative):
                self.assertIn(f"| {EXPECTED_ID} |", text)

    def test_section_five_matches_validator_numeric_bounds(self):
        self.assertEqual(validate_repo.MIN_SKILL_DESCRIPTION_CHARS, 32)
        self.assertEqual(validate_repo.MAX_SKILL_DESCRIPTION_CHARS, 500)
        self.assertEqual(validate_repo.MAX_SKILL_BYTES, 15 * 1024)
        for relative in ("docs/PLUGIN_STANDARD.md", "docs/PLUGIN_STANDARD.en.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            section = text.split("## 5. Skill conventions", 1)[1].split("## 6.", 1)[0]
            with self.subTest(relative=relative):
                self.assertRegex(section, re.compile(r"32.?500"))
                self.assertIn("15 KiB", section)

    def test_section_five_documents_progressive_disclosure_and_body_semantics(self):
        expectations = {
            "docs/PLUGIN_STANDARD.md": (
                "progressive disclosure",
                "не должен",
                "делег",
                "limitations",
                "approval-contract: exact-preview",
                "untrusted-data-policy: data-not-instructions",
            ),
            "docs/PLUGIN_STANDARD.en.md": (
                "progressive disclosure",
                "must not",
                "delegat",
                "limitations",
                "approval-contract: exact-preview",
                "untrusted-data-policy: data-not-instructions",
            ),
        }
        for relative, needles in expectations.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            section = text.split("## 5. Skill conventions", 1)[1].split("## 6.", 1)[0].casefold()
            for needle in needles:
                with self.subTest(relative=relative, needle=needle):
                    self.assertIn(needle.casefold(), section)


if __name__ == "__main__":
    unittest.main()
