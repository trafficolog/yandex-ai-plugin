import unittest

from scripts import seo_topical_architecture


COVERAGE_WITH_SEARCH = {
    "wordstat": "COMPLETE",
    "search": "COMPLETE",
    "webmaster": "COMPLETE",
    "metrika": "MISSING",
    "site_inventory": "COMPLETE",
}

NODES = [
    {
        "page_id": "existing",
        "url": "/existing/",
        "canonical_parent_id": None,
        "cluster_ids": [],
        "evidence": ["WEBMASTER_EXISTING_URL"],
        "confidence": "MEDIUM",
    }
]


class TestSeoFinalReviewHardening(unittest.TestCase):
    def test_page_decision_evidence_must_be_a_list(self):
        for malformed in ("WEBMASTER_EXISTING_URL", {"source": "webmaster"}):
            with self.subTest(malformed=malformed):
                with self.assertRaises(ValueError):
                    seo_topical_architecture.build_topical_architecture(
                        mode="EXISTING_SITE",
                        coverage=COVERAGE_WITH_SEARCH,
                        clusters=[],
                        page_decisions=[{
                            "page_id": "existing",
                            "decision": "PRESERVE",
                            "cluster_ids": [],
                            "evidence": malformed,
                            "confidence": "MEDIUM",
                            "claim_class": "OBSERVED",
                        }],
                        structural_nodes=NODES,
                        semantic_edges=[],
                    )


if __name__ == "__main__":
    unittest.main()
