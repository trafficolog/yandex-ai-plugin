import unittest
from scripts import yw_recrawl


class TestRecrawl(unittest.TestCase):
    def test_same_host_url_is_valid(self):
        yw_recrawl.validate_url_for_host("https://example.com/a", "https://example.com")

    def test_cross_host_url_is_rejected(self):
        with self.assertRaises(ValueError):
            yw_recrawl.validate_url_for_host("https://evil.example/a", "https://example.com")

    def test_scheme_must_match_selected_host(self):
        with self.assertRaises(ValueError):
            yw_recrawl.validate_url_for_host("http://example.com/a", "https://example.com")

    def test_explicit_default_port_is_equivalent(self):
        yw_recrawl.validate_url_for_host("https://example.com/a", "https://example.com:443")
        yw_recrawl.validate_url_for_host("https://example.com:443/a", "https://example.com")

    def test_quota_and_queue_paths(self):
        quota = yw_recrawl.quota_request(1, "h")
        queue = yw_recrawl.queue_request(1, "h", limit=20)
        self.assertTrue(quota["path"].endswith("/recrawl/quota"))
        self.assertTrue(queue["path"].endswith("/recrawl/queue"))
        self.assertEqual(queue["params"]["limit"], 20)

    def test_submit_request_validates_host(self):
        req = yw_recrawl.submit_request(1, "h", "https://example.com/p", host_url="https://example.com")
        self.assertEqual(req["method"], "POST")
        self.assertEqual(req["body"], {"url": "https://example.com/p"})
        with self.assertRaises(ValueError):
            yw_recrawl.submit_request(1, "h", "https://other.com/p", host_url="https://example.com")

    def test_url_already_added_is_nonfatal(self):
        result = yw_recrawl.normalize_submit_error(409, "URL_ALREADY_ADDED")
        self.assertEqual(result["state"], "already_queued")
        self.assertFalse(result["retry_required"])
        self.assertIsNone(yw_recrawl.normalize_submit_error(400, "BAD_REQUEST"))


if __name__ == "__main__":
    unittest.main()
