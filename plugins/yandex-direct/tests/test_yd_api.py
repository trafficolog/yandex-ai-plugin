import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from scripts import yd_api
from scripts.yd_api import YandexDirectClient


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

    def _run_cli_and_capture_dry_run(self, method: str) -> bool:
        captured = {}

        def fake_request(self, service, request_method, params, *, dry_run=False):
            captured["service"] = service
            captured["method"] = request_method
            captured["dry_run"] = dry_run
            return {"dry_run": dry_run}

        with patch.object(yd_api.YandexDirectClient, "request", new=fake_request):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                rc = yd_api.main(["bids", method, "--params", "{}", "--token", "token"])
        self.assertEqual(rc, 0)
        return captured["dry_run"]

    def test_set_defaults_to_preview_without_execute(self):
        self.assertTrue(self._run_cli_and_capture_dry_run("set"))

    def test_unknown_method_defaults_to_preview_without_execute(self):
        self.assertTrue(self._run_cli_and_capture_dry_run("frobnicate"))

    def test_known_read_method_executes_without_execute(self):
        self.assertFalse(self._run_cli_and_capture_dry_run("get"))

    def test_method_classification_is_case_insensitive(self):
        self.assertFalse(self._run_cli_and_capture_dry_run("GET"))
        self.assertTrue(self._run_cli_and_capture_dry_run("Set"))


if __name__ == "__main__":
    unittest.main()
