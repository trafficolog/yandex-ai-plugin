import unittest

from scripts.seo_context import (
    classify_device_alignment,
    classify_geo_alignment,
    classify_period_alignment,
    classify_search_alignment,
    normalize_query,
    normalize_url,
)


class ContextTests(unittest.TestCase):
    def test_query_normalization_is_conservative(self):
        self.assertEqual(normalize_query("  КУПИТЬ\u00a0  Пасту  "), "купить пасту")
        self.assertNotEqual(normalize_query("купить пасту"), normalize_query("купить зубную пасту"))

    def test_url_keeps_query_parameters(self):
        self.assertEqual(
            normalize_url("HTTPS://Example.COM:443/path?b=2&a=1#x"),
            "https://example.com/path?a=1&b=2",
        )
        self.assertNotEqual(
            normalize_url("https://x.test/p?id=1"),
            normalize_url("https://x.test/p?id=2"),
        )

    def test_period_alignment(self):
        exact = [
            {"period": {"from": "2026-08-01", "to": "2026-08-31"}},
            {"period": {"from": "2026-08-01", "to": "2026-08-31"}},
        ]
        self.assertEqual(classify_period_alignment(exact), "EXACT")
        approx = [
            {"period": {"from": "2026-08-01", "to": "2026-08-31"}},
            {"window": "rolling_30_days"},
        ]
        self.assertEqual(classify_period_alignment(approx), "APPROXIMATE")
        mismatch = [
            {"period": {"from": "2026-07-01", "to": "2026-07-31"}},
            {"period": {"from": "2026-08-01", "to": "2026-08-31"}},
        ]
        self.assertEqual(classify_period_alignment(mismatch), "MISMATCHED")

    def test_missing_period_context_is_unknown(self):
        self.assertEqual(classify_period_alignment([]), "UNKNOWN")
        self.assertEqual(classify_period_alignment([{}, {}]), "UNKNOWN")
        self.assertEqual(
            classify_period_alignment([
                {"period": {"from": "2026-08-01", "to": "2026-08-31"}},
                {},
            ]),
            "UNKNOWN",
        )

    def test_geo_alignment_requires_same_semantic_context(self):
        exact = [
            {"geo_type": "serp_region", "region_ids": [213]},
            {"geo_type": "serp_region", "region_ids": [213]},
        ]
        self.assertEqual(classify_geo_alignment(exact), "EXACT")
        self.assertEqual(
            classify_geo_alignment([
                {"geo_type": "serp_region", "region_ids": [213]},
                {"geo_type": "visitor_region", "region_ids": [213]},
            ]),
            "MISMATCHED",
        )
        self.assertEqual(classify_geo_alignment([{}]), "UNKNOWN")

    def test_geo_alignment_understands_source_specific_fields(self):
        self.assertEqual(
            classify_geo_alignment([
                {"search_region_id": 213},
                {"search_region_id": 213},
            ]),
            "EXACT",
        )
        self.assertEqual(
            classify_geo_alignment([
                {"search_region_id": 213},
                {"metrika_visitor_region": 213},
            ]),
            "MISMATCHED",
        )
        self.assertNotEqual(
            classify_geo_alignment([
                {"metrika_visitor_region": 213},
                {"search_region_id": None},
            ]),
            "EXACT",
        )

    def test_search_context_alignment(self):
        self.assertEqual(
            classify_search_alignment([
                {"search_type": "SEARCH_TYPE_RU"},
                {"search_type": "SEARCH_TYPE_RU"},
            ]),
            "EXACT",
        )
        self.assertEqual(
            classify_search_alignment([
                {"search_type": "SEARCH_TYPE_RU"},
                {"search_type": "SEARCH_TYPE_COM"},
            ]),
            "MISMATCHED",
        )
        self.assertEqual(classify_search_alignment([{}]), "UNKNOWN")

    def test_device_context_alignment(self):
        self.assertEqual(
            classify_device_alignment([
                {"device": "desktop"},
                {"device": "desktop"},
            ]),
            "EXACT",
        )
        self.assertEqual(
            classify_device_alignment([
                {"devices": ["desktop", "mobile"]},
                {"devices": ["mobile", "desktop"]},
            ]),
            "EXACT",
        )
        self.assertEqual(
            classify_device_alignment([
                {"device": "desktop"},
                {"device": "mobile"},
            ]),
            "MISMATCHED",
        )
        self.assertEqual(classify_device_alignment([{}]), "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
