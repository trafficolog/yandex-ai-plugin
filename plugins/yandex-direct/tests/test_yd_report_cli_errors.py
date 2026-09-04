import io
import os
import unittest
from unittest.mock import patch

from scripts import yd_report


class ReportCLIErrorBoundaryTests(unittest.TestCase):
    def test_network_failure_is_structured_without_traceback(self):
        stderr = io.StringIO()
        env = {**os.environ, "YANDEX_DIRECT_TOKEN": "env-secret"}
        with patch.dict(os.environ, env, clear=True):
            with patch("sys.stderr", stderr):
                with patch.object(
                    yd_report,
                    "fetch_report",
                    side_effect=yd_report.ReportError(
                        "Direct Reports network error: temporary DNS failure",
                        error_type="network",
                    ),
                ):
                    rc = yd_report.main(["campaign", "2026-08-01", "2026-08-31"])

        self.assertEqual(rc, 2)
        text = stderr.getvalue()
        self.assertIn('"type": "network"', text)
        self.assertIn("temporary DNS failure", text)
        self.assertNotIn("Traceback", text)
        self.assertNotIn("env-secret", text)


if __name__ == "__main__":
    unittest.main()
