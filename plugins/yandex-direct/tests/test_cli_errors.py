import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from scripts import yd_api
from scripts.yd_api import YandexDirectError


class DirectCLIErrorTests(unittest.TestCase):
    def run_cli(self, argv, *, request_error=None):
        stderr = io.StringIO()
        stdout = io.StringIO()
        env = dict(os.environ)
        env["YANDEX_DIRECT_TOKEN"] = "token"
        patcher = patch.object(yd_api.YandexDirectClient, "request")
        with patch.dict(os.environ, env, clear=True):
            with patcher as request:
                if request_error is None:
                    request.return_value = {"result": {}}
                else:
                    request.side_effect = request_error
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    rc = yd_api.main(argv)
        return rc, stdout.getvalue(), stderr.getvalue(), request

    def assert_structured_error(self, rc, stderr, expected_type):
        self.assertEqual(rc, 2)
        self.assertNotIn("Traceback", stderr)
        payload = json.loads(stderr)
        self.assertEqual(payload["error"]["type"], expected_type)
        self.assertTrue(payload["error"]["message"])

    def test_non_object_params_is_validation_error(self):
        rc, _stdout, stderr, _request = self.run_cli(["campaigns", "get", "--params", "[]"])
        self.assert_structured_error(rc, stderr, "validation")

    def test_malformed_json_is_input_error(self):
        rc, _stdout, stderr, _request = self.run_cli(["campaigns", "get", "--params", "{"])
        self.assert_structured_error(rc, stderr, "input")

    def test_missing_params_file_is_input_error(self):
        rc, _stdout, stderr, _request = self.run_cli(
            ["campaigns", "get", "--params-file", "/definitely/missing/direct-params.json"]
        )
        self.assert_structured_error(rc, stderr, "input")

    def test_network_error_is_structured(self):
        rc, _stdout, stderr, _request = self.run_cli(
            ["campaigns", "get", "--params", "{}"],
            request_error=YandexDirectError("Network error: offline", error_type="network"),
        )
        self.assert_structured_error(rc, stderr, "network")

    def test_http_error_is_structured(self):
        rc, _stdout, stderr, _request = self.run_cli(
            ["campaigns", "get", "--params", "{}"],
            request_error=YandexDirectError("HTTP 500: bounded body", error_type="http"),
        )
        self.assert_structured_error(rc, stderr, "http")

    def test_api_error_is_structured(self):
        rc, _stdout, stderr, _request = self.run_cli(
            ["campaigns", "get", "--params", "{}"],
            request_error=YandexDirectError("Yandex Direct API error", error_type="api"),
        )
        self.assert_structured_error(rc, stderr, "api")


if __name__ == "__main__":
    unittest.main()
