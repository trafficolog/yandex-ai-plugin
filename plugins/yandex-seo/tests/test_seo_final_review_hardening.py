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

    def test_missing_search_rejects_search_owned_provenance(self):
        missing_search = {**COVERAGE_WITH_SEARCH, "search": "MISSING"}

        with self.subTest(source="clusters"):
            with self.assertRaises(ValueError):
                seo_topical_architecture.build_topical_architecture(
                    mode="EXISTING_SITE",
                    coverage=missing_search,
                    clusters=[{"cluster_id": "search-c1"}],
                    page_decisions=[],
                    structural_nodes=NODES,
                    semantic_edges=[],
                )

        with self.subTest(source="page_decision_reason"):
            with self.assertRaises(ValueError):
                seo_topical_architecture.build_topical_architecture(
                    mode="EXISTING_SITE",
                    coverage=missing_search,
                    clusters=[],
                    page_decisions=[{
                        "page_id": "existing",
                        "decision": "PRESERVE",
                        "reason_codes": ["SERP_OVERLAP"],
                        "cluster_ids": [],
                        "evidence": [],
                        "confidence": "LOW",
                        "claim_class": "HYPOTHESIS",
                    }],
                    structural_nodes=NODES,
                    semantic_edges=[],
                )

        link_nodes = [
            *NODES,
            {
                "page_id": "support",
                "url": "/support/",
                "canonical_parent_id": "existing",
                "cluster_ids": [],
                "evidence": [],
                "confidence": "LOW",
            },
        ]
        with self.subTest(source="semantic_edge_reason"):
            with self.assertRaises(ValueError):
                seo_topical_architecture.build_topical_architecture(
                    mode="EXISTING_SITE",
                    coverage=missing_search,
                    clusters=[],
                    page_decisions=[],
                    structural_nodes=link_nodes,
                    semantic_edges=[{
                        "from_page_id": "existing",
                        "to_page_id": "support",
                        "relation": "SUPPORT",
                        "user_need": "supporting detail",
                        "reason_codes": ["SERP_BRIDGE_RISK"],
                        "evidence": [],
                        "confidence": "LOW",
                        "claim_class": "HYPOTHESIS",
                    }],
                )


if __name__ == "__main__":
    unittest.main()
