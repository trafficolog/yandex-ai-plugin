import unittest

from scripts._http import oauth_headers, redact_headers
from scripts.ym_api import build_management_url, is_consequential, prepare_request


class TestMetrikaApi(unittest.TestCase):
    def test_oauth_header_and_redaction(self):
        self.assertEqual(oauth_headers("secret")["Authorization"], "OAuth secret")
        self.assertEqual(
            redact_headers({"Authorization": "OAuth secret", "Accept": "application/json"}),
            {"Authorization": "OAuth ***", "Accept": "application/json"},
        )

    def test_management_url_encodes_query(self):
        self.assertEqual(
            build_management_url("counters", {"per_page": 10, "search_string": "мой сайт"}),
            "https://api-metrika.yandex.net/management/v1/counters?per_page=10&search_string=%D0%BC%D0%BE%D0%B9+%D1%81%D0%B0%D0%B9%D1%82",
        )

    def test_write_methods_are_consequential(self):
        self.assertFalse(is_consequential("GET"))
        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.assertTrue(is_consequential(method), method)

    def test_prepare_write_request_redacts_token(self):
        preview = prepare_request(
            method="POST",
            path="counter/123/goals",
            token="secret",
            body={"goal": {"name": "Lead"}},
        )
        self.assertEqual(preview["headers"]["Authorization"], "OAuth ***")
        self.assertEqual(preview["method"], "POST")
        self.assertEqual(preview["body"], {"goal": {"name": "Lead"}})


if __name__ == "__main__":
    unittest.main()
