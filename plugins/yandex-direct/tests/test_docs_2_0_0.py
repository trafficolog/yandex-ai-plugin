import json
from pathlib import Path
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]


class Direct200DocumentationTests(unittest.TestCase):
    def test_readmes_document_hardened_cli_and_transport_contract(self):
        for name in ["README.md", "README.en.md"]:
            text = (PLUGIN / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertIn("YANDEX_DIRECT_TOKEN", text)
                self.assertIn("--sandbox", text)
                self.assertIn("RequestId", text)
                self.assertIn("Units", text)
                self.assertIn("python -m compileall -q scripts", text)
                self.assertNotIn(" --token ", text)

    def test_changelogs_document_final_2_0_0_helper_hardening(self):
        for name in ["CHANGELOG.md", "CHANGELOG.en.md"]:
            text = (PLUGIN / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertIn("## 2.0.0", text)
                self.assertIn("YANDEX_DIRECT_TOKEN", text)
                self.assertIn("sandbox", text.lower())
                self.assertIn("RequestId", text)

    def test_api_skill_documents_env_token_and_sandbox_boundary(self):
        text = (PLUGIN / "skills/yandex-direct-api/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("YANDEX_DIRECT_TOKEN", text)
        self.assertIn("--sandbox", text)
        self.assertIn("RequestId", text)

    def test_safety_reference_names_environment_as_approval_bound(self):
        text = (PLUGIN / "references/safety.md").read_text(encoding="utf-8")
        self.assertIn("environment", text.lower())
        self.assertIn("production", text.lower())
        self.assertIn("sandbox", text.lower())

    def test_direct_api_reference_is_freshness_controlled(self):
        matrix = json.loads((ROOT / "docs/CONTRACT_MATRIX.json").read_text(encoding="utf-8"))
        contract = next(item for item in matrix["contracts"] if item["id"] == "repository.api-reference-freshness")
        path = "plugins/yandex-direct/references/api-2026.md"
        self.assertIn(path, contract["references"])
        self.assertIn(path, contract["freshness_controlled_references"])


if __name__ == "__main__":
    unittest.main()
