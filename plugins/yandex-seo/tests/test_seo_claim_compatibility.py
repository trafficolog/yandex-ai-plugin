import unittest

from scripts import seo_internal_linking, seo_topical_architecture


ARCHITECTURE = {
    "schema": "seo-topical-architecture/v1",
    "structural_tree": {
        "nodes": [
            {"page_id": "a", "canonical_parent_id": None},
            {"page_id": "b", "canonical_parent_id": None},
        ],
        "edges": [],
    },
    "semantic_graph": {"nodes": [{"page_id": "a"}, {"page_id": "b"}], "edges": []},
}

COVERAGE = {
    "wordstat": "COMPLETE",
    "search": "COMPLETE",
    "webmaster": "COMPLETE",
    "metrika": "PARTIAL",
    "site_inventory": "COMPLETE",
}


class TestSeoClaimCompatibility(unittest.TestCase):
    def test_methodology_only_link_cannot_claim_observed_or_derived_evidence(self):
        for claim_class in ("OBSERVED", "DERIVED"):
            with self.subTest(claim_class=claim_class):
                with self.assertRaises(ValueError):
                    seo_internal_linking.build_link_plan(
                        architecture=ARCHITECTURE,
                        candidate_links=[{
                            "from_page_id": "a",
                            "to_page_id": "b",
                            "relation": "SUPPORT",
                            "user_need": "supporting methodology context",
                            "reason_codes": ["METHODOLOGY_HEURISTIC"],
                            "evidence": [],
                            "confidence": "HIGH",
                            "claim_class": claim_class,
                        }],
                    )

    def test_semantic_hypothesis_only_link_cannot_claim_empirical_evidence(self):
        with self.assertRaises(ValueError):
            seo_internal_linking.build_link_plan(
                architecture=ARCHITECTURE,
                candidate_links=[{
                    "from_page_id": "a",
                    "to_page_id": "b",
                    "relation": "SUPPORT",
                    "user_need": "candidate semantic path",
                    "reason_codes": ["SEMANTIC_HYPOTHESIS"],
                    "evidence": [],
                    "confidence": "MEDIUM",
                    "claim_class": "DERIVED",
                }],
            )

    def test_methodology_only_semantic_edge_cannot_claim_empirical_evidence(self):
        with self.assertRaises(ValueError):
            seo_topical_architecture.build_topical_architecture(
                mode="EXISTING_SITE",
                coverage=COVERAGE,
                clusters=[],
                page_decisions=[],
                structural_nodes=[
                    {
                        "page_id": "a",
                        "url": "/a/",
                        "canonical_parent_id": None,
                        "cluster_ids": [],
                        "evidence": [],
                        "confidence": "MEDIUM",
                    },
                    {
                        "page_id": "b",
                        "url": "/b/",
                        "canonical_parent_id": None,
                        "cluster_ids": [],
                        "evidence": [],
                        "confidence": "MEDIUM",
                    },
                ],
                semantic_edges=[{
                    "from_page_id": "a",
                    "to_page_id": "b",
                    "relation": "SUPPORT",
                    "user_need": "methodology-only semantic path",
                    "reason_codes": ["METHODOLOGY_HEURISTIC"],
                    "evidence": [],
                    "confidence": "HIGH",
                    "claim_class": "OBSERVED",
                }],
            )

    def test_unknown_reason_code_cannot_bypass_claim_compatibility(self):
        with self.assertRaises(ValueError):
            seo_internal_linking.build_link_plan(
                architecture=ARCHITECTURE,
                candidate_links=[{
                    "from_page_id": "a",
                    "to_page_id": "b",
                    "relation": "SUPPORT",
                    "user_need": "typo must not create empirical provenance",
                    "reason_codes": ["METHODOLOGY_HEURISTIC", "SERP_OVELRAP"],
                    "evidence": [],
                    "confidence": "HIGH",
                    "claim_class": "OBSERVED",
                }],
            )

    def test_methodology_only_link_remains_valid_as_methodology(self):
        plan = seo_internal_linking.build_link_plan(
            architecture=ARCHITECTURE,
            candidate_links=[{
                "from_page_id": "a",
                "to_page_id": "b",
                "relation": "SUPPORT",
                "user_need": "supporting methodology context",
                "reason_codes": ["METHODOLOGY_HEURISTIC"],
                "evidence": [],
                "confidence": "LOW",
                "claim_class": "METHODOLOGY",
            }],
        )
        self.assertEqual(plan[0]["claim_class"], "METHODOLOGY")


if __name__ == "__main__":
    unittest.main()
