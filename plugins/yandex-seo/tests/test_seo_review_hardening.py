import unittest

from scripts import seo_internal_linking, seo_topical_architecture


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

    def test_audit_reports_observed_link_without_structural_or_semantic_justification(self):
        architecture = {
            "schema": "seo-topical-architecture/v1",
            "structural_tree": {
                "nodes": [
                    {"page_id": "a", "canonical_parent_id": None},
                    {"page_id": "b", "canonical_parent_id": None},
                ],
                "edges": [],
            },
            "semantic_graph": {
                "nodes": [{"page_id": "a"}, {"page_id": "b"}],
                "edges": [],
            },
        }
        audit = seo_internal_linking.audit_link_inventory(
            architecture=architecture,
            existing_links=[{"from_page_id": "a", "to_page_id": "b"}],
        )
        findings = [item for item in audit["findings"] if item["type"] == "UNJUSTIFIED_LINK"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["from_page_id"], "a")
        self.assertEqual(findings[0]["to_page_id"], "b")

    def test_proposed_parentless_page_requires_root_or_bridge_role(self):
        with self.assertRaises(ValueError):
            seo_topical_architecture.build_topical_architecture(
                mode="GREENFIELD",
                coverage=COVERAGE,
                clusters=[],
                page_decisions=[],
                structural_nodes=[{
                    "page_id": "orphan",
                    "proposed_url": "/orphan/",
                    "canonical_parent_id": None,
                    "breadcrumbs": [],
                    "cluster_ids": [],
                    "evidence": [],
                    "confidence": "LOW",
                }],
                semantic_edges=[],
            )

        result = seo_topical_architecture.build_topical_architecture(
            mode="GREENFIELD",
            coverage=COVERAGE,
            clusters=[],
            page_decisions=[],
            structural_nodes=[{
                "page_id": "root",
                "proposed_url": "/",
                "page_role": "ROOT",
                "canonical_parent_id": None,
                "breadcrumbs": [],
                "cluster_ids": [],
                "evidence": ["USER_BUSINESS_CONSTRAINT"],
                "confidence": "MEDIUM",
            }],
            semantic_edges=[],
        )
        self.assertEqual(result["structural_tree"]["nodes"][0]["page_role"], "ROOT")


if __name__ == "__main__":
    unittest.main()
