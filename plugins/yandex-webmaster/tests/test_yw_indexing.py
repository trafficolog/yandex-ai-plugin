import unittest
from scripts import yw_indexing


class TestIndexing(unittest.TestCase):
    def test_indexing_history_path(self):
        req = yw_indexing.indexing_history_request(1, "h", date_from="2026-08-01", date_to="2026-08-31")
        self.assertTrue(req["path"].endswith("/indexing/history"))
        self.assertEqual(req["params"]["date_from"], "2026-08-01")

    def test_in_search_history_path(self):
        req = yw_indexing.in_search_request(1, "h", date_from="2026-08-01", date_to="2026-08-31")
        self.assertTrue(req["path"].endswith("/search-urls/in-search/history"))

    def test_search_events_history_path(self):
        req = yw_indexing.search_events_request(1, "h", date_from="2026-08-01", date_to="2026-08-31")
        self.assertTrue(req["path"].endswith("/search-urls/events/history"))

    def test_archive_lifecycle(self):
        start = yw_indexing.archive_start_request(1, "h")
        status = yw_indexing.archive_status_request(1, "h", "task-1")
        self.assertEqual(start["method"], "POST")
        self.assertTrue(start["path"].endswith("/indexing/archive"))
        self.assertEqual(status["method"], "GET")
        self.assertTrue(status["path"].endswith("/indexing/archive/task-1"))
        self.assertEqual(yw_indexing.archive_download_url({"state": "DONE", "download_url": "https://storage/x"}), "https://storage/x")
        self.assertIsNone(yw_indexing.archive_download_url({"state": "IN_PROGRESS"}))

    def test_archive_download_url_rejects_non_https(self):
        for url in ["file:///etc/passwd", "http://127.0.0.1/archive"]:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    yw_indexing.archive_download_url({"state": "DONE", "download_url": url})


if __name__ == "__main__":
    unittest.main()
