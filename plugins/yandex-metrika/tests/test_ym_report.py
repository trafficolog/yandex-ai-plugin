import unittest

from scripts.ym_report import (
    CURRENT_ATTRIBUTION_MODELS,
    REPORT_PATHS,
    build_report_url,
    extract_quality_metadata,
    validate_attribution_model,
)


class TestMetrikaReport(unittest.TestCase):
    def test_current_attribution_models(self):
        self.assertEqual(
            CURRENT_ATTRIBUTION_MODELS,
            {"cross_device_first", "last", "cross_device_last_significant", "automatic"},
        )

    def test_report_paths(self):
        self.assertEqual(REPORT_PATHS["table"], "/stat/v1/data")
        self.assertEqual(REPORT_PATHS["bytime"], "/stat/v1/data/bytime")
        self.assertEqual(REPORT_PATHS["comparison"], "/stat/v1/data/comparison")
        self.assertEqual(REPORT_PATHS["drilldown"], "/stat/v1/data/drilldown")
        self.assertEqual(REPORT_PATHS["comparison-drilldown"], "/stat/v1/data/comparison/drilldown")

    def test_build_report_url_serializes_lists(self):
        url = build_report_url(
            "table",
            {
                "ids": 123,
                "metrics": ["ym:s:visits", "ym:s:users"],
                "dimensions": ["ym:s:trafficSource"],
                "date1": "2026-08-01",
                "date2": "2026-08-31",
            },
        )
        self.assertIn("metrics=ym%3As%3Avisits%2Cym%3As%3Ausers", url)
        self.assertIn("dimensions=ym%3As%3AtrafficSource", url)

    def test_extract_quality_metadata(self):
        payload = {
            "sampled": True,
            "sample_share": 0.25,
            "sample_size": 250,
            "sample_space": 1000,
            "data_lag": 90,
            "contains_sensitive_data": True,
            "total_rows_rounded": True,
            "data": [],
        }
        self.assertEqual(
            extract_quality_metadata(payload),
            {
                "sampled": True,
                "sample_share": 0.25,
                "sample_size": 250,
                "sample_space": 1000,
                "data_lag": 90,
                "contains_sensitive_data": True,
                "total_rows_rounded": True,
            },
        )

    def test_invalid_attribution_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_attribution_model("lastsign")


if __name__ == "__main__":
    unittest.main()
