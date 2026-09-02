import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase7ContractTests(unittest.TestCase):
    def test_contract_matrix_contains_phase7_invariants(self):
        matrix = json.loads((ROOT / "docs/CONTRACT_MATRIX.json").read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in matrix["contracts"]}
        expected = {
            "wordstat.topic-map-candidate-boundary",
            "seo.topical-architecture-structural-tree",
            "seo.topical-architecture-evidence-classes",
            "seo.internal-linking-preview-only",
        }
        self.assertTrue(expected.issubset(by_id), expected - set(by_id))
        for contract_id in expected:
            contract = by_id[contract_id]
            self.assertEqual(contract["status"], "implemented")
            self.assertTrue(contract["skills"], contract_id)
            self.assertTrue(contract["helpers"], contract_id)
            self.assertTrue(contract["tests"], contract_id)
            self.assertTrue(contract["references"], contract_id)

    def test_service_matrix_documents_ownership_pipeline_in_both_languages(self):
        ru = (ROOT / "docs/SERVICE_MATRIX.md").read_text(encoding="utf-8")
        en = (ROOT / "docs/SERVICE_MATRIX.en.md").read_text(encoding="utf-8")
        for text in (ru, en):
            self.assertIn("yandex-wordstat-topic-map", text)
            self.assertIn("yandex-search-clustering", text)
            self.assertIn("yandex-seo-topical-architecture", text)
            self.assertIn("yandex-seo-internal-linking", text)
            self.assertIn("wordstat-topic-map/v1", text)
            self.assertIn("seo-topical-architecture/v1", text)

    def test_wordstat_readmes_keep_candidate_only_boundary(self):
        for rel in ["plugins/yandex-wordstat/README.md", "plugins/yandex-wordstat/README.en.md"]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("yandex-wordstat-topic-map", text)
            self.assertIn("yandex-search-clustering", text)
            self.assertIn("yandex-seo-topical-architecture", text)
            self.assertIn("candidate", text.lower())
            self.assertNotIn("Wordstat proves final page boundaries", text)

    def test_seo_readmes_document_two_layer_architecture_and_transport_boundary(self):
        for rel in ["plugins/yandex-seo/README.md", "plugins/yandex-seo/README.en.md"]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("yandex-seo-topical-architecture", text)
            self.assertIn("yandex-seo-internal-linking", text)
            self.assertIn("structural_tree", text)
            self.assertIn("semantic_graph", text)
            self.assertIn("METHODOLOGY", text)
            self.assertIn("transport", text.lower())

    def test_root_readmes_explain_phase7_pipeline_and_versions(self):
        for rel in ["README.md", "README.en.md"]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("Wordstat", text)
            self.assertIn("Search", text)
            self.assertIn("Topical Architecture", text)
            self.assertIn("Internal Linking", text)
            self.assertIn("SERP", text)
            self.assertIn("yandex-wordstat      1.1.0", text)
            self.assertIn("yandex-seo           1.1.0", text)

    def test_phase7_publisher_targets_exact_main_ci_commit_and_only_expected_tags(self):
        workflow = ROOT / ".github/workflows/publish-phase-7-topical-architecture.yml"
        self.assertTrue(workflow.is_file())
        text = workflow.read_text(encoding="utf-8")
        for token in [
            "workflow_run:",
            "head_branch == 'main'",
            "TARGET_SHA",
            'test "$(git rev-parse HEAD)" = "$TARGET_SHA"',
            '"version": "1.1.0"',
            "phase-7-topical-architecture-1.0.0",
            "yandex-wordstat-v1.1.0",
            "yandex-seo-v1.1.0",
        ]:
            self.assertIn(token, text)
        self.assertNotIn("yandex-search-v1.1.0", text)
        self.assertNotIn("yandex-search-v1.0.2", text)


if __name__ == "__main__":
    unittest.main()
