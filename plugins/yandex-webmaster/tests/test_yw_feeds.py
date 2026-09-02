import unittest
from scripts import yw_feeds


class TestFeeds(unittest.TestCase):
    def test_https_host_required_for_mutation(self):
        yw_feeds.validate_host_https("https://example.com")
        with self.assertRaises(ValueError):
            yw_feeds.validate_host_https("http://example.com")

    def test_list_start_status_paths(self):
        listing = yw_feeds.list_request(1, "h")
        start = yw_feeds.start_request(1, "h", host_url="https://example.com", feed_url="https://example.com/feed.yml", feed_type="GOODS", region_ids=[213])
        status = yw_feeds.status_request(1, "h", "req-1")
        self.assertTrue(listing["path"].endswith("/feeds/list"))
        self.assertTrue(start["path"].endswith("/feeds/add/start"))
        self.assertEqual(start["body"]["type"], "GOODS")
        self.assertEqual(start["body"]["regionIds"], [213])
        self.assertTrue(status["path"].endswith("/feeds/add/info"))
        self.assertEqual(status["params"]["requestId"], "req-1")

    def test_batch_add_wraps_feeds_key_and_limits_batch_size(self):
        feed = {"url": "https://example.com/feed.yml", "type": "GOODS"}
        req = yw_feeds.batch_add_request(1, "h", host_url="https://example.com", feeds=[feed])
        self.assertEqual(req["body"], {"feeds": [feed]})
        req50 = yw_feeds.batch_add_request(1, "h", host_url="https://example.com", feeds=[feed] * 50)
        self.assertEqual(len(req50["body"]["feeds"]), 50)
        with self.assertRaises(ValueError):
            yw_feeds.batch_add_request(1, "h", host_url="https://example.com", feeds=[])
        with self.assertRaises(ValueError):
            yw_feeds.batch_add_request(1, "h", host_url="https://example.com", feeds=[feed] * 51)

    def test_delete_is_batch_remove_and_destructive(self):
        req = yw_feeds.delete_request(1, "h", host_url="https://example.com", urls=["https://example.com/feed.yml"])
        self.assertEqual(req["method"], "DELETE")
        self.assertTrue(req["path"].endswith("/feeds/batch/remove"))
        self.assertEqual(req["body"], {"urls": ["https://example.com/feed.yml"]})
        with self.assertRaises(ValueError):
            yw_feeds.delete_request(1, "h", host_url="https://example.com", urls=[])


if __name__ == "__main__":
    unittest.main()
