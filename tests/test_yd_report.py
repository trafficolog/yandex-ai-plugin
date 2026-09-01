import unittest
from scripts.yd_report import build_report_body, parse_retry_in


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


if __name__ == "__main__":
    unittest.main()
