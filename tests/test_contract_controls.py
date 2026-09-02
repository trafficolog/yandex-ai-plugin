import json
from datetime import date, timedelta
from pathlib import Path
import tempfile
import unittest

from scripts.validate_repo import (
    MAX_REFERENCE_AGE_DAYS,
    parse_verified_date,
    validate_contract_matrix,
    validate_reference_freshness,
)


class FreshnessContractTests(unittest.TestCase):
    def test_max_reference_age_is_90_days(self):
        self.assertEqual(MAX_REFERENCE_AGE_DAYS, 90)

    def test_supported_verified_marker_forms(self):
        expected = date(2026, 9, 2)
        for text in [
            "Verified: 2026-09-02",
            "verified 2026-09-02",
            "verified_at: 2026-09-02",
        ]:
            with self.subTest(text=text):
                self.assertEqual(parse_verified_date(text), expected)

    def test_malformed_or_missing_verified_date_fails(self):
        for text in ["Verified: 2026-13-40", "Verified: yesterday", "no marker"]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_verified_date(text)

    def test_exactly_90_days_is_valid_and_91_days_is_stale(self):
        today = date(2026, 9, 2)
        self.assertEqual(
            validate_reference_freshness("Verified: 2026-06-04", today=today),
            [],
        )
        errors = validate_reference_freshness("Verified: 2026-06-03", today=today)
        self.assertTrue(any("stale" in error.lower() for error in errors))

    def test_future_verification_date_is_rejected(self):
        errors = validate_reference_freshness(
            "verified_at: 2026-09-03",
            today=date(2026, 9, 2),
        )
        self.assertTrue(any("future" in error.lower() for error in errors))


class ContractMatrixTests(unittest.TestCase):
    def make_tree(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        skill = root / "plugins/yandex-direct/skills/router/SKILL.md"
        helper = root / "plugins/yandex-direct/scripts/helper.py"
        test = root / "plugins/yandex-direct/tests/test_helper.py"
        reference = root / "plugins/yandex-direct/references/api.md"
        for path in (skill, helper, test, reference):
            path.parent.mkdir(parents=True, exist_ok=True)
        skill.write_text("---\nname: router\ndescription: Use when routing.\n---\n", encoding="utf-8")
        helper.write_text("VALUE = 1\n", encoding="utf-8")
        test.write_text("def test_value(): assert True\n", encoding="utf-8")
        reference.write_text("Verified: 2026-09-02\n", encoding="utf-8")
        matrix = {
            "version": 1,
            "contracts": [{
                "id": "direct.preview-before-write",
                "plugin": "yandex-direct",
                "status": "implemented",
                "skills": ["plugins/yandex-direct/skills/router/SKILL.md"],
                "helpers": ["plugins/yandex-direct/scripts/helper.py"],
                "tests": ["plugins/yandex-direct/tests/test_helper.py"],
                "references": ["plugins/yandex-direct/references/api.md"],
                "freshness_controlled_references": ["plugins/yandex-direct/references/api.md"],
            }],
        }
        return tmp, root, matrix

    def test_valid_matrix(self):
        tmp, root, matrix = self.make_tree()
        self.addCleanup(tmp.cleanup)
        self.assertEqual(
            validate_contract_matrix(root, matrix, known_plugins={"yandex-direct"}, today=date(2026, 9, 2)),
            [],
        )

    def test_duplicate_contract_id_is_rejected(self):
        tmp, root, matrix = self.make_tree()
        self.addCleanup(tmp.cleanup)
        matrix["contracts"].append(dict(matrix["contracts"][0]))
        errors = validate_contract_matrix(root, matrix, known_plugins={"yandex-direct"}, today=date(2026, 9, 2))
        self.assertTrue(any("duplicate" in error.lower() for error in errors))

    def test_invalid_status_and_unknown_plugin_are_rejected(self):
        tmp, root, matrix = self.make_tree()
        self.addCleanup(tmp.cleanup)
        matrix["contracts"][0]["status"] = "planned-ish"
        matrix["contracts"][0]["plugin"] = "unknown"
        errors = validate_contract_matrix(root, matrix, known_plugins={"yandex-direct"}, today=date(2026, 9, 2))
        self.assertTrue(any("status" in error.lower() for error in errors))
        self.assertTrue(any("unknown plugin" in error.lower() for error in errors))

    def test_missing_path_and_non_skill_path_are_rejected(self):
        tmp, root, matrix = self.make_tree()
        self.addCleanup(tmp.cleanup)
        matrix["contracts"][0]["helpers"] = ["plugins/yandex-direct/scripts/missing.py"]
        matrix["contracts"][0]["skills"] = ["plugins/yandex-direct/scripts/helper.py"]
        errors = validate_contract_matrix(root, matrix, known_plugins={"yandex-direct"}, today=date(2026, 9, 2))
        self.assertTrue(any("does not exist" in error.lower() for error in errors))
        self.assertTrue(any("skill.md" in error.lower() for error in errors))

    def test_implemented_contract_requires_regression_test(self):
        tmp, root, matrix = self.make_tree()
        self.addCleanup(tmp.cleanup)
        matrix["contracts"][0]["tests"] = []
        errors = validate_contract_matrix(root, matrix, known_plugins={"yandex-direct"}, today=date(2026, 9, 2))
        self.assertTrue(any("regression test" in error.lower() for error in errors))

    def test_freshness_controlled_reference_requires_valid_marker(self):
        tmp, root, matrix = self.make_tree()
        self.addCleanup(tmp.cleanup)
        (root / "plugins/yandex-direct/references/api.md").write_text("No verification marker\n", encoding="utf-8")
        errors = validate_contract_matrix(root, matrix, known_plugins={"yandex-direct"}, today=date(2026, 9, 2))
        self.assertTrue(any("verification" in error.lower() for error in errors))


if __name__ == "__main__":
    unittest.main()
