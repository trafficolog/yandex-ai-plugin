import unittest

from scripts import ywstat_trends


def points(values, start_year=2026, start_month=1):
    out = []
    year, month = start_year, start_month
    for value in values:
        out.append({"date": f"{year:04d}-{month:02d}-01T00:00:00Z", "count": value, "share": 0.0})
        month += 1
        if month == 13:
            month = 1
            year += 1
    return out


class TestWordstatTrends(unittest.TestCase):
    def test_low_volume_noise(self):
        result = ywstat_trends.classify_trend(points([2, 3, 2, 20]), absolute_floor=100)
        self.assertEqual(result["classification"], "LOW_VOLUME_NOISE")
        self.assertGreater(result["growth_pct"], 500)

    def test_stable(self):
        result = ywstat_trends.classify_trend(points([1000, 1050, 950, 1020]))
        self.assertEqual(result["classification"], "STABLE")

    def test_growing(self):
        result = ywstat_trends.classify_trend(points([950, 1000, 1050, 1700]))
        self.assertEqual(result["classification"], "GROWING")
        self.assertGreaterEqual(result["growth_pct"], 50)

    def test_explosive(self):
        result = ywstat_trends.classify_trend(points([950, 1000, 1050, 3500]))
        self.assertEqual(result["classification"], "EXPLOSIVE")
        self.assertGreaterEqual(result["growth_pct"], 200)

    def test_seasonal_spike_takes_precedence(self):
        data = [
            {"date":"2025-05-01T00:00:00Z","count":900},
            {"date":"2025-06-01T00:00:00Z","count":1000},
            {"date":"2025-07-01T00:00:00Z","count":1100},
            {"date":"2025-08-01T00:00:00Z","count":2900},
            {"date":"2026-05-01T00:00:00Z","count":950},
            {"date":"2026-06-01T00:00:00Z","count":1000},
            {"date":"2026-07-01T00:00:00Z","count":1050},
            {"date":"2026-08-01T00:00:00Z","count":3000},
        ]
        result = ywstat_trends.classify_trend(data, seasonal_tolerance_pct=10)
        self.assertEqual(result["classification"], "SEASONAL")
        self.assertEqual(result["seasonal_reference"]["date"], "2025-08-01T00:00:00Z")

    def test_thresholds_are_reported(self):
        result = ywstat_trends.classify_trend(points([100, 100, 100, 151]), growing_pct=50, explosive_pct=200)
        self.assertEqual(result["thresholds"]["growing_pct"], 50)
        self.assertEqual(result["thresholds"]["explosive_pct"], 200)


if __name__ == "__main__":
    unittest.main()
