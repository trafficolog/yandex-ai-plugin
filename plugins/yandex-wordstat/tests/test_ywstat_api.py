import unittest

from scripts import _http, ywstat_api


class TestWordstatApi(unittest.TestCase):
    def test_api_key_header_and_redaction(self):
        headers = _http.auth_headers(api_key="secret")
        self.assertEqual(headers["Authorization"], "Api-Key secret")
        self.assertEqual(_http.redact_headers(headers)["Authorization"], "Api-Key ***")

    def test_iam_header_and_redaction(self):
        headers = _http.auth_headers(iam_token="iam-secret")
        self.assertEqual(headers["Authorization"], "Bearer iam-secret")
        self.assertEqual(_http.redact_headers(headers)["Authorization"], "Bearer ***")

    def test_credentials_are_mutually_exclusive(self):
        with self.assertRaises(ValueError):
            _http.auth_headers(api_key="a", iam_token="b")
        with self.assertRaises(ValueError):
            _http.auth_headers()

    def test_folder_id_is_optional_and_trimmed(self):
        self.assertIsNone(ywstat_api.validate_folder_id(None))
        self.assertEqual(ywstat_api.validate_folder_id(" folder-123 "), "folder-123")
        self.assertEqual(len(ywstat_api.validate_folder_id("x" * 50)), 50)
        with self.assertRaises(ValueError):
            ywstat_api.validate_folder_id(" ")
        with self.assertRaises(ValueError):
            ywstat_api.validate_folder_id("x" * 51)

    def test_endpoint_mapping_and_folder_injection(self):
        req = ywstat_api.build_request(
            "top",
            {"phrase": "зубная паста", "numPhrases": 50},
            api_key="secret",
            folder_id="folder",
        )
        self.assertEqual(req["url"], "https://searchapi.api.cloud.yandex.net/v2/wordstat/topRequests")
        self.assertEqual(req["body"]["folderId"], "folder")
        self.assertEqual(req["headers"]["Authorization"], "Api-Key ***")
        self.assertNotIn("secret", repr(req))
        for method, endpoint in {
            "dynamics": "dynamics",
            "regions": "regions",
            "regions_tree": "getRegionsTree",
        }.items():
            self.assertTrue(ywstat_api.build_request(method, {}, iam_token="t")["url"].endswith(endpoint))
        with self.assertRaises(ValueError):
            ywstat_api.build_request("unknown", {}, api_key="x")

    def test_execute_uses_credentials_supplied_at_execution_time(self):
        calls = []
        def transport(method, url, headers, body):
            calls.append((method, url, headers, body))
            return {"ok": True}
        req = ywstat_api.build_request("regions_tree", {}, api_key="x")
        result = ywstat_api.execute_request(req, api_key="x", transport=transport)
        self.assertEqual(result, {"ok": True})
        self.assertEqual(calls[0][2]["Authorization"], "Api-Key x")
        self.assertNotIn("Api-Key x", repr(req))

    def test_cost_estimate(self):
        result = ywstat_api.estimate_cost({"top": 20, "dynamics": 10, "regions": 4, "regions_tree": 3})
        self.assertAlmostEqual(result["estimated_rub"], 0.8)
        self.assertEqual(result["verified_at"], "2026-09-01")
        self.assertEqual(result["requests"], 37)

    def test_quota_plan(self):
        fits = ywstat_api.plan_quota({"top": 20, "dynamics": 40, "regions": 5})
        self.assertTrue(fits["fits_safety_budget"])
        self.assertEqual(fits["requests"], 65)
        self.assertEqual(fits["hourly_safety_budget"], 90)
        overflow = ywstat_api.plan_quota({"top": 91})
        self.assertFalse(overflow["fits_safety_budget"])
        self.assertEqual(overflow["minimum_hourly_windows"], 2)


if __name__ == "__main__":
    unittest.main()
