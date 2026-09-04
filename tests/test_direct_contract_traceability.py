import json
from pathlib import Path
import unittest

from scripts.contract_controls import parse_verified_date


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "docs/CONTRACT_MATRIX.json"
DIRECT_SOURCES = "plugins/yandex-direct/references/sources.md"


class DirectContractTraceabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        cls.contracts = {item["id"]: item for item in cls.matrix["contracts"]}

    def assert_contract_traces(self, contract_id, *, skill, helper, test, reference):
        contract = self.contracts[contract_id]
        self.assertEqual(contract["plugin"], "yandex-direct")
        self.assertEqual(contract["status"], "implemented")
        self.assertIn(skill, contract["skills"])
        self.assertIn(helper, contract["helpers"])
        self.assertIn(test, contract["tests"])
        self.assertIn(reference, contract["references"])

    def test_reports_async_transport_contract_is_explicit(self):
        self.assert_contract_traces(
            "direct.reports-async-transport",
            skill="plugins/yandex-direct/skills/yandex-direct-reporting/SKILL.md",
            helper="plugins/yandex-direct/scripts/yd_report.py",
            test="plugins/yandex-direct/tests/test_yd_report.py",
            reference="plugins/yandex-direct/references/api-2026.md",
        )

    def test_reports_kpi_provenance_contract_is_explicit(self):
        self.assert_contract_traces(
            "direct.reports-kpi-provenance",
            skill="plugins/yandex-direct/skills/yandex-direct-reporting/SKILL.md",
            helper="plugins/yandex-direct/scripts/yd_report.py",
            test="plugins/yandex-direct/tests/test_yd_report.py",
            reference="plugins/yandex-direct/references/reporting.md",
        )

    def test_creation_not_activation_contract_is_explicit(self):
        self.assert_contract_traces(
            "direct.creation-not-activation",
            skill="plugins/yandex-direct/skills/yandex-direct-create/SKILL.md",
            helper="plugins/yandex-direct/scripts/yd_api.py",
            test="plugins/yandex-direct/tests/test_yd_api.py",
            reference="plugins/yandex-direct/references/create-workflow.md",
        )

    def test_direct_sources_are_freshness_controlled_with_canonical_marker(self):
        freshness = self.contracts["repository.api-reference-freshness"]
        self.assertIn(DIRECT_SOURCES, freshness["references"])
        self.assertIn(DIRECT_SOURCES, freshness["freshness_controlled_references"])
        source_text = (ROOT / DIRECT_SOURCES).read_text(encoding="utf-8")
        verified = parse_verified_date(source_text)
        self.assertEqual(verified.isoformat(), "2026-09-04")


if __name__ == "__main__":
    unittest.main()
