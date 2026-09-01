import unittest
from scripts import yw_sitemaps


class TestSitemaps(unittest.TestCase):
    def test_endpoint_versions(self):
        self.assertEqual(yw_sitemaps.endpoint_version("list"), "v4")
        self.assertEqual(yw_sitemaps.endpoint_version("add"), "v4")
        self.assertEqual(yw_sitemaps.endpoint_version("priority_recrawl"), "v4.1")
        self.assertEqual(yw_sitemaps.endpoint_version("priority_limit"), "v4.1")
        with self.assertRaises(ValueError):
            yw_sitemaps.endpoint_version("unknown")

    def test_list_add_delete_paths(self):
        listing = yw_sitemaps.list_request(1, "h")
        added = yw_sitemaps.add_request(1, "h", "https://example.com/sitemap.xml")
        deleted = yw_sitemaps.delete_request(1, "h", "sid")
        self.assertTrue(listing["path"].endswith("/sitemaps"))
        self.assertTrue(added["path"].endswith("/user-added-sitemaps"))
        self.assertEqual(added["body"], {"url": "https://example.com/sitemap.xml"})
        self.assertTrue(deleted["path"].endswith("/user-added-sitemaps/sid"))
        self.assertEqual(deleted["method"], "DELETE")

    def test_priority_recrawl_uses_v41(self):
        limit = yw_sitemaps.priority_limit_request(1, "h")
        req = yw_sitemaps.priority_recrawl_request(1, "h", "sid", parent_id="parent")
        self.assertEqual(limit["version"], "v4.1")
        self.assertTrue(limit["path"].endswith("/sitemaps/recrawl"))
        self.assertEqual(req["version"], "v4.1")
        self.assertTrue(req["path"].endswith("/sitemaps/sid/recrawl"))
        self.assertEqual(req["params"]["parent_id"], "parent")

    def test_priority_state_exposes_quota(self):
        state = yw_sitemaps.priority_state({
            "sitemap_recrawl_info": {"pending": True, "allowed": False},
            "host_sitemaps_recrawl_limit_info": {"monthly_limit_requests": 10, "requests_count": 4, "nearest_allowed_day": "2026-09-03"}
        })
        self.assertTrue(state["pending"])
        self.assertFalse(state["allowed"])
        self.assertEqual(state["monthly_limit_requests"], 10)
        self.assertEqual(state["nearest_allowed_day"], "2026-09-03")


if __name__ == "__main__":
    unittest.main()
