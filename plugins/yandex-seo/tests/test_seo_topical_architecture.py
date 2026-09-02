import unittest

from scripts import seo_topical_architecture


COVERAGE_WITH_SEARCH = {
    "wordstat": "COMPLETE",
    "search": "COMPLETE",
    "webmaster": "MISSING",
    "metrika": "MISSING",
    "site_inventory": "MISSING",
}


class TestSeoTopicalArchitecture(unittest.TestCase):
    def test_missing_search_adds_limitation_and_preserves_hypothesis(self):
        result = seo_topical_architecture.build_topical_architecture(
            mode="GREENFIELD",
            coverage={**COVERAGE_WITH_SEARCH, "search": "MISSING"},
            clusters=[],
            page_decisions=[{
                "page_id": "p1",
                "decision": "CREATE",
                "cluster_ids": ["c1"],
                "evidence": [],
                "confidence": "LOW",
                "claim_class": "HYPOTHESIS",
            }],
            structural_nodes=[{
                "page_id": "p1",
                "proposed_url": "/seo/",
                "canonical_parent_id": None,
                "breadcrumbs": [],
                "cluster_ids": ["c1"],
                "evidence": [],
                "confidence": "LOW",
            }],
            semantic_edges=[],
        )
        self.assertEqual(result["schema"], "seo-topical-architecture/v1")
        self.assertIn("SERP_VALIDATION_MISSING", result["limitations"])
        self.assertEqual(result["page_decisions"][0]["claim_class"], "HYPOTHESIS")

    def test_missing_search_rejects_strong_boundary_change_claim(self):
        with self.assertRaises(ValueError):
            seo_topical_architecture.build_topical_architecture(
                mode="GREENFIELD",
                coverage={**COVERAGE_WITH_SEARCH, "search": "MISSING"},
                clusters=[],
                page_decisions=[{
                    "page_id": "p1",
                    "decision": "CREATE",
                    "cluster_ids": [],
                    "evidence": ["WORDSTAT_ASSOCIATION"],
                    "confidence": "HIGH",
                    "claim_class": "DERIVED",
                }],
                structural_nodes=[{
                    "page_id": "p1",
                    "proposed_url": "/new/",
                    "canonical_parent_id": None,
                    "breadcrumbs": [],
                    "cluster_ids": [],
                    "evidence": ["WORDSTAT_ASSOCIATION"],
                    "confidence": "HIGH",
                }],
                semantic_edges=[],
            )

    def test_missing_search_allows_observed_preserve_existing_page(self):
        result = seo_topical_architecture.build_topical_architecture(
            mode="EXISTING_SITE",
            coverage={
                **COVERAGE_WITH_SEARCH,
                "search": "MISSING",
                "webmaster": "COMPLETE",
                "site_inventory": "COMPLETE",
            },
            clusters=[],
            page_decisions=[{
                "page_id": "p1",
                "decision": "PRESERVE",
                "cluster_ids": [],
                "evidence": ["WEBMASTER_EXISTING_URL"],
                "confidence": "HIGH",
                "claim_class": "OBSERVED",
            }],
            structural_nodes=[{
                "page_id": "p1",
                "url": "/existing/",
                "canonical_parent_id": None,
                "breadcrumbs": [],
                "cluster_ids": [],
                "evidence": ["WEBMASTER_EXISTING_URL"],
                "confidence": "HIGH",
            }],
            semantic_edges=[],
        )
        self.assertEqual(result["page_decisions"][0]["claim_class"], "OBSERVED")
        self.assertIn("SERP_VALIDATION_MISSING", result["limitations"])

    def test_duplicate_proposed_urls_are_rejected(self):
        with self.assertRaises(ValueError):
            seo_topical_architecture.build_topical_architecture(
                mode="GREENFIELD",
                coverage=COVERAGE_WITH_SEARCH,
                clusters=[],
                page_decisions=[],
                structural_nodes=[
                    {"page_id": "p1", "proposed_url": "/same/", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"},
                    {"page_id": "p2", "proposed_url": "/same/", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"},
                ],
                semantic_edges=[],
            )

    def test_unknown_parent_and_structural_cycle_are_rejected(self):
        with self.assertRaises(ValueError):
            seo_topical_architecture.build_topical_architecture(
                mode="GREENFIELD",
                coverage=COVERAGE_WITH_SEARCH,
                clusters=[],
                page_decisions=[],
                structural_nodes=[
                    {"page_id": "p1", "proposed_url": "/p1/", "canonical_parent_id": "missing", "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"}
                ],
                semantic_edges=[],
            )

        with self.assertRaises(ValueError):
            seo_topical_architecture.build_topical_architecture(
                mode="GREENFIELD",
                coverage=COVERAGE_WITH_SEARCH,
                clusters=[],
                page_decisions=[],
                structural_nodes=[
                    {"page_id": "p1", "proposed_url": "/p1/", "canonical_parent_id": "p2", "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"},
                    {"page_id": "p2", "proposed_url": "/p2/", "canonical_parent_id": "p1", "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"},
                ],
                semantic_edges=[],
            )

    def test_semantic_edge_requires_known_pages_and_valid_claim_class(self):
        nodes = [
            {"page_id": "p1", "proposed_url": "/p1/", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"}
        ]
        with self.assertRaises(ValueError):
            seo_topical_architecture.build_topical_architecture(
                mode="GREENFIELD",
                coverage=COVERAGE_WITH_SEARCH,
                clusters=[],
                page_decisions=[],
                structural_nodes=nodes,
                semantic_edges=[{
                    "from_page_id": "p1",
                    "to_page_id": "missing",
                    "relation": "SUPPORT",
                    "user_need": "detail",
                    "reason_codes": ["SEMANTIC_HYPOTHESIS"],
                    "evidence": [],
                    "confidence": "LOW",
                    "claim_class": "HYPOTHESIS",
                }],
            )

        with self.assertRaises(ValueError):
            seo_topical_architecture.build_topical_architecture(
                mode="GREENFIELD",
                coverage=COVERAGE_WITH_SEARCH,
                clusters=[],
                page_decisions=[],
                structural_nodes=[
                    *nodes,
                    {"page_id": "p2", "proposed_url": "/p2/", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"},
                ],
                semantic_edges=[{
                    "from_page_id": "p1",
                    "to_page_id": "p2",
                    "relation": "SUPPORT",
                    "user_need": "detail",
                    "reason_codes": [],
                    "evidence": [],
                    "confidence": "LOW",
                    "claim_class": "PROVEN_RANKING_FACTOR",
                }],
            )

    def test_methodology_edge_stays_methodology_and_existing_site_decision_is_preserved(self):
        result = seo_topical_architecture.build_topical_architecture(
            mode="EXISTING_SITE",
            coverage={**COVERAGE_WITH_SEARCH, "webmaster": "COMPLETE", "site_inventory": "COMPLETE"},
            clusters=[{"cluster_id": "c1"}],
            page_decisions=[{
                "page_id": "p1",
                "decision": "PRESERVE",
                "cluster_ids": ["c1"],
                "evidence": ["WEBMASTER_EXISTING_URL"],
                "confidence": "HIGH",
                "claim_class": "OBSERVED",
            }],
            structural_nodes=[
                {"page_id": "p1", "url": "/root/", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": ["c1"], "evidence": ["WEBMASTER_EXISTING_URL"], "confidence": "HIGH"},
                {"page_id": "p2", "url": "/root/support/", "canonical_parent_id": "p1", "breadcrumbs": ["p1"], "cluster_ids": [], "evidence": [], "confidence": "MEDIUM"},
            ],
            semantic_edges=[{
                "from_page_id": "p1",
                "to_page_id": "p2",
                "relation": "SUPPORT",
                "user_need": "supporting explanation",
                "reason_codes": ["METHODOLOGY_HEURISTIC"],
                "evidence": ["semantic-cocoon methodology"],
                "confidence": "LOW",
                "claim_class": "METHODOLOGY",
            }],
            fact_sets=[{
                "fact_set_id": "pricing",
                "subject": "price",
                "canonical_page_id": "p1",
                "consumers": ["p2"],
                "dimensions": ["region"],
                "verification_required": True,
            }],
        )
        self.assertEqual(result["mode"], "EXISTING_SITE")
        self.assertEqual(result["page_decisions"][0]["decision"], "PRESERVE")
        self.assertEqual(result["semantic_graph"]["edges"][0]["claim_class"], "METHODOLOGY")
        self.assertEqual(result["consistency"]["mutable_fact_sets"][0]["canonical_page_id"], "p1")


if __name__ == "__main__":
    unittest.main()
