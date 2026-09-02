import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_marketing_prioritize():
    path = ROOT / "plugins/yandex-marketing/scripts/marketing_prioritize.py"
    spec = importlib.util.spec_from_file_location("marketing_prioritize_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load marketing_prioritize.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReviewFollowupTraceabilityTests(unittest.TestCase):
    def test_review_blocker_contracts_are_traceable(self):
        matrix = json.loads((ROOT / "docs/CONTRACT_MATRIX.json").read_text(encoding="utf-8"))
        ids = {contract["id"] for contract in matrix["contracts"]}
        required = {
            "direct.preview-before-write",
            "metrika.direct-expense-duplication-guard",
            "webmaster.feed-batch-safety",
            "webmaster.indexing-archive-lifecycle",
            "seo.evidence-period-geo-semantics",
            "seo.webmaster-impressions-unknown",
            "marketing.quality-metadata-shape",
        }
        self.assertEqual(required - ids, set())

    def test_marketing_design_taxonomy_matches_executable_contract(self):
        module = load_marketing_prioritize()
        expected_implemented = {
            "MEASUREMENT_RISK",
            "KPI_CONTEXT_MISMATCH",
            "ATTRIBUTION_MISMATCH",
            "BUDGET_CONSTRAINT_CANDIDATE",
            "BUDGET_REALLOCATION_CANDIDATE",
            "DEMAND_EXPANSION_CANDIDATE",
            "SEARCH_TERM_EXPANSION_CANDIDATE",
            "SEARCH_TERM_EXCLUSION_REVIEW",
            "LANDING_MISMATCH_HYPOTHESIS",
        }
        expected_deferred = {
            "GOAL_ALIGNMENT_RISK",
            "MATURITY_RISK",
            "SPEND_EFFICIENCY_REVIEW",
            "QUERY_COVERAGE_GAP",
            "SEASONALITY_ALERT",
            "QUERY_MISMATCH_HYPOTHESIS",
            "TRAFFIC_QUALITY_HYPOTHESIS",
            "COMPETITIVE_CONTEXT",
            "SERP_INTENT_CONTEXT",
        }
        self.assertEqual(module.IMPLEMENTED_FINDING_TYPES, expected_implemented)
        self.assertEqual(module.DEFERRED_FINDING_TYPES, expected_deferred)
        self.assertEqual(module.APPROVED_EXTERNAL_FINDING_TYPES, {"GOAL_ALIGNMENT_RISK"})

        design = (ROOT / "docs/superpowers/specs/2026-09-02-yandex-marketing-plugin-design.md").read_text(encoding="utf-8")
        self.assertIn("OPUS 1.1.1 normative amendment", design)
        self.assertIn("exactly these nine classes", design)
        for finding_type in expected_implemented | expected_deferred | {"QUERY_INTENT_REVIEW"}:
            self.assertIn(f"`{finding_type}`", design)
        self.assertIn("historical design vocabulary only", design)

    def test_cross_service_auth_policy_is_documented_as_deferred_metadata(self):
        for plugin in ("yandex-seo", "yandex-marketing"):
            for filename in ("README.md", "README.en.md"):
                text = (ROOT / "plugins" / plugin / filename).read_text(encoding="utf-8")
                self.assertIn("authentication: ON_USE", text, f"{plugin}/{filename}")
                self.assertIn("deferred-auth", text, f"{plugin}/{filename}")

    def test_opus_1_1_1_publisher_declares_expected_tags(self):
        workflow = (ROOT / ".github/workflows/publish-opus-1.1.1.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_run", workflow)
        self.assertIn("conclusion == 'success'", workflow)
        for tag in ("opus-1.1.1", "yandex-metrika-v1.0.2", "yandex-webmaster-v1.0.3"):
            self.assertIn(tag, workflow)


if __name__ == "__main__":
    unittest.main()
