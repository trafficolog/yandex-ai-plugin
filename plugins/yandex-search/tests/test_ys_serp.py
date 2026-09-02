import unittest

from scripts.ys_serp import build_snapshot, normalize_url


class TestSerp(unittest.TestCase):
    def test_url_normalization_is_conservative(self):
        self.assertEqual(
            normalize_url("HTTPS://WWW.Example.COM:443/path?b=2&a=1#frag"),
            "https://www.example.com/path?a=1&b=2",
        )
        self.assertNotEqual(
            normalize_url("https://x.test/p?id=1"),
            normalize_url("https://x.test/p?id=2"),
        )

    def test_empty_path_normalizes_to_slash(self):
        self.assertEqual(normalize_url("https://example.com"), "https://example.com/")

    def test_snapshot_has_fingerprint_and_url_keys(self):
        snap = build_snapshot(
            "q",
            [{"rank": 1, "url": "https://A.test/x#f", "title": "A", "snippet": "", "domain": "A.test", "modified_at": None}],
            search_type="SEARCH_TYPE_RU",
            region=213,
        )
        self.assertEqual(snap["results"][0]["url_key"], "https://a.test/x")
        self.assertEqual(len(snap["config_fingerprint"]), 20)
        self.assertEqual(snap["group_mode"], "GROUP_MODE_FLAT")
        self.assertEqual(snap["max_supported_results"], 250)
        self.assertEqual(snap["window_start"], 0)
        self.assertEqual(snap["window_end"], 20)
        self.assertFalse(snap["reaches_result_ceiling"])

    def test_second_page_rank_is_absolute(self):
        snap = build_snapshot(
            "q",
            [{"rank": 1, "url": "https://example.test/a", "title": "A", "snippet": "", "domain": "example.test", "modified_at": None}],
            page=1,
            groups_on_page=20,
        )
        self.assertEqual(snap["results"][0]["position_on_page"], 1)
        self.assertEqual(snap["results"][0]["rank"], 21)

    def test_snapshot_window_ending_at_250_is_recorded(self):
        snap = build_snapshot("q", [], page=4, groups_on_page=50)
        self.assertEqual(snap["window_start"], 200)
        self.assertEqual(snap["window_end"], 250)
        self.assertTrue(snap["reaches_result_ceiling"])

    def test_snapshot_rejects_window_crossing_250(self):
        with self.assertRaises(ValueError):
            build_snapshot("q", [], page=4, groups_on_page=60)

    def test_snapshot_cannot_observe_absolute_rank_above_250(self):
        results = [
            {"url": f"https://example.test/{index}", "title": str(index), "snippet": "", "domain": "example.test", "modified_at": None}
            for index in range(51)
        ]
        with self.assertRaises(ValueError):
            build_snapshot("q", results, page=4, groups_on_page=50)

    def test_clustering_snapshot_must_be_flat(self):
        with self.assertRaises(ValueError):
            build_snapshot("q", [], group_mode="GROUP_MODE_DEEP")


if __name__ == "__main__":
    unittest.main()
