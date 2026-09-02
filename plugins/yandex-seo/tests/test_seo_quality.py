import unittest

from scripts.seo_quality import capability_mode, propagate_limitations


class QualityTests(unittest.TestCase):
    def test_capability_modes(self):
        self.assertEqual(capability_mode({"wordstat": 1, "search": 1, "webmaster": 1, "metrika": 1}), "FULL")
        self.assertEqual(capability_mode({"wordstat": 1, "search": 1}), "DISCOVERY")
        self.assertEqual(capability_mode({"search": 1, "webmaster": 1}), "VISIBILITY")
        self.assertEqual(capability_mode({"webmaster": 1, "metrika": 1}), "PERFORMANCE")
        self.assertEqual(capability_mode({"wordstat": 1}), "PARTIAL")

    def test_limitations_are_propagated(self):
        records = [
            {"source": "yandex-metrika", "quality": {"sampled": True, "sample_share": 0.1}},
            {"source": "yandex-webmaster", "coverage": {"top_n": 500}},
            {"source": "yandex-search", "cluster": {"bridge_risk": True, "cluster_id": "C1"}},
        ]
        out = propagate_limitations(records)
        kinds = {item["kind"] for item in out}
        self.assertEqual(kinds, {"METRIKA_SAMPLING", "WEBMASTER_TOP_N", "SEARCH_BRIDGE_RISK"})
        self.assertTrue(any(item.get("sample_share") == 0.1 for item in out))

    def test_data_lag_propagates_without_sampling(self):
        out = propagate_limitations([
            {"source": "yandex-metrika", "quality": {"sampled": False, "data_lag": 3}},
        ])
        self.assertIn("METRIKA_DATA_LAG", {item["kind"] for item in out})
        lag = next(item for item in out if item["kind"] == "METRIKA_DATA_LAG")
        self.assertEqual(lag["data_lag"], 3)

    def test_missing_metrika_quality_uses_cross_service_marker(self):
        out = propagate_limitations([{"source": "yandex-metrika"}])
        self.assertIn("QUALITY_METADATA_MISSING", {item["kind"] for item in out})
        self.assertNotIn("METRIKA_QUALITY_UNKNOWN", {item["kind"] for item in out})


if __name__ == "__main__":
    unittest.main()
