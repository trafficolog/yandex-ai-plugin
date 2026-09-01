import json
import unittest
from scripts.yd_api import YandexDirectClient, WRITE_METHODS


class TestYandexDirectClient(unittest.TestCase):
    def test_uses_v501_endpoint(self):
        client = YandexDirectClient("token")
        self.assertEqual(
            client.endpoint("campaigns"),
            "https://api.direct.yandex.com/json/v501/campaigns",
        )

    def test_client_login_header_is_optional(self):
        without_login = YandexDirectClient("token").headers()
        with_login = YandexDirectClient("token", client_login="agency-client").headers()
        self.assertNotIn("Client-Login", without_login)
        self.assertEqual(with_login["Client-Login"], "agency-client")

    def test_dry_run_redacts_token(self):
        client = YandexDirectClient("secret-token", client_login="client")
        preview = client.request("campaigns", "update", {"Campaigns": [{"Id": 123}]}, dry_run=True)
        self.assertTrue(preview["dry_run"])
        self.assertEqual(preview["headers"]["Authorization"], "Bearer ***REDACTED***")
        self.assertEqual(preview["body"]["method"], "update")

    def test_write_methods_include_budget_affecting_mutations(self):
        for method in {"add", "update", "delete", "suspend", "resume", "archive", "unarchive", "setAuto"}:
            self.assertIn(method, WRITE_METHODS)


if __name__ == "__main__":
    unittest.main()
