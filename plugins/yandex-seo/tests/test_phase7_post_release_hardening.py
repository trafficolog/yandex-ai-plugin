import unittest

from scripts import seo_topical_architecture


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


if __name__ == "__main__":
    unittest.main()
