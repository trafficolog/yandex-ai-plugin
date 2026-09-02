import unittest

from scripts.ys_request import build_search_request, config_fingerprint


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

    def test_fingerprint_is_stable_and_ignores_query_text(self):
        left = build_search_request("one", folder_id="f", api_key="k", region=213)
        right = build_search_request("two", folder_id="f", api_key="k", region=213)
        self.assertEqual(config_fingerprint(left["body"]), config_fingerprint(right["body"]))


if __name__ == "__main__":
    unittest.main()
