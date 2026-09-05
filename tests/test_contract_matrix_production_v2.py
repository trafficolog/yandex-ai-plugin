from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ProductionContractMatrixV2Tests(unittest.TestCase):
    def test_production_matrix_uses_only_v2_exact_test_refs(self):
        data = json.loads((ROOT / "docs/CONTRACT_MATRIX.json").read_text(encoding="utf-8"))
        self.assertEqual(data["version"], 2)
        for contract in data["contracts"]:
            with self.subTest(contract=contract.get("id")):
                self.assertNotIn("tests", contract)
                if contract.get("status") in {"implemented", "infrastructure"}:
                    refs = contract.get("test_refs")
                    self.assertIsInstance(refs, list)
                    self.assertTrue(refs)
                    self.assertTrue(all("::" in ref for ref in refs))


if __name__ == "__main__":
    unittest.main()
