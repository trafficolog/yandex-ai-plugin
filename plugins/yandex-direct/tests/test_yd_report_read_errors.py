import unittest
import urllib.error

from scripts import yd_report


class _FailingResponse:
    status = 200
    headers = {}

    def read(self):
        raise TimeoutError("response read timed out")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FailingBody:
    def __init__(self):
        self.closed = False

    def read(self, size=-1):
        raise OSError("socket reset while reading error body")

    def close(self):
        self.closed = True


class ReportReadFailureTests(unittest.TestCase):
    def setUp(self):
        self.body = yd_report.build_report_body(
            "campaign",
            "2026-08-01",
            "2026-08-31",
            report_name="read-failure",
        )

    def test_success_response_read_failure_is_typed_network_error(self):
        def opener(request, timeout=0):
            return _FailingResponse()

        with self.assertRaises(yd_report.ReportError) as ctx:
            yd_report.fetch_report("secret-token-value", self.body, opener=opener)

        self.assertEqual(ctx.exception.error_type, "network")
        self.assertIn("reading response", str(ctx.exception))
        self.assertNotIn("secret-token-value", str(ctx.exception))

    def test_http_error_body_read_failure_is_typed_network_error_and_closed(self):
        failing_body = _FailingBody()
        error = urllib.error.HTTPError(
            yd_report.REPORTS_URL,
            500,
            "server error",
            {},
            failing_body,
        )

        def opener(request, timeout=0):
            raise error

        with self.assertRaises(yd_report.ReportError) as ctx:
            yd_report.fetch_report("secret-token-value", self.body, opener=opener)

        self.assertEqual(ctx.exception.error_type, "network")
        self.assertIn("reading HTTP 500 error response", str(ctx.exception))
        self.assertNotIn("secret-token-value", str(ctx.exception))
        self.assertTrue(failing_body.closed)


if __name__ == "__main__":
    unittest.main()
