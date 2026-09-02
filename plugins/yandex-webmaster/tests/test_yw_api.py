import unittest

from scripts import _http, yw_api


class TestWebmasterApi(unittest.TestCase):
    def test_oauth_header_and_redaction(self):
        headers = _http.auth_headers("secret")
        self.assertEqual(headers["Authorization"], "OAuth secret")
        self.assertEqual(_http.redact_headers(headers)["Authorization"], "OAuth ***")

    def test_v4_url_encodes_query(self):
        url = yw_api.api_url("user/123/hosts", params={"offset": 10, "tag": ["a", "b"]})
        self.assertTrue(url.startswith("https://api.webmaster.yandex.net/v4/user/123/hosts?"))
        self.assertIn("offset=10", url)
        self.assertIn("tag=a", url)
        self.assertIn("tag=b", url)

    def test_v41_url_is_explicit(self):
        url = yw_api.api_url("user/1/hosts/h/sitemaps/recrawl", version="v4.1")
        self.assertEqual(url, "https://api.webmaster.yandex.net/v4.1/user/1/hosts/h/sitemaps/recrawl")

    def test_prepare_write_request_redacts_token(self):
        preview = yw_api.prepare_request(method="POST", path="user/1/hosts", token="secret", body={"host_url": "https://example.com"})
        self.assertTrue(preview["consequential"])
        self.assertEqual(preview["headers"]["Authorization"], "OAuth ***")
        self.assertEqual(preview["body"]["host_url"], "https://example.com")

    def test_preview_does_not_execute_transport(self):
        calls = []
        result = yw_api.run_request(
            method="POST",
            path="user/1/hosts",
            token="secret",
            body={"host_url": "https://example.com"},
            execute=False,
            transport=lambda **kwargs: calls.append(kwargs),
        )
        self.assertEqual(calls, [])
        self.assertTrue(result["dry_run"])

    def test_api_version_is_restricted(self):
        with self.assertRaises(ValueError):
            yw_api.api_url("user", version="v999")


if __name__ == "__main__":
    unittest.main()
