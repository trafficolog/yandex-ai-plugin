import unittest

from scripts.seo_bundle import add_evidence, new_bundle


class BundleTests(unittest.TestCase):
    def test_bundle_contract(self):
        bundle = new_bundle(
            {"site": "example.com"},
            {"wordstat": True, "search": False, "webmaster": True, "metrika": False},
        )
        self.assertEqual(bundle["version"], 1)
        self.assertTrue(bundle["coverage"]["wordstat"])
        self.assertEqual(bundle["evidence"], [])
        self.assertEqual(bundle["alignment"]["period"], "UNKNOWN")
        self.assertEqual(bundle["alignment"]["geo"], "UNKNOWN")

    def test_bundle_materializes_period_and_geo_alignment(self):
        context = {
            "period_evidence": [
                {"period": {"from": "2026-08-01", "to": "2026-08-31"}},
                {"period": {"from": "2026-08-01", "to": "2026-08-31"}},
            ],
            "geo_evidence": [
                {"geo_type": "serp_region", "region_ids": [213]},
                {"geo_type": "visitor_region", "region_ids": [213]},
            ],
        }
        bundle = new_bundle(context, {})
        self.assertEqual(bundle["alignment"]["period"], "EXACT")
        self.assertEqual(bundle["alignment"]["geo"], "MISMATCHED")

    def test_evidence_keeps_provenance_and_kinds(self):
        bundle = new_bundle({}, {})
        add_evidence(bundle, {"kind": "OBSERVED", "metric": "wordstat_count", "value": 100, "source": "yandex-wordstat"})
        add_evidence(bundle, {"kind": "OBSERVED", "metric": "webmaster_demand", "value": 80, "source": "yandex-webmaster"})
        self.assertEqual([item["metric"] for item in bundle["evidence"]], ["wordstat_count", "webmaster_demand"])

    def test_ambiguous_demand_is_rejected(self):
        bundle = new_bundle({}, {})
        with self.assertRaises(ValueError):
            add_evidence(bundle, {"kind": "OBSERVED", "metric": "demand", "value": 100, "source": "x"})

    def test_unknown_kind_is_rejected(self):
        bundle = new_bundle({}, {})
        with self.assertRaises(ValueError):
            add_evidence(bundle, {"kind": "FACT", "metric": "clicks", "value": 1, "source": "x"})


if __name__ == "__main__":
    unittest.main()
