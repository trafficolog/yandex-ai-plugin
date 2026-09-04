import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

from scripts import yd_report
from scripts.yd_report import build_report_body, build_report_metadata, fetch_report, parse_retry_in


class _Response:
    def __init__(self, status: int, body: bytes, headers=None):
        self.status = status
        self._body = body
        self.headers = headers or {}

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _TrackingBody:
    def __init__(self, body: bytes):
        self.body = body
        self.read_sizes = []
        self.closed = False

    def read(self, size=-1):
        self.read_sizes.append(size)
        if size is None or size < 0:
            return self.body
        return self.body[:size]

    def close(self):
        self.closed = True


class TestReportHelpers(unittest.TestCase):
    def test_report_name_is_stable_when_supplied(self):
        body1 = build_report_body("campaign", "2026-08-01", "2026-08-31", report_name="audit-42")
        body2 = build_report_body("campaign", "2026-08-01", "2026-08-31", report_name="audit-42")
        self.assertEqual(body1["params"]["ReportName"], "audit-42")
        self.assertEqual(body1, body2)

    def test_current_criteria_fields_use_criterion_names(self):
        body = build_report_body("criteria", "2026-08-01", "2026-08-31", report_name="criteria")
        fields = body["params"]["FieldNames"]
        self.assertIn("Criterion", fields)
        self.assertIn("CriterionId", fields)
        self.assertIn("CriterionType", fields)
        self.assertNotIn("Criteria", fields)

    def test_retry_in_header_is_case_insensitive(self):
        self.assertEqual(parse_retry_in({"retryIn": "7"}), 7)
        self.assertEqual(parse_retry_in({"Retryin": "11"}), 11)
        self.assertEqual(parse_retry_in({}), 5)

    def test_conversion_reports_make_default_attribution_explicit(self):
        body = build_report_body("campaign", "2026-08-01", "2026-08-31", report_name="campaign")
        self.assertEqual(body["params"]["AttributionModels"], ["LC"])

    def test_report_can_scope_goals_and_attribution(self):
        body = build_report_body(
            "campaign",
            "2026-08-01",
            "2026-08-31",
            report_name="campaign",
            goals=[123, 456],
            attribution_models=["LSCCD"],
        )
        self.assertEqual(body["params"]["Goals"], [123, 456])
        self.assertEqual(body["params"]["AttributionModels"], ["LSCCD"])

    def test_report_metadata_preserves_kpi_context_without_inventing_currency(self):
        body = build_report_body(
            "campaign",
            "2026-08-01",
            "2026-08-31",
            report_name="campaign",
            include_vat="NO",
            goals=[123],
            attribution_models=["AUTO"],
        )
        metadata = build_report_metadata("campaign", body)
        self.assertEqual(metadata["period"], {"from": "2026-08-01", "to": "2026-08-31"})
        self.assertEqual(metadata["goal_ids"], [123])
        self.assertEqual(metadata["attribution_models"], ["AUTO"])
        self.assertEqual(metadata["vat_basis"], "excluded")
        self.assertIsNone(metadata["currency"])
        self.assertEqual(metadata["currency_source"], "not_returned_by_reports_helper")

    def test_output_writes_metadata_sidecar_with_env_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.tsv"
            env = {**os.environ, "YANDEX_DIRECT_TOKEN": "token"}
            with patch.dict(os.environ, env, clear=True):
                with patch.object(yd_report, "fetch_report", return_value="Date\tClicks\n2026-08-01\t1\n"):
                    rc = yd_report.main([
                        "campaign", "2026-08-01", "2026-08-31",
                        "--output", str(output),
                        "--goals", "123", "--attribution-models", "AUTO",
                    ])
            self.assertEqual(rc, 0)
            sidecar = Path(str(output) + ".metadata.json")
            self.assertTrue(sidecar.is_file())
            metadata = json.loads(sidecar.read_text(encoding="utf-8"))
            self.assertEqual(metadata["goal_ids"], ["123"])
            self.assertEqual(metadata["attribution_models"], ["AUTO"])

    def test_cli_rejects_token_argument(self):
        env = {**os.environ, "YANDEX_DIRECT_TOKEN": "env-token"}
        stderr = io.StringIO()
        with patch.dict(os.environ, env, clear=True):
            with patch("sys.stderr", stderr):
                with patch.object(yd_report, "fetch_report", return_value="Date\tClicks\n"):
                    rc = yd_report.main([
                        "campaign", "2026-08-01", "2026-08-31",
                        "--token", "argv-secret",
                    ])
        self.assertEqual(rc, 2)
        self.assertNotIn("argv-secret", stderr.getvalue())

    def test_missing_env_token_does_not_advertise_argv_secret_input(self):
        env = {key: value for key, value in os.environ.items() if key != "YANDEX_DIRECT_TOKEN"}
        stderr = io.StringIO()
        with patch.dict(os.environ, env, clear=True):
            with patch("sys.stderr", stderr):
                with self.assertRaises(SystemExit):
                    yd_report.main(["campaign", "2026-08-01", "2026-08-31"])
        self.assertIn("YANDEX_DIRECT_TOKEN", stderr.getvalue())
        self.assertNotIn("--token", stderr.getvalue())

    def test_obsolete_include_discount_is_not_sent(self):
        body = build_report_body("campaign", "2026-08-01", "2026-08-31", report_name="campaign")
        self.assertNotIn("IncludeDiscount", body["params"])

    def test_http_error_body_is_bounded_and_replacement_decoded(self):
        tracking = _TrackingBody(b"bad:\xff" + (b"x" * 5000) + b"TAIL-SENTINEL")
        error = urllib.error.HTTPError(
            yd_report.REPORTS_URL,
            400,
            "bad request",
            {},
            tracking,
        )
        body = build_report_body("campaign", "2026-08-01", "2026-08-31", report_name="bounded-error")

        def opener(request, timeout=0):
            raise error

        with self.assertRaises(RuntimeError) as ctx:
            fetch_report("token", body, opener=opener)
        self.assertEqual(tracking.read_sizes, [4096])
        self.assertTrue(tracking.closed)
        self.assertIn("bad:�", str(ctx.exception))
        self.assertNotIn("TAIL-SENTINEL", str(ctx.exception))

    def test_url_error_is_converted_to_secret_free_operational_failure(self):
        body = build_report_body("campaign", "2026-08-01", "2026-08-31", report_name="network-error")

        def opener(request, timeout=0):
            raise urllib.error.URLError("temporary DNS failure")

        with self.assertRaisesRegex(RuntimeError, "Direct Reports network error") as ctx:
            fetch_report("secret-token-value", body, opener=opener)
        self.assertNotIn("secret-token-value", str(ctx.exception))

    def test_first_http_500_is_retried_once_with_injected_transport(self):
        first = urllib.error.HTTPError(
            yd_report.REPORTS_URL,
            500,
            "server error",
            {"retryIn": "1"},
            io.BytesIO(b"temporary"),
        )
        second = _Response(200, b"Date\tClicks\n2026-08-01\t1\n")
        responses = [first, second]
        sleeps = []

        def opener(request, timeout=0):
            current = responses.pop(0)
            if isinstance(current, Exception):
                raise current
            return current

        body = build_report_body("campaign", "2026-08-01", "2026-08-31", report_name="retry-500")
        text = fetch_report("token", body, max_attempts=3, opener=opener, sleep=sleeps.append)
        self.assertIn("2026-08-01", text)
        self.assertEqual(len(responses), 0)
        self.assertEqual(sleeps, [1])


if __name__ == "__main__":
    unittest.main()
