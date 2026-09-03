import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from scripts import yd_api
from scripts._approval import preview_id
from scripts.yd_api import YandexDirectClient


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return b'{"result":{"UpdateResults":[]}}'


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

    def test_dry_run_redacts_token_and_emits_preview_id(self):
        client = YandexDirectClient("secret-token", client_login="client")
        preview = client.request("campaigns", "update", {"Campaigns": [{"Id": 123}]}, dry_run=True)
        self.assertTrue(preview["dry_run"])
        self.assertEqual(preview["headers"]["Authorization"], "Bearer ***REDACTED***")
        self.assertEqual(preview["body"]["method"], "update")
        self.assertEqual(preview["preview_id"], preview_id(client.approval_envelope("campaigns", "update", {"Campaigns": [{"Id": 123}]})))

    def test_write_execute_requires_approval_before_transport(self):
        client = YandexDirectClient("token", client_login="client")
        with patch("scripts.yd_api.urllib.request.urlopen") as opener:
            with self.assertRaises(ValueError):
                client.request("campaigns", "update", {"Campaigns": [{"Id": 123}]})
        opener.assert_not_called()

    def test_wrong_approval_does_not_call_transport(self):
        client = YandexDirectClient("token", client_login="client")
        with patch("scripts.yd_api.urllib.request.urlopen") as opener:
            with self.assertRaises(ValueError):
                client.request(
                    "campaigns",
                    "update",
                    {"Campaigns": [{"Id": 123}]},
                    approve="0" * 64,
                )
        opener.assert_not_called()

    def test_exact_approval_calls_transport_once(self):
        client = YandexDirectClient("token", client_login="client")
        params = {"Campaigns": [{"Id": 123}]}
        approve = preview_id(client.approval_envelope("campaigns", "update", params))
        with patch("scripts.yd_api.urllib.request.urlopen", return_value=FakeResponse()) as opener:
            result = client.request("campaigns", "update", params, approve=approve)
        opener.assert_called_once()
        self.assertIn("result", result)

    def test_client_login_change_invalidates_approval(self):
        params = {"Campaigns": [{"Id": 123}]}
        source = YandexDirectClient("token", client_login="client-a")
        approve = preview_id(source.approval_envelope("campaigns", "update", params))
        target = YandexDirectClient("token", client_login="client-b")
        with patch("scripts.yd_api.urllib.request.urlopen") as opener:
            with self.assertRaises(ValueError):
                target.request("campaigns", "update", params, approve=approve)
        opener.assert_not_called()

    def test_service_change_invalidates_approval(self):
        client = YandexDirectClient("token", client_login="client")
        params = {"Campaigns": [{"Id": 123}]}
        approve = preview_id(client.approval_envelope("campaigns", "update", params))
        with patch("scripts.yd_api.urllib.request.urlopen") as opener:
            with self.assertRaises(ValueError):
                client.request("adgroups", "update", params, approve=approve)
        opener.assert_not_called()

    def test_body_change_invalidates_approval(self):
        client = YandexDirectClient("token", client_login="client")
        approved_params = {"Campaigns": [{"Id": 123}]}
        changed_params = {"Campaigns": [{"Id": 124}]}
        approve = preview_id(client.approval_envelope("campaigns", "update", approved_params))
        with patch("scripts.yd_api.urllib.request.urlopen") as opener:
            with self.assertRaises(ValueError):
                client.request("campaigns", "update", changed_params, approve=approve)
        opener.assert_not_called()

    def test_known_read_method_executes_without_approval(self):
        client = YandexDirectClient("token")
        with patch("scripts.yd_api.urllib.request.urlopen", return_value=FakeResponse()) as opener:
            client.request("campaigns", "get", {})
        opener.assert_called_once()

    def _run_cli_and_capture_dry_run(self, method: str) -> bool:
        captured = {}

        def fake_request(self, service, request_method, params, *, dry_run=False, approve=None):
            captured["service"] = service
            captured["method"] = request_method
            captured["dry_run"] = dry_run
            captured["approve"] = approve
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

    def test_method_classification_is_case_insensitive(self):
        self.assertFalse(self._run_cli_and_capture_dry_run("GET"))
        self.assertTrue(self._run_cli_and_capture_dry_run("Set"))

    def test_cli_execute_passes_approval_to_client(self):
        captured = {}

        def fake_request(self, service, request_method, params, *, dry_run=False, approve=None):
            captured["dry_run"] = dry_run
            captured["approve"] = approve
            return {"ok": True}

        with patch.object(yd_api.YandexDirectClient, "request", new=fake_request):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                rc = yd_api.main([
                    "campaigns",
                    "update",
                    "--params",
                    "{}",
                    "--token",
                    "token",
                    "--execute",
                    "--approve",
                    "a" * 64,
                ])
        self.assertEqual(rc, 0)
        self.assertFalse(captured["dry_run"])
        self.assertEqual(captured["approve"], "a" * 64)


if __name__ == "__main__":
    unittest.main()
