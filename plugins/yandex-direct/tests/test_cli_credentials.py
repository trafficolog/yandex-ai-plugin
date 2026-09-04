import io
import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from scripts import yd_api


class DirectCLICredentialTests(unittest.TestCase):
    def test_token_argument_is_rejected_without_echoing_secret(self):
        secret = "argv-token-secret"
        for argv in [
            ["campaigns", "get", "--params", "{}", "--token", secret],
            ["campaigns", "get", "--params", "{}", f"--token={secret}"],
        ]:
            with self.subTest(argv=argv):
                stderr = io.StringIO()
                with patch.dict(os.environ, {"YANDEX_DIRECT_TOKEN": "env-token"}, clear=False):
                    with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                        rc = yd_api.main(argv)
                self.assertEqual(rc, 2)
                self.assertNotIn(secret, stderr.getvalue())
                payload = json.loads(stderr.getvalue())
                self.assertEqual(payload["error"]["type"], "validation")
                self.assertIn("--token", payload["error"]["message"])
                self.assertIn("YANDEX_DIRECT_TOKEN", payload["error"]["message"])

    def test_missing_env_token_returns_structured_error_without_transport(self):
        stderr = io.StringIO()
        env = dict(os.environ)
        env.pop("YANDEX_DIRECT_TOKEN", None)
        with patch.dict(os.environ, env, clear=True):
            with patch("scripts.yd_api._http.request_json") as request_json:
                with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                    rc = yd_api.main(["campaigns", "get", "--params", "{}"])
        self.assertEqual(rc, 2)
        request_json.assert_not_called()
        payload = json.loads(stderr.getvalue())
        self.assertEqual(payload["error"]["type"], "validation")
        self.assertIn("YANDEX_DIRECT_TOKEN", payload["error"]["message"])

    def test_env_token_is_used(self):
        captured = {}

        def fake_request(self, service, method, params, *, dry_run=False, approve=None):
            captured["token"] = self.token
            return {"result": {}}

        with patch.dict(os.environ, {"YANDEX_DIRECT_TOKEN": "env-token"}, clear=False):
            with patch.object(yd_api.YandexDirectClient, "request", new=fake_request):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    rc = yd_api.main(["campaigns", "get", "--params", "{}"])
        self.assertEqual(rc, 0)
        self.assertEqual(captured["token"], "env-token")


if __name__ == "__main__":
    unittest.main()
