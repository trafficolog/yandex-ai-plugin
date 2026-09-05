from __future__ import annotations

from datetime import date
from pathlib import Path
import tempfile
import unittest

from scripts.validate_repo import validate_contract_matrix


class ContractMatrixV2TraceabilityTests(unittest.TestCase):
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
        test.write_text(
            "import unittest\n\n"
            "FLAG = False\n\n"
            "def test_value():\n"
            "    assert True\n\n"
            "class HelperTests(unittest.TestCase):\n"
            "    def test_method(self):\n"
            "        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        reference.write_text("Verified: 2026-09-02\n", encoding="utf-8")
        matrix = {
            "version": 2,
            "contracts": [{
                "id": "direct.preview-before-write",
                "plugin": "yandex-direct",
                "status": "implemented",
                "skills": ["plugins/yandex-direct/skills/router/SKILL.md"],
                "helpers": ["plugins/yandex-direct/scripts/helper.py"],
                "test_refs": ["plugins/yandex-direct/tests/test_helper.py::test_value"],
                "references": ["plugins/yandex-direct/references/api.md"],
                "freshness_controlled_references": ["plugins/yandex-direct/references/api.md"],
            }],
        }
        return tmp, root, matrix, test

    def validate(self, root, matrix):
        return validate_contract_matrix(
            root,
            matrix,
            known_plugins={"yandex-direct"},
            today=date(2026, 9, 2),
        )

    def test_valid_top_level_function_selector_passes(self):
        tmp, root, matrix, _ = self.make_tree()
        self.addCleanup(tmp.cleanup)
        self.assertEqual(self.validate(root, matrix), [])

    def test_valid_class_method_selector_passes(self):
        tmp, root, matrix, _ = self.make_tree()
        self.addCleanup(tmp.cleanup)
        matrix["contracts"][0]["test_refs"] = [
            "plugins/yandex-direct/tests/test_helper.py::HelperTests::test_method"
        ]
        self.assertEqual(self.validate(root, matrix), [])

    def test_legacy_tests_key_is_rejected(self):
        tmp, root, matrix, _ = self.make_tree()
        self.addCleanup(tmp.cleanup)
        entry = matrix["contracts"][0]
        entry["tests"] = ["plugins/yandex-direct/tests/test_helper.py"]
        errors = self.validate(root, matrix)
        self.assertTrue(any("legacy" in error.lower() or "tests" in error.lower() for error in errors), errors)

    def test_missing_function_class_and_method_are_rejected(self):
        selectors = (
            "plugins/yandex-direct/tests/test_helper.py::test_missing",
            "plugins/yandex-direct/tests/test_helper.py::MissingTests::test_method",
            "plugins/yandex-direct/tests/test_helper.py::HelperTests::test_missing",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                tmp, root, matrix, _ = self.make_tree()
                self.addCleanup(tmp.cleanup)
                matrix["contracts"][0]["test_refs"] = [selector]
                self.assertTrue(self.validate(root, matrix))

    def test_malformed_escape_and_non_python_selectors_are_rejected(self):
        selectors = (
            "plugins/yandex-direct/tests/test_helper.py",
            "../outside.py::test_value",
            "plugins/yandex-direct/tests/test_helper.txt::test_value",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                tmp, root, matrix, _ = self.make_tree()
                self.addCleanup(tmp.cleanup)
                matrix["contracts"][0]["test_refs"] = [selector]
                self.assertTrue(self.validate(root, matrix))

    def test_invalid_python_and_non_utf8_fail_closed(self):
        for payload, binary in (("def test_value(:\n", False), (b"\xff\xfe", True)):
            with self.subTest(binary=binary):
                tmp, root, matrix, test = self.make_tree()
                self.addCleanup(tmp.cleanup)
                if binary:
                    test.write_bytes(payload)
                else:
                    test.write_text(payload, encoding="utf-8")
                self.assertTrue(self.validate(root, matrix))

    def test_static_skip_decorators_are_rejected(self):
        sources = (
            "import unittest\n@unittest.skip('x')\ndef test_value(): pass\n",
            "import unittest\n@unittest.skipIf(True, 'x')\ndef test_value(): pass\n",
            "import unittest\n@unittest.skipUnless(False, 'x')\ndef test_value(): pass\n",
            "import unittest\n@unittest.skip('x')\nclass HelperTests(unittest.TestCase):\n    def test_method(self): pass\n",
        )
        selectors = (
            "plugins/yandex-direct/tests/test_helper.py::test_value",
            "plugins/yandex-direct/tests/test_helper.py::test_value",
            "plugins/yandex-direct/tests/test_helper.py::test_value",
            "plugins/yandex-direct/tests/test_helper.py::HelperTests::test_method",
        )
        for source, selector in zip(sources, selectors):
            with self.subTest(selector=selector, source=source.splitlines()[1]):
                tmp, root, matrix, test = self.make_tree()
                self.addCleanup(tmp.cleanup)
                test.write_text(source, encoding="utf-8")
                matrix["contracts"][0]["test_refs"] = [selector]
                errors = self.validate(root, matrix)
                self.assertTrue(any("skip" in error.lower() for error in errors), errors)

    def test_dynamic_skip_condition_is_not_treated_as_static_skip(self):
        tmp, root, matrix, test = self.make_tree()
        self.addCleanup(tmp.cleanup)
        test.write_text(
            "import unittest\nFLAG = False\n@unittest.skipIf(FLAG, 'runtime')\ndef test_value(): pass\n",
            encoding="utf-8",
        )
        self.assertEqual(self.validate(root, matrix), [])


if __name__ == "__main__":
    unittest.main()
