import unittest

from scripts import seo_topical_architecture


COVERAGE = {
    "wordstat": "COMPLETE",
    "search": "COMPLETE",
    "webmaster": "COMPLETE",
    "metrika": "PARTIAL",
    "site_inventory": "COMPLETE",
}


class TestSeoReviewHardening(unittest.TestCase):
    def test_destructive_existing_site_decision_strips_execution_state(self):
        result = seo_topical_architecture.build_topical_architecture(
            mode="EXISTING_SITE",
            coverage=COVERAGE,
            clusters=[],
            page_decisions=[{
                "page_id": "legacy",
                "decision": "MERGE",
                "cluster_ids": [],
                "evidence": ["WEBMASTER_EXISTING_URL"],
                "confidence": "MEDIUM",
                "claim_class": "DERIVED",
                "status": "EXECUTED",
                "write": True,
                "execution_id": "should-not-survive",
            }],
            structural_nodes=[{
                "page_id": "legacy",
                "url": "/legacy/",
                "canonical_parent_id": None,
                "breadcrumbs": [],
                "cluster_ids": [],
                "evidence": ["WEBMASTER_EXISTING_URL"],
                "confidence": "MEDIUM",
            }],
            semantic_edges=[],
        )
        decision = result["page_decisions"][0]
        self.assertEqual(decision["status"], "PREVIEW")
        self.assertNotIn("write", decision)
        self.assertNotIn("execution_id", decision)


if __name__ == "__main__":
    unittest.main()
