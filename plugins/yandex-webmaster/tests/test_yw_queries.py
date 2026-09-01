import unittest
from scripts import yw_queries


class TestQueries(unittest.TestCase):
    def test_popular_request_defaults_to_top_500(self):
        req = yw_queries.popular_request(1, "https:example.com:443")
        self.assertEqual(req["method"], "GET")
        self.assertIn("/search-queries/popular", req["path"])
        self.assertEqual(req["params"]["limit"], 500)
        self.assertEqual(req["params"]["order_by"], "TOTAL_SHOWS")

    def test_popular_limit_cannot_exceed_500(self):
        with self.assertRaises(ValueError):
            yw_queries.popular_request(1, "h", limit=501)

    def test_query_history_all_and_specific(self):
        all_req = yw_queries.history_request(1, "h", date_from="2026-08-01", date_to="2026-08-31")
        one_req = yw_queries.history_request(1, "h", date_from="2026-08-01", date_to="2026-08-31", query_id="q1")
        self.assertIn("/search-queries/all/history", all_req["path"])
        self.assertIn("/search-queries/q1/history", one_req["path"])

    def test_query_analytics_is_post(self):
        req = yw_queries.analytics_request(1, "h", {"limit": 100, "text_indicator": "QUERY"})
        self.assertEqual(req["method"], "POST")
        self.assertTrue(req["path"].endswith("/query-analytics/list"))
        self.assertEqual(req["body"]["limit"], 100)

    def test_coverage_note_does_not_claim_completeness(self):
        note = yw_queries.coverage_note("popular", returned=500, limit=500)
        self.assertIn("top-N", note)
        self.assertIn("not complete", note)


if __name__ == "__main__":
    unittest.main()
