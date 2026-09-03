import unittest

from scripts import seo_internal_linking, seo_topical_architecture


COVERAGE = {
    "wordstat": "COMPLETE",
    "search": "COMPLETE",
    "webmaster": "MISSING",
    "metrika": "MISSING",
    "site_inventory": "MISSING",
}


class TestPhase7PostReleaseHardening(unittest.TestCase):
    def test_structural_nodes_strip_execution_and_decision_state(self):
        result = seo_topical_architecture.build_topical_architecture(
            mode="GREENFIELD",
            coverage=COVERAGE,
            clusters=[],
            page_decisions=[],
            structural_nodes=[{
                "page_id": "p1",
                "proposed_url": "/topic/",
                "title": "Topic",
                "page_role": "ROOT",
                "canonical_parent_id": None,
                "breadcrumbs": [],
                "cluster_ids": [],
                "evidence": [],
                "confidence": "LOW",
                "decision": "REDIRECT",
                "status": "EXECUTED",
                "write": True,
                "execution_id": "exec-1",
            }],
            semantic_edges=[],
        )

        node = result["structural_tree"]["nodes"][0]
        self.assertEqual(node["title"], "Topic")
        for forbidden in ("decision", "status", "write", "execution_id"):
            self.assertNotIn(forbidden, node)

    def test_link_plan_rejects_non_list_evidence(self):
        architecture = seo_topical_architecture.build_topical_architecture(
            mode="GREENFIELD",
            coverage=COVERAGE,
            clusters=[],
            page_decisions=[],
            structural_nodes=[
                {
                    "page_id": "p1",
                    "proposed_url": "/a/",
                    "page_role": "ROOT",
                    "canonical_parent_id": None,
                    "breadcrumbs": [],
                    "cluster_ids": [],
                    "evidence": [],
                    "confidence": "LOW",
                },
                {
                    "page_id": "p2",
                    "proposed_url": "/b/",
                    "page_role": "ROOT",
                    "canonical_parent_id": None,
                    "breadcrumbs": [],
                    "cluster_ids": [],
                    "evidence": [],
                    "confidence": "LOW",
                },
            ],
            semantic_edges=[],
        )
        base = {
            "from_page_id": "p1",
            "to_page_id": "p2",
            "relation": "SUPPORT",
            "user_need": "Read supporting detail",
            "reason_codes": ["SEMANTIC_HYPOTHESIS"],
            "confidence": "LOW",
            "claim_class": "HYPOTHESIS",
        }
        for malformed in ("cluster:c1", {"source": "c1"}):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                seo_internal_linking.build_link_plan(
                    architecture=architecture,
                    candidate_links=[{**base, "evidence": malformed}],
                )


if __name__ == "__main__":
    unittest.main()
