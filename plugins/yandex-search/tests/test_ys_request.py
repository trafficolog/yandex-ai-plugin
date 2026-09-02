import unittest

from scripts.ys_request import MAX_RESULTS, build_search_request, config_fingerprint


class TestSearchRequest(unittest.TestCase):
    def test_sync_rest_body_uses_camel_case(self):
        request = build_search_request("hello", folder_id="folder", api_key="key", region=213)
        self.assertTrue(request["url"].endswith("/v2/web/search"))
        self.assertEqual(request["body"]["query"]["queryText"], "hello")
        self.assertEqual(request["body"]["folderId"], "folder")
        self.assertEqual(request["body"]["groupSpec"]["groupMode"], "GROUP_MODE_FLAT")
        self.assertEqual(request["body"]["groupSpec"]["docsInGroup"], "1")
        self.assertEqual(request["preview"]["headers"]["Authorization"], "Api-Key ***")

    def test_async_endpoint(self):
        self.assertTrue(build_search_request("hello", folder_id="f", iam_token="t", mode="async")["url"].endswith("/v2/web/searchAsync"))

    def test_invalid_search_type_rejected(self):
        with self.assertRaises(ValueError):
            build_search_request("x", folder_id="f", api_key="k", search_type="SEARCH_TYPE_EN")

    def test_invalid_fix_typo_mode_rejected(self):
        with self.assertRaises(ValueError):
            build_search_request("x", folder_id="f", api_key="k", fix_typo_mode="FIX_TYPO_MODE_MAGIC")

    def test_result_depth_constant(self):
        self.assertEqual(MAX_RESULTS, 250)

    def test_requested_page_cannot_exceed_result_ceiling(self):
        with self.assertRaises(ValueError):
            build_search_request(
                "x", folder_id="f", api_key="k",
                groups_on_page=100, docs_in_group=3,
            )

    def test_complete_window_ending_at_250_is_allowed(self):
        request = build_search_request(
            "x", folder_id="f", api_key="k",
            page=4, groups_on_page=50, docs_in_group=1,
        )
        self.assertEqual(request["body"]["query"]["page"], "4")
        self.assertEqual(request["body"]["groupSpec"]["groupsOnPage"], "50")

    def test_partial_window_crossing_250_is_rejected(self):
        with self.assertRaises(ValueError):
            build_search_request(
                "x", folder_id="f", api_key="k",
                page=4, groups_on_page=60, docs_in_group=1,
            )

    def test_page_starting_at_250_is_rejected(self):
        with self.assertRaises(ValueError):
            build_search_request(
                "x", folder_id="f", api_key="k",
                page=5, groups_on_page=50, docs_in_group=1,
            )

    def test_fingerprint_is_stable_and_ignores_query_text(self):
        left = build_search_request("one", folder_id="f", api_key="k", region=213)
        right = build_search_request("two", folder_id="f", api_key="k", region=213)
        self.assertEqual(config_fingerprint(left["body"]), config_fingerprint(right["body"]))


if __name__ == "__main__":
    unittest.main()
