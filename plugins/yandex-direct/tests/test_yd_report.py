import io
import unittest
import urllib.error
from unittest.mock import patch

from scripts import yd_report
from scripts.yd_report import build_report_body, fetch_report, parse_retry_in


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

    def test_obsolete_include_discount_is_not_sent(self):
        body = build_report_body("campaign", "2026-08-01", "2026-08-31", report_name="campaign")
        self.assertNotIn("IncludeDiscount", body["params"])

    def test_first_http_500_is_retried_once(self):
        first = urllib.error.HTTPError(
            yd_report.REPORTS_URL,
            500,
            "server error",
            {"retryIn": "1"},
            io.BytesIO(b"temporary"),
        )
        second = _Response(200, b"Date\tClicks\n2026-08-01\t1\n")
        body = build_report_body("campaign", "2026-08-01", "2026-08-31", report_name="retry-500")
        with patch.object(yd_report.urllib.request, "urlopen", side_effect=[first, second]) as opener:
            with patch.object(yd_report.time, "sleep"):
                text = fetch_report("token", body, max_attempts=3)
        self.assertIn("2026-08-01", text)
        self.assertEqual(opener.call_count, 2)


if __name__ == "__main__":
    unittest.main()
