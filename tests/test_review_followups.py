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
            "direct.preview-bound-write",
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

    def test_metrika_expense_reference_covers_non_utm_direct_provenance(self):
        text = (ROOT / "plugins/yandex-metrika/references/imports.md").read_text(encoding="utf-8")
        self.assertIn("TrafficSource", text)
        self.assertIn("TrafficSourceDetail", text)
        self.assertIn("DIRECT_SOURCE_UNVERIFIED", text)

    def test_shared_runtime_promotion_requires_installability_contract(self):
        for path in [ROOT / "docs/PLUGIN_STANDARD.md", ROOT / "docs/PLUGIN_STANDARD.en.md"]:
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("installability", text)
            self.assertIn("distribution", text)
            self.assertIn("shared runtime", text)

    def test_cross_service_auth_policy_is_documented_as_deferred_metadata(self):
        for path in [ROOT / "docs/PLUGIN_STANDARD.md", ROOT / "docs/PLUGIN_STANDARD.en.md"]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("ON_USE", text)
            self.assertIn("deferred-auth", text)

    def test_opus_1_1_1_publisher_declares_expected_tags(self):
        workflow = (ROOT / ".github/workflows/publish-opus-1.1.1.yml").read_text(encoding="utf-8")
        self.assertIn("opus-1.1.1", workflow)
        self.assertIn("yandex-metrika-v1.0.2", workflow)
        self.assertIn("yandex-marketing-v1.1.0", workflow)
