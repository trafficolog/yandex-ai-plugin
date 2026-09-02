import unittest

from scripts.seo_opportunities import (
    find_content_gaps,
    find_conversion_opportunities,
    find_ctr_opportunities,
    find_technical_blockers,
)


class OpportunityTests(unittest.TestCase):
    def test_discovery_candidate_vs_validated_gap(self):
        partial = {"coverage": {"wordstat": True}, "queries": [{"query_key": "a", "wordstat_count": 1000}]}
        self.assertEqual(find_content_gaps(partial)[0]["type"], "DISCOVERY_CANDIDATE")
        full = {
            "coverage": {"wordstat": True, "search": True, "webmaster": True},
            "queries": [{
                "query_key": "a",
                "wordstat_count": 1000,
                "search_site_present": False,
                "webmaster_impressions": 0,
            }],
        }
        finding = find_content_gaps(full)[0]
        self.assertEqual(finding["type"], "CONTENT_GAP")
        self.assertEqual(finding["kind"], "DERIVED")
        self.assertEqual(finding["confidence"], "HIGH")

    def test_missing_webmaster_impressions_is_not_high_confidence_gap(self):
        bundle = {
            "coverage": {"wordstat": True, "search": True, "webmaster": True},
            "queries": [{
                "query_key": "a",
                "wordstat_count": 1000,
                "search_site_present": False,
                "webmaster_impressions": None,
            }],
        }
        finding = find_content_gaps(bundle)[0]
        self.assertEqual(finding["type"], "DISCOVERY_CANDIDATE")
        self.assertNotEqual(finding["confidence"], "HIGH")
        self.assertIn("WEBMASTER_IMPRESSIONS_UNKNOWN", finding["limitations"])

    def test_webmaster_top_n_lowers_gap_confidence(self):
        bundle = {
            "coverage": {"wordstat": True, "search": True, "webmaster": True},
            "limitations": [{"kind": "WEBMASTER_TOP_N", "top_n": 500}],
            "queries": [{
                "query_key": "a",
                "wordstat_count": 1000,
                "search_site_present": False,
                "webmaster_impressions": 0,
            }],
        }
        finding = find_content_gaps(bundle)[0]
        self.assertEqual(finding["type"], "CONTENT_GAP")
        self.assertEqual(finding["confidence"], "MEDIUM")
        self.assertIn("WEBMASTER_TOP_N", finding["limitations"])

    def test_ctr_uses_own_baseline_only(self):
        bundle = {
            "queries": [
                {"query_key": "a", "webmaster_ctr": 0.04, "own_baseline_ctr": 0.07},
                {"query_key": "b", "webmaster_ctr": 0.04},
            ]
        }
        out = find_ctr_opportunities(bundle)
        self.assertEqual([item["query_key"] for item in out], ["a"])
        self.assertNotIn("benchmark", out[0])

    def test_conversion_mismatch_is_hypothesis(self):
        bundle = {
            "pages": [{
                "url_key": "https://x/p",
                "organic_conversion_rate": 0.01,
                "own_comparable_conversion_rate": 0.04,
                "intent_evidence": True,
            }]
        }
        out = find_conversion_opportunities(bundle)
        self.assertEqual(out[0]["kind"], "HYPOTHESIS")
        self.assertEqual(out[0]["type"], "LANDING_OR_INTENT_MISMATCH")

    def test_technical_blocker_is_correlation_not_cause(self):
        bundle = {"pages": [{"url_key": "https://x/p", "technical_issue": "NOT_INDEXED", "opportunity_evidence": True}]}
        out = find_technical_blockers(bundle)
        self.assertEqual(out[0]["kind"], "DERIVED")
        self.assertFalse(out[0]["causal_claim"])


if __name__ == "__main__":
    unittest.main()
