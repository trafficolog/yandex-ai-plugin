import unittest

from scripts import seo_topical_architecture


COVERAGE_WITH_SEARCH = {
    "wordstat": "COMPLETE",
    "search": "COMPLETE",
    "webmaster": "MISSING",
    "metrika": "MISSING",
    "site_inventory": "MISSING",
}


def existing_nodes():
    return [
        {"page_id": "p1", "url": "/one/", "page_role": "ROOT", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": ["c1"], "evidence": ["existing"], "confidence": "HIGH"},
        {"page_id": "p2", "url": "/two/", "page_role": "SUPPORT", "canonical_parent_id": "p1", "breadcrumbs": ["p1"], "cluster_ids": ["c1"], "evidence": ["existing"], "confidence": "HIGH"},
    ]


def valid_cluster(**overrides):
    cluster = {
        "cluster_id": "c1",
        "queries": ["seo", "seo audit"],
        "min_shared_urls": 2,
        "bridge_risk": False,
    }
    cluster.update(overrides)
    return cluster


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
                "page_role": "ROOT",
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
                    "page_role": "ROOT",
                    "canonical_parent_id": None,
                    "breadcrumbs": [],
                    "cluster_ids": [],
                    "evidence": ["WORDSTAT_ASSOCIATION"],
                    "confidence": "HIGH",
                }],
                semantic_edges=[],
            )

    def test_empirical_boundary_decision_requires_search_owned_reason_even_when_search_complete(self):
        with self.assertRaises(ValueError):
            seo_topical_architecture.build_topical_architecture(
                mode="EXISTING_SITE",
                coverage={**COVERAGE_WITH_SEARCH, "webmaster": "COMPLETE", "site_inventory": "COMPLETE"},
                clusters=[valid_cluster()],
                page_decisions=[{
                    "page_id": "p1",
                    "decision": "MERGE",
                    "target_page_id": "p2",
                    "cluster_ids": ["c1"],
                    "reason_codes": ["WORDSTAT_ASSOCIATION", "WEBMASTER_EXISTING_URL"],
                    "evidence": ["wordstat association"],
                    "confidence": "HIGH",
                    "claim_class": "DERIVED",
                }],
                structural_nodes=existing_nodes(),
                semantic_edges=[],
            )

    def test_partial_search_is_explicit_limitation(self):
        result = seo_topical_architecture.build_topical_architecture(
            mode="GREENFIELD",
            coverage={**COVERAGE_WITH_SEARCH, "search": "PARTIAL"},
            clusters=[],
            page_decisions=[],
            structural_nodes=[],
            semantic_edges=[],
        )
        self.assertIn("SERP_VALIDATION_PARTIAL", result["limitations"])

    def test_empirical_merge_requires_existing_page_evidence(self):
        with self.assertRaises(ValueError):
            seo_topical_architecture.build_topical_architecture(
                mode="EXISTING_SITE",
                coverage={**COVERAGE_WITH_SEARCH, "webmaster": "COMPLETE", "site_inventory": "COMPLETE"},
                clusters=[valid_cluster()],
                page_decisions=[{
                    "page_id": "p1",
                    "decision": "MERGE",
                    "target_page_id": "p2",
                    "cluster_ids": ["c1"],
                    "reason_codes": ["SERP_OVERLAP"],
                    "evidence": ["cluster:c1"],
                    "confidence": "HIGH",
                    "claim_class": "DERIVED",
                }],
                structural_nodes=existing_nodes(),
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

    def test_search_cluster_contract_is_validated_and_limitations_propagate(self):
        with self.assertRaises(ValueError):
            seo_topical_architecture.build_topical_architecture(
                mode="GREENFIELD",
                coverage=COVERAGE_WITH_SEARCH,
                clusters=[{"cluster_id": "c1"}],
                page_decisions=[],
                structural_nodes=[],
                semantic_edges=[],
            )

        result = seo_topical_architecture.build_topical_architecture(
            mode="GREENFIELD",
            coverage=COVERAGE_WITH_SEARCH,
            clusters=[valid_cluster(bridge_risk=True, limitations=["SEARCH_SNAPSHOT_PARTIAL"])],
            source_artifacts=[{
                "schema": "wordstat-topic-map/v1",
                "limitations": ["WORDSTAT_ASSOCIATIONS_CAPPED"],
            }],
            page_decisions=[],
            structural_nodes=[],
            semantic_edges=[],
        )
        self.assertIn("SEARCH_BRIDGE_RISK", result["limitations"])
        self.assertIn("SEARCH_SNAPSHOT_PARTIAL", result["limitations"])
        self.assertIn("WORDSTAT_ASSOCIATIONS_CAPPED", result["limitations"])

    def test_not_evaluated_stages_are_distinct_from_evaluated_empty_results(self):
        result = seo_topical_architecture.build_topical_architecture(
            mode="GREENFIELD",
            coverage=COVERAGE_WITH_SEARCH,
            clusters=[],
            page_decisions=[],
            structural_nodes=[],
            semantic_edges=[],
        )
        self.assertIsNone(result["link_plan"])
        self.assertIsNone(result["audits"])
        self.assertIsNone(result["consistency"]["navigation_conflicts"])
        self.assertIsNone(result["consistency"]["parity_checks"])

        result = seo_topical_architecture.attach_link_plan(result, [])
        result = seo_topical_architecture.attach_audit(result, {"kind": "INTERNAL_LINK_AUDIT", "findings": []})
        result = seo_topical_architecture.attach_consistency_results(
            result, navigation_conflicts=[], parity_checks=[]
        )
        self.assertEqual(result["link_plan"], [])
        self.assertEqual(result["audits"], [{"kind": "INTERNAL_LINK_AUDIT", "findings": []}])
        self.assertEqual(result["consistency"]["navigation_conflicts"], [])
        self.assertEqual(result["consistency"]["parity_checks"], [])

    def test_duplicate_proposed_urls_are_rejected(self):
        with self.assertRaises(ValueError):
            seo_topical_architecture.build_topical_architecture(
                mode="GREENFIELD",
                coverage=COVERAGE_WITH_SEARCH,
                clusters=[],
                page_decisions=[],
                structural_nodes=[
                    {"page_id": "p1", "proposed_url": "/same/", "page_role": "ROOT", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"},
                    {"page_id": "p2", "proposed_url": "/same/", "page_role": "ROOT", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"},
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
            {"page_id": "p1", "proposed_url": "/p1/", "page_role": "ROOT", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"}
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
                    {"page_id": "p2", "proposed_url": "/p2/", "page_role": "ROOT", "canonical_parent_id": None, "breadcrumbs": [], "cluster_ids": [], "evidence": [], "confidence": "LOW"},
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
            clusters=[valid_cluster()],
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
