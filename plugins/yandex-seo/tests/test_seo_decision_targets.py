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


def build_with_decisions(decisions):
    return seo_topical_architecture.build_topical_architecture(
        mode="EXISTING_SITE",
        coverage=COVERAGE,
        clusters=[],
        page_decisions=decisions,
        structural_nodes=NODES,
        semantic_edges=[],
    )


def build_with(decision):
    return build_with_decisions([decision])


class TestSeoDecisionTargets(unittest.TestCase):
    def test_duplicate_page_decisions_are_rejected(self):
        with self.assertRaises(ValueError):
            build_with_decisions([
                {
                    "page_id": "legacy",
                    "decision": "PRESERVE",
                    "cluster_ids": [],
                    "evidence": ["WEBMASTER_EXISTING_URL"],
                    "confidence": "MEDIUM",
                    "claim_class": "OBSERVED",
                },
                {
                    "page_id": "legacy",
                    "decision": "REDIRECT",
                    "target_page_id": "target",
                    "cluster_ids": [],
                    "evidence": ["WEBMASTER_EXISTING_URL"],
                    "confidence": "MEDIUM",
                    "claim_class": "DERIVED",
                },
            ])

    def test_empirical_page_decision_requires_provenance(self):
        for claim_class in ("OBSERVED", "DERIVED"):
            with self.subTest(claim_class=claim_class):
                with self.assertRaises(ValueError):
                    build_with({
                        "page_id": "legacy",
                        "decision": "PRESERVE",
                        "cluster_ids": [],
                        "evidence": [],
                        "confidence": "MEDIUM",
                        "claim_class": claim_class,
                    })

        reason_only = build_with({
            "page_id": "legacy",
            "decision": "PRESERVE",
            "reason_codes": ["WEBMASTER_EXISTING_URL"],
            "cluster_ids": [],
            "evidence": [],
            "confidence": "MEDIUM",
            "claim_class": "OBSERVED",
        })
        self.assertEqual(reason_only["page_decisions"][0]["reason_codes"], ["WEBMASTER_EXISTING_URL"])

        evidence_only = build_with({
            "page_id": "legacy",
            "decision": "PRESERVE",
            "cluster_ids": [],
            "evidence": ["webmaster:page-observed"],
            "confidence": "MEDIUM",
            "claim_class": "OBSERVED",
        })
        self.assertEqual(evidence_only["page_decisions"][0]["evidence"], ["webmaster:page-observed"])

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

    def test_destructive_decision_cannot_target_its_source_page(self):
        for decision in ("MERGE", "REDIRECT"):
            with self.subTest(decision=decision):
                with self.assertRaises(ValueError):
                    build_with({
                        "page_id": "legacy",
                        "decision": decision,
                        "target_page_id": "legacy",
                        "cluster_ids": [],
                        "evidence": ["WEBMASTER_EXISTING_URL"],
                        "confidence": "MEDIUM",
                        "claim_class": "DERIVED",
                    })

    def test_redirect_cannot_target_its_source_url(self):
        with self.assertRaises(ValueError):
            build_with({
                "page_id": "legacy",
                "decision": "REDIRECT",
                "target_url": "/legacy/",
                "cluster_ids": [],
                "evidence": ["WEBMASTER_EXISTING_URL"],
                "confidence": "MEDIUM",
                "claim_class": "DERIVED",
            })

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

    def test_page_decision_rejects_unknown_reason_code(self):
        with self.assertRaises(ValueError):
            build_with({
                "page_id": "legacy",
                "decision": "REDIRECT",
                "target_page_id": "target",
                "reason_codes": ["SERP_OVELRAP"],
                "cluster_ids": [],
                "evidence": ["WEBMASTER_EXISTING_URL"],
                "confidence": "MEDIUM",
                "claim_class": "OBSERVED",
            })

    def test_methodology_only_page_decision_cannot_claim_empirical_evidence(self):
        for claim_class in ("OBSERVED", "DERIVED"):
            with self.subTest(claim_class=claim_class):
                with self.assertRaises(ValueError):
                    build_with({
                        "page_id": "legacy",
                        "decision": "REDIRECT",
                        "target_page_id": "target",
                        "reason_codes": ["METHODOLOGY_HEURISTIC"],
                        "cluster_ids": [],
                        "evidence": [],
                        "confidence": "MEDIUM",
                        "claim_class": claim_class,
                    })

    def test_page_decision_preserves_valid_reason_codes(self):
        result = build_with({
            "page_id": "legacy",
            "decision": "PRESERVE",
            "reason_codes": ["WEBMASTER_EXISTING_URL"],
            "cluster_ids": [],
            "evidence": ["WEBMASTER_EXISTING_URL"],
            "confidence": "MEDIUM",
            "claim_class": "OBSERVED",
        })
        self.assertEqual(result["page_decisions"][0]["reason_codes"], ["WEBMASTER_EXISTING_URL"])


if __name__ == "__main__":
    unittest.main()
