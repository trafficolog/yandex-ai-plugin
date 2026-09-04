import io
import os
import unittest
from unittest.mock import patch

from scripts import yd_report


class ReportTokenRedactionTests(unittest.TestCase):
    def test_legacy_token_argument_is_rejected_without_echoing_secret(self):
        secret = "oauth-secret-that-must-not-appear"
        stderr = io.StringIO()
        env = {**os.environ, "YANDEX_DIRECT_TOKEN": "env-token"}
        with patch.dict(os.environ, env, clear=True):
            with patch("sys.stderr", stderr):
                rc = yd_report.main([
                    "campaign",
                    "2026-08-01",
                    "2026-08-31",
                    "--token",
                    secret,
                ])

        self.assertEqual(rc, 2)
        text = stderr.getvalue()
        self.assertIn("--token", text)
        self.assertIn("YANDEX_DIRECT_TOKEN", text)
        self.assertNotIn(secret, text)
        self.assertNotIn("unrecognized arguments", text)


if __name__ == "__main__":
    unittest.main()
