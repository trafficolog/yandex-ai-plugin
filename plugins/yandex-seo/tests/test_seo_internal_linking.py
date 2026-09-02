import unittest

from scripts import seo_internal_linking


ARCHITECTURE = {
    "schema": "seo-topical-architecture/v1",
    "structural_tree": {
        "nodes": [
            {"page_id": "root", "canonical_parent_id": None},
            {"page_id": "support", "canonical_parent_id": "root"},
            {"page_id": "compare", "canonical_parent_id": "root"},
        ],
        "edges": [
            {"parent_page_id": "root", "child_page_id": "support"},
            {"parent_page_id": "root", "child_page_id": "compare"},
        ],
    },
    "semantic_graph": {
        "nodes": [{"page_id": "root"}, {"page_id": "support"}, {"page_id": "compare"}],
        "edges": [
            {
                "from_page_id": "root",
                "to_page_id": "support",
                "relation": "SUPPORT",
                "user_need": "learn details",
                "reason_codes": ["SERP_OVERLAP"],
                "evidence": ["cluster:c1"],
                "confidence": "HIGH",
                "claim_class": "DERIVED",
            },
            {
                "from_page_id": "support",
                "to_page_id": "root",
                "relation": "PARENT_CONTEXT",
                "user_need": "return to overview",
                "reason_codes": ["METHODOLOGY_HEURISTIC"],
                "evidence": [],
                "confidence": "LOW",
                "claim_class": "METHODOLOGY",
            },
        ],
    },
}


class TestSeoInternalLinking(unittest.TestCase):
    def test_link_plan_is_preview_only_and_preserves_claim_class(self):
        plan = seo_internal_linking.build_link_plan(
            architecture=ARCHITECTURE,
            candidate_links=[{
                "from_page_id": "support",
                "to_page_id": "root",
                "relation": "PARENT_CONTEXT",
                "user_need": "return to overview",
                "reason_codes": ["METHODOLOGY_HEURISTIC"],
                "evidence": [],
                "confidence": "LOW",
                "claim_class": "METHODOLOGY",
                "anchor_concept": "основная тема",
                "placement": "after supporting explanation",
            }],
        )
        self.assertEqual(plan[0]["status"], "PREVIEW")
        self.assertEqual(plan[0]["claim_class"], "METHODOLOGY")
        self.assertNotIn("execute", plan[0])
        self.assertNotIn("write", plan[0])

    def test_unknown_endpoint_and_forced_exact_match_are_rejected(self):
        with self.assertRaises(ValueError):
            seo_internal_linking.build_link_plan(
                architecture=ARCHITECTURE,
                candidate_links=[{
                    "from_page_id": "root", "to_page_id": "missing", "relation": "SUPPORT",
                    "user_need": "detail", "reason_codes": [], "evidence": [],
                    "confidence": "LOW", "claim_class": "HYPOTHESIS",
                }],
            )

        with self.assertRaises(ValueError):
            seo_internal_linking.build_link_plan(
                architecture=ARCHITECTURE,
                candidate_links=[{
                    "from_page_id": "root", "to_page_id": "support", "relation": "SUPPORT",
                    "user_need": "detail", "reason_codes": [], "evidence": [],
                    "confidence": "LOW", "claim_class": "HYPOTHESIS",
                    "anchor_concept": "seo аудит", "exact_match_required": True,
                }],
            )

    def test_audit_detects_orphans_structural_gaps_and_missing_semantic_links(self):
        audit = seo_internal_linking.audit_link_inventory(
            architecture=ARCHITECTURE,
            existing_links=[
                {"from_page_id": "root", "to_page_id": "support"},
            ],
        )
        types = [finding["type"] for finding in audit["findings"]]
        self.assertIn("ORPHAN_PAGE", types)
        self.assertIn("STRUCTURAL_PARENT_LINK_MISSING", types)
        self.assertIn("MISSING_JUSTIFIED_LINK", types)
        orphan_pages = {f["page_id"] for f in audit["findings"] if f["type"] == "ORPHAN_PAGE"}
        self.assertIn("compare", orphan_pages)

    def test_audit_reports_unknown_link_endpoint(self):
        audit = seo_internal_linking.audit_link_inventory(
            architecture=ARCHITECTURE,
            existing_links=[{"from_page_id": "root", "to_page_id": "outside"}],
        )
        self.assertIn("UNKNOWN_LINK_ENDPOINT", {f["type"] for f in audit["findings"]})

    def test_semantic_cycle_is_not_an_error_by_itself(self):
        audit = seo_internal_linking.audit_link_inventory(
            architecture=ARCHITECTURE,
            existing_links=[
                {"from_page_id": "root", "to_page_id": "support"},
                {"from_page_id": "support", "to_page_id": "root"},
                {"from_page_id": "root", "to_page_id": "compare"},
                {"from_page_id": "compare", "to_page_id": "root"},
            ],
        )
        self.assertNotIn("GRAPH_CYCLE", {f["type"] for f in audit["findings"]})


if __name__ == "__main__":
    unittest.main()
