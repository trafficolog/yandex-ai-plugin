from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "REQ-SKILL-ROUTING", "REQ-REFERENCE-VOLATILITY", "REQ-HELPER-TESTS",
    "REQ-EVAL-CONTRACT", "REQ-READ-FIRST", "REQ-WRITE-PREVIEW",
    "REQ-EXPLICIT-APPROVAL", "REQ-NO-SECRETS", "REQ-CAPABILITY-MATRIX",
    "REQ-PLUGIN-SEMVER", "REQ-NO-UNIVERSAL-THRESHOLDS",
    "REQ-RUNTIME-PATH-PORTABILITY", "REQ-SOURCE-SEMANTICS",
    "REQ-CROSS-SERVICE-TRANSPORT", "REQ-BILINGUAL-DOCS",
    "REQ-CHANGELOG-PARITY", "REQ-DOCS-RELEASE-NO-PLUGIN-BUMP",
}


def parse_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        if not line.startswith("| REQ-"):
            continue
        rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows


class GovernanceRequirementTests(unittest.TestCase):
    def test_ru_en_requirement_ids_match_fixed_set_and_rows_are_complete(self):
        for filename in ("docs/PLUGIN_STANDARD.md", "docs/PLUGIN_STANDARD.en.md"):
            rows = parse_rows((ROOT / filename).read_text(encoding="utf-8"))
            ids = [cells[0] for cells in rows]
            with self.subTest(filename=filename):
                self.assertEqual(set(ids), EXPECTED)
                self.assertEqual(len(ids), len(EXPECTED))
                self.assertEqual(len(ids), len(set(ids)))
                for cells in rows:
                    self.assertEqual(len(cells), 4, cells)
                    self.assertTrue(all(cells), cells)
                    self.assertRegex(cells[2].lower(), r"validator|ci|review|policy")


if __name__ == "__main__":
    unittest.main()
