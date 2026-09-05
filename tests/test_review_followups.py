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

    def test_metrika_expense_reference_covers_non_utm_direct_provenance(self):
        text = (ROOT / "plugins/yandex-metrika/references/imports.md").read_text(encoding="utf-8")
        for token in (
            "TrafficSourceDetail=yandex_direct_star",
            "DIRECT_DUPLICATION_RISK",
            "DIRECT_SOURCE_UNVERIFIED",
            "google_adwords",
        ):
            self.assertIn(token, text)

    def test_shared_runtime_promotion_requires_installability_contract(self):
        standard_ru = (ROOT / "docs/PLUGIN_STANDARD.md").read_text(encoding="utf-8")
        standard_en = (ROOT / "docs/PLUGIN_STANDARD.en.md").read_text(encoding="utf-8")
        package_doc = (ROOT / "packages/README.md").read_text(encoding="utf-8")
        amendment = (
            ROOT / "docs/superpowers/specs/2026-09-03-opus-1.1.2-residual-audit-hardening-amendment.md"
        ).read_text(encoding="utf-8")
        for text in (standard_ru, standard_en, package_doc, amendment):
            self.assertIn("installability", text.lower())
            self.assertIn("distribution", text.lower())
            self.assertIn("_http.py", text)
        self.assertIn("no hidden dependency on the monorepo root", standard_en.lower())
        self.assertIn("Independent installability", standard_en)


if __name__ == "__main__":
    unittest.main()
