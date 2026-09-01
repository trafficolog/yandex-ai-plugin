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

    def test_download_url_for_success(self):
        self.assertEqual(yw_export.download_url({"download_status": "SUCCESS", "url": "https://storage/x"}), "https://storage/x")
        self.assertIsNone(yw_export.download_url({"download_status": "IN_PROGRESS"}))

    def test_download_to_file(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / "nested" / "report.tsv"
            result = yw_export.download_to_file("https://storage/x", output, transport=lambda url: b"a\tb\n1\t2\n")
            self.assertEqual(result, output)
            self.assertEqual(output.read_bytes(), b"a\tb\n1\t2\n")


if __name__ == "__main__":
    unittest.main()
