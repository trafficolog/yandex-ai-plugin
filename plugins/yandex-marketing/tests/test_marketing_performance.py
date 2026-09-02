import unittest

from scripts.marketing_performance import compare_performance, derive_performance, reconcile_conversions

KPI = {
    "business_objective": "purchase",
    "goal_ids": ["1"],
    "attribution_model": "automatic",
    "metric_basis": "converted_sessions",
    "currency": "RUB",
    "vat_basis": "excluded",
    "period": {"from": "2026-08-01", "to": "2026-08-31"},
}


class MarketingPerformanceTests(unittest.TestCase):
    def test_derives_only_supported_metrics(self):
        result = derive_performance(
            {"impressions": 1000, "clicks": 100, "cost": 5000, "conversions": 10, "revenue": 15000, "maturity": "MATURE"},
            KPI,
        )
        self.assertEqual(result["cpc"], 50)
        self.assertEqual(result["ctr"], 0.1)
        self.assertEqual(result["cr"], 0.1)
        self.assertEqual(result["cpa"], 500)
        self.assertEqual(result["roas"], 3)
        no_revenue = derive_performance({"clicks": 10, "cost": 100, "conversions": 1}, KPI)
        self.assertNotIn("roas", no_revenue)
        self.assertNotIn("drr", no_revenue)

    def test_money_metrics_require_explicit_currency_and_vat(self):
        unknown_money = {**KPI, "currency": None, "vat_basis": None}
        result = derive_performance(
            {"impressions": 1000, "clicks": 100, "cost": 5000, "conversions": 10, "revenue": 15000},
            unknown_money,
        )
        self.assertEqual(result["ctr"], 0.1)
        self.assertEqual(result["cr"], 0.1)
        for metric in ("cpc", "cpa", "roas", "drr"):
            self.assertNotIn(metric, result)
        self.assertIn("MONEY_CONTEXT_UNKNOWN", result["limitations"])

    def test_compare_blocks_different_goals_and_currency(self):
        left = derive_performance({"cost": 100, "conversions": 2}, KPI)
        different_goal = derive_performance({"cost": 100, "conversions": 5}, {**KPI, "goal_ids": ["micro"]})
        self.assertEqual(compare_performance(left, different_goal)["status"], "INCOMPARABLE")
        different_currency = derive_performance({"cost": 100, "conversions": 5}, {**KPI, "currency": "EUR"})
        self.assertEqual(compare_performance(left, different_currency)["status"], "INCOMPARABLE")

    def test_immature_data_is_disclosed(self):
        result = derive_performance({"cost": 100, "conversions": 1, "maturity": "IMMATURE"}, KPI)
        self.assertIn("IMMATURE", result["limitations"])

    def test_conversion_reconciliation_can_be_explainable(self):
        direct = {"metric": "conversions", "value": 10, "source": "yandex-direct", "kpi": KPI}
        metrika = {"metric": "conversions", "value": 12, "source": "yandex-metrika", "kpi": KPI}
        self.assertEqual(
            reconcile_conversions(direct, metrika, {"known_difference_reason": "different date basis"})["status"],
            "EXPLAINABLE_DIFFERENCE",
        )
        bad = {**metrika, "kpi": {**KPI, "attribution_model": "other"}}
        self.assertEqual(reconcile_conversions(direct, bad, {})["status"], "INCOMPARABLE")


if __name__ == "__main__":
    unittest.main()
