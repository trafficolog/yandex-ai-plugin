import io
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from scripts import yd_api
from scripts._approval import preview_id
from scripts.yd_api import YandexDirectClient


class DirectSandboxTests(unittest.TestCase):
    def test_production_and_sandbox_use_explicit_documented_bases(self):
        production = YandexDirectClient("token", environment="production")
        sandbox = YandexDirectClient("token", environment="sandbox")
        self.assertEqual(
            production.endpoint("campaigns"),
            "https://api.direct.yandex.com/json/v501/campaigns",
        )
        self.assertEqual(
            sandbox.endpoint("campaigns"),
            "https://api-sandbox.direct.yandex.com/json/v5/campaigns",
        )

    def test_environment_is_bound_into_approval(self):
        params = {"Campaigns": [{"Id": 123}]}
        production = YandexDirectClient("token", environment="production")
        sandbox = YandexDirectClient("token", environment="sandbox")
        production_id = preview_id(production.approval_envelope("campaigns", "update", params))
        sandbox_id = preview_id(sandbox.approval_envelope("campaigns", "update", params))
        self.assertNotEqual(production_id, sandbox_id)

        with patch("scripts.yd_api._http.request_json") as request_json:
            with self.assertRaises(ValueError):
                sandbox.request("campaigns", "update", params, approve=production_id)
        request_json.assert_not_called()

    def test_cli_sandbox_flag_selects_sandbox_client(self):
        captured = {}

        def fake_request(self, service, method, params, *, dry_run=False, approve=None):
            captured["environment"] = self.environment
            return {"result": {}}

        with patch.dict(os.environ, {"YANDEX_DIRECT_TOKEN": "token"}, clear=False):
            with patch.object(yd_api.YandexDirectClient, "request", new=fake_request):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    rc = yd_api.main(["campaigns", "get", "--params", "{}", "--sandbox"])
        self.assertEqual(rc, 0)
        self.assertEqual(captured["environment"], "sandbox")


if __name__ == "__main__":
    unittest.main()
