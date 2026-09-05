from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ProductionContractMatrixV2Tests(unittest.TestCase):
    def load_contracts(self):
        data = json.loads((ROOT / "docs/CONTRACT_MATRIX.json").read_text(encoding="utf-8"))
        return data, {contract["id"]: contract for contract in data["contracts"]}

    def test_production_matrix_uses_only_v2_exact_test_refs(self):
        data, _ = self.load_contracts()
        self.assertEqual(data["version"], 2)
        for contract in data["contracts"]:
            with self.subTest(contract=contract.get("id")):
                self.assertNotIn("tests", contract)
                if contract.get("status") in {"implemented", "infrastructure"}:
                    refs = contract.get("test_refs")
                    self.assertIsInstance(refs, list)
                    self.assertTrue(refs)
                    self.assertTrue(all("::" in ref for ref in refs))

    def test_search_presence_contract_traces_actual_presence_helper_and_regression(self):
        _, contracts = self.load_contracts()
        contract = contracts["search.presence-not-market-share"]
        self.assertIn("plugins/yandex-search/scripts/ys_compare.py", contract["helpers"])
        self.assertIn(
            "plugins/yandex-search/tests/test_ys_compare.py::TestCompare::test_competitor_presence",
            contract["test_refs"],
        )


if __name__ == "__main__":
    unittest.main()
