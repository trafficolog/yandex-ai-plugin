import unittest

from scripts import seo_topical_architecture


COVERAGE = {
    "wordstat": "COMPLETE",
    "search": "COMPLETE",
    "webmaster": "COMPLETE",
    "metrika": "PARTIAL",
    "site_inventory": "COMPLETE",
}

NODES = [
    {
        "page_id": "legacy",
        "url": "/legacy/",
        "canonical_parent_id": None,
        "cluster_ids": [],
        "evidence": ["WEBMASTER_EXISTING_URL"],
        "confidence": "MEDIUM",
    },
    {
        "page_id": "target",
        "url": "/target/",
        "canonical_parent_id": None,
        "cluster_ids": [],
        "evidence": ["WEBMASTER_EXISTING_URL"],
        "confidence": "MEDIUM",
    },
]


def build_with(decision):
    return seo_topical_architecture.build_topical_architecture(
        mode="EXISTING_SITE",
        coverage=COVERAGE,
        clusters=[],
        page_decisions=[decision],
        structural_nodes=NODES,
        semantic_edges=[],
    )


class TestSeoDecisionTargets(unittest.TestCase):
    def test_target_page_id_must_reference_known_architecture_page(self):
        with self.assertRaises(ValueError):
            build_with({
                "page_id": "legacy",
                "decision": "MERGE",
                "target_page_id": "missing",
                "cluster_ids": [],
                "evidence": ["WEBMASTER_EXISTING_URL"],
                "confidence": "MEDIUM",
                "claim_class": "DERIVED",
            })

        result = build_with({
            "page_id": "legacy",
            "decision": "MERGE",
            "target_page_id": "target",
            "cluster_ids": [],
            "evidence": ["WEBMASTER_EXISTING_URL"],
            "confidence": "MEDIUM",
            "claim_class": "DERIVED",
        })
        self.assertEqual(result["page_decisions"][0]["target_page_id"], "target")

    def test_target_url_must_be_nonempty_string_when_supplied(self):
        for invalid in ({"url": "/target/"}, "", "   "):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    build_with({
                        "page_id": "legacy",
                        "decision": "REDIRECT",
                        "target_url": invalid,
                        "cluster_ids": [],
                        "evidence": ["WEBMASTER_EXISTING_URL"],
                        "confidence": "MEDIUM",
                        "claim_class": "DERIVED",
                    })

        result = build_with({
            "page_id": "legacy",
            "decision": "REDIRECT",
            "target_url": "/target/",
            "cluster_ids": [],
            "evidence": ["WEBMASTER_EXISTING_URL"],
            "confidence": "MEDIUM",
            "claim_class": "DERIVED",
        })
        self.assertEqual(result["page_decisions"][0]["target_url"], "/target/")


if __name__ == "__main__":
    unittest.main()
