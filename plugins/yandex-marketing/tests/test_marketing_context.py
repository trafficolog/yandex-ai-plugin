import unittest

from scripts.marketing_context import (
    classify_maturity,
    classify_period_alignment,
    compare_kpi_fingerprints,
    kpi_fingerprint,
    normalize_query,
    normalize_url,
)


class MarketingContextTests(unittest.TestCase):
    def test_query_normalization_is_conservative(self):
        self.assertEqual(normalize_query("  Купить   ЗУБНУЮ\u00a0пасту "), "купить зубную пасту")
        self.assertNotEqual(normalize_query("купить пасту"), normalize_query("купить зубную пасту"))

    def test_url_normalization_preserves_query_parameters(self):
        self.assertEqual(normalize_url("HTTPS://Example.COM:443?a=2&b=1#x"), "https://example.com/?a=2&b=1")
        self.assertNotEqual(normalize_url("https://example.com/?id=1"), normalize_url("https://example.com/?id=2"))

    def test_kpi_fingerprint_comparison_reports_material_mismatch(self):
        base = kpi_fingerprint({
            "business_objective": "purchase",
            "goal_ids": ["2", "1"],
            "attribution_model": "automatic",
            "metric_basis": "converted_sessions",
            "currency": "RUB",
            "vat_basis": "excluded",
            "period": {"from": "2026-08-01", "to": "2026-08-31"},
        })
        same = kpi_fingerprint({**base, "goal_ids": ["1", "2"]})
        self.assertTrue(compare_kpi_fingerprints(base, same)["compatible"])
        for key, value in [
            ("goal_ids", ["9"]),
            ("attribution_model", "last"),
            ("metric_basis", "users"),
            ("currency", "EUR"),
            ("vat_basis", "included"),
            ("period", {"from": "2026-07-01", "to": "2026-07-31"}),
        ]:
            other = dict(base)
            other[key] = value
            result = compare_kpi_fingerprints(base, other)
            self.assertFalse(result["compatible"], key)
            self.assertIn(key, result["mismatches"])

    def test_missing_material_kpi_fields_are_incompatible(self):
        result = compare_kpi_fingerprints({}, {})
        self.assertFalse(result["compatible"])
        self.assertIn("goal_ids", result["missing"])
        self.assertIn("attribution_model", result["missing"])
        self.assertIn("currency", result["missing"])
        self.assertIn("vat_basis", result["missing"])
        self.assertIn("period", result["missing"])

    def test_period_alignment_states(self):
        first = {"period": {"from": "2026-08-01", "to": "2026-08-31"}}
        same = {"period": {"from": "2026-08-01", "to": "2026-08-31"}}
        self.assertEqual(classify_period_alignment([first, same]), "EXACT")
        approximate = {"period": {"from": "2026-08-02", "to": "2026-09-01"}, "approximate_period": True}
        self.assertEqual(classify_period_alignment([first, approximate]), "APPROXIMATE")
        different = {"period": {"from": "2026-06-01", "to": "2026-06-30"}}
        self.assertEqual(classify_period_alignment([first, different]), "MISMATCHED")

    def test_maturity_states(self):
        self.assertEqual(classify_maturity({"conversion_delay_days": 7, "days_since_period_end": 10}), "MATURE")
        self.assertEqual(classify_maturity({"conversion_delay_days": 7, "days_since_period_end": 3}), "IMMATURE")
        self.assertEqual(classify_maturity({}), "MATURITY_UNKNOWN")


if __name__ == "__main__":
    unittest.main()
