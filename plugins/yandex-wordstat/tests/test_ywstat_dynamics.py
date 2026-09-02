import unittest

from scripts import ywstat_dynamics


class TestWordstatDynamics(unittest.TestCase):
    def test_payload_uses_rest_camel_case(self):
        payload = ywstat_dynamics.build_dynamics_payload(
            "зубная паста",
            period="PERIOD_MONTHLY",
            from_date="2025-01-01T00:00:00Z",
            to_date="2026-01-31T23:59:59Z",
            regions=["225"],
            devices=["DEVICE_ALL"],
            folder_id="folder",
        )
        self.assertEqual(payload["period"], "PERIOD_MONTHLY")
        self.assertIn("fromDate", payload)
        self.assertIn("toDate", payload)
        self.assertNotIn("from_date", payload)
        self.assertEqual(payload["folderId"], "folder")

    def test_daily_period_is_supported(self):
        payload = ywstat_dynamics.build_dynamics_payload(
            '"зубная паста" -оптом',
            period="PERIOD_DAILY",
            from_date="2026-01-01T00:00:00Z",
            to_date="2026-01-02T00:00:00Z",
        )
        self.assertEqual(payload["period"], "PERIOD_DAILY")

    def test_monthly_weekly_operator_compatibility(self):
        for period in ["PERIOD_MONTHLY", "PERIOD_WEEKLY"]:
            ywstat_dynamics.validate_expression_for_period("работа +на дому", period)
            ywstat_dynamics.validate_expression_for_period("интернет-магазин", period)
            for expression in [
                "купить !собаку", '"зубная паста"', "билеты [из москвы]",
                "заказать (роллы|пицца)", "доставка -цветы",
            ]:
                with self.assertRaises(ValueError, msg=(period, expression)):
                    ywstat_dynamics.validate_expression_for_period(expression, period)

    def test_monthly_weekly_rejection_is_described_as_plugin_compatibility_guard(self):
        with self.assertRaises(ValueError) as caught:
            ywstat_dynamics.validate_expression_for_period("купить !собаку", "PERIOD_MONTHLY")
        message = str(caught.exception).lower()
        self.assertIn("plugin compatibility", message)
        self.assertIn("period_daily", message)
        self.assertNotIn("yandex forbids", message)
        self.assertNotIn("documented yandex restriction", message)
        self.assertNotIn("only guarantees", message)

    def test_daily_allows_documented_operators(self):
        for expression in [
            "купить !собаку", '"зубная паста"', "билеты [из москвы]",
            "заказать (роллы|пицца)", "доставка -цветы", "работа +на дому",
        ]:
            ywstat_dynamics.validate_expression_for_period(expression, "PERIOD_DAILY")

    def test_unknown_period_is_rejected(self):
        with self.assertRaises(ValueError):
            ywstat_dynamics.validate_expression_for_period("x", "PERIOD_HOURLY")

    def test_date_order_is_validated(self):
        with self.assertRaises(ValueError):
            ywstat_dynamics.build_dynamics_payload(
                "x", period="PERIOD_MONTHLY",
                from_date="2026-03-01T00:00:00Z", to_date="2026-02-01T00:00:00Z"
            )

    def test_normalize_series_converts_numbers(self):
        rows = ywstat_dynamics.normalize_series({
            "results": [
                {"date":"2026-01-01T00:00:00Z", "count":"1200", "share":"0.12"},
                {"date":"2026-02-01T00:00:00Z", "count":"1500", "share":"0.14"},
            ]
        })
        self.assertEqual(rows[0]["count"], 1200)
        self.assertAlmostEqual(rows[0]["share"], 0.12)
        self.assertEqual(rows[1]["date"], "2026-02-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
