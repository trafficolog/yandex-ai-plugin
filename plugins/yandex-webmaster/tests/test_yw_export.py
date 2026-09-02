from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from scripts import yw_export


class TestExport(unittest.TestCase):
    def test_pro_export_paths(self):
        start = yw_export.start_request(1, "h", dates=["2026-08-20"], paths=["/catalog"], region_ids=[213], use_pro_tariff=False)
        status = yw_export.status_request(1, "h", "task-1")
        limits = yw_export.limits_request(1, "h")
        dates = yw_export.available_dates_request(1, "h")
        self.assertEqual(start["method"], "POST")
        self.assertTrue(start["path"].endswith("/pro/serp/queries/download"))
        self.assertTrue(status["path"].endswith("/pro/serp/queries/download/task-1"))
        self.assertTrue(limits["path"].endswith("/pro/limits"))
        self.assertTrue(dates["path"].endswith("/pro/serp/dates"))

    def test_pro_tariff_serializes_as_documented_string(self):
        disabled = yw_export.start_request(1, "h", dates=["2026-08-20"], paths=["/catalog"], use_pro_tariff=False)
        enabled = yw_export.start_request(1, "h", dates=["2026-08-20"], paths=["/catalog"], use_pro_tariff=True)
        self.assertEqual(disabled["body"]["use_pro_tariff"], "false")
        self.assertEqual(enabled["body"]["use_pro_tariff"], "true")

    def test_pro_paths_require_relative_leading_slash(self):
        accepted = yw_export.start_request(1, "h", dates=["2026-08-20"], paths=["/catalog?q=1"])
        self.assertEqual(accepted["body"]["paths"], ["/catalog?q=1"])
        for path in ["catalog", "https://example.com/catalog", "", "   "]:
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    yw_export.start_request(1, "h", dates=["2026-08-20"], paths=[path])

    def test_download_url_for_success(self):
        self.assertEqual(yw_export.download_url({"download_status": "SUCCESS", "url": "https://storage/x"}), "https://storage/x")
        self.assertIsNone(yw_export.download_url({"download_status": "IN_PROGRESS"}))
        with self.assertRaises(ValueError):
            yw_export.download_url({"download_status": "SUCCESS", "url": "http://storage/x"})

    def test_export_state_maps_documented_lifecycle(self):
        self.assertEqual(yw_export.export_state({"download_status": "IN_PROGRESS"})["state"], "PENDING")
        failed = yw_export.export_state({"download_status": "FAILED", "error_code": "LIMIT", "error_message": "quota"})
        self.assertEqual(failed["state"], "FAILED")
        self.assertEqual(failed["error_code"], "LIMIT")
        self.assertEqual(failed["error_message"], "quota")
        ready = yw_export.export_state({"download_status": "SUCCESS", "url": "https://storage/x"})
        self.assertEqual(ready["state"], "READY")
        self.assertEqual(ready["url"], "https://storage/x")
        self.assertEqual(ready["download_age"], "UNKNOWN")
        missing = yw_export.export_state({"download_status": "SUCCESS"})
        self.assertEqual(missing["state"], "DOWNLOAD_URL_MISSING")

    def test_export_state_expires_only_when_age_is_proven_over_24_hours(self):
        completed = datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc)
        at_boundary = yw_export.export_state(
            {"download_status": "SUCCESS", "url": "https://storage/x"},
            completed_at=completed,
            now=completed + timedelta(hours=24),
        )
        self.assertEqual(at_boundary["state"], "READY")
        expired = yw_export.export_state(
            {"download_status": "SUCCESS", "url": "https://storage/x"},
            completed_at=completed,
            now=completed + timedelta(hours=24, seconds=1),
        )
        self.assertEqual(expired["state"], "DOWNLOAD_EXPIRED")
        self.assertGreater(expired["download_age_hours"], 24)

    def test_quota_plan_does_not_assume_missing_usage_is_available(self):
        unknown = yw_export.plan_quota(25)
        self.assertEqual(unknown["status"], "QUOTA_USAGE_UNKNOWN")
        self.assertIsNone(unknown["known_remaining"])

    def test_quota_plan_uses_known_remaining_without_executing(self):
        within = yw_export.plan_quota(25, known_remaining=30)
        risk = yw_export.plan_quota(25, known_remaining=20)
        self.assertEqual(within["status"], "WITHIN_KNOWN_QUOTA")
        self.assertEqual(risk["status"], "QUOTA_LIMIT_RISK")
        self.assertEqual(within["requested_units"], 25)

    def test_quota_plan_prefers_initialization_response_remaining(self):
        plan = yw_export.plan_quota(
            25,
            known_remaining=10,
            initialization_response={"quota_remaining": 40, "quota_used": 60},
        )
        self.assertEqual(plan["status"], "WITHIN_KNOWN_QUOTA")
        self.assertEqual(plan["known_remaining"], 40)
        self.assertEqual(plan["quota_used"], 60)
        self.assertEqual(plan["quota_source"], "initialization_response")

    def test_download_to_file(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / "nested" / "report.tsv"
            result = yw_export.download_to_file("https://storage/x", output, transport=lambda url: b"a\tb\n1\t2\n")
            self.assertEqual(result, output)
            self.assertEqual(output.read_bytes(), b"a\tb\n1\t2\n")

    def test_download_rejects_non_https_schemes_before_transport(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.tsv"
            for url in ["file:///etc/passwd", "http://127.0.0.1/report"]:
                with self.subTest(url=url):
                    with self.assertRaises(ValueError):
                        yw_export.download_to_file(url, output, transport=lambda value: b"unsafe")


if __name__ == "__main__":
    unittest.main()
