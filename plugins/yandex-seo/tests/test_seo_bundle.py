import unittest

from scripts.seo_bundle import add_evidence, new_bundle

VALID_CONTEXT = {
    "site": "example.com",
    "analysis_period": {"from": "2026-08-01", "to": "2026-08-31"},
    "search_region_id": 213,
    "search_type": "SEARCH_TYPE_RU",
}


class BundleTests(unittest.TestCase):
    def test_bundle_contract(self):
        bundle = new_bundle(
            VALID_CONTEXT,
            {"wordstat": True, "search": False, "webmaster": True, "metrika": False},
        )
        self.assertEqual(bundle["version"], 1)
        self.assertTrue(bundle["coverage"]["wordstat"])
        self.assertEqual(bundle["evidence"], [])
        self.assertEqual(bundle["alignment"]["period"], "UNKNOWN")
        self.assertEqual(bundle["alignment"]["geo"], "UNKNOWN")
        self.assertEqual(bundle["alignment"]["search"], "UNKNOWN")
        self.assertEqual(bundle["alignment"]["device"], "UNKNOWN")

    def test_bundle_rejects_missing_required_context(self):
        for missing in ("site", "analysis_period", "search_region_id"):
            context = dict(VALID_CONTEXT)
            context.pop(missing)
            with self.assertRaises(ValueError, msg=missing):
                new_bundle(context, {})
        with self.assertRaises(ValueError):
            new_bundle({**VALID_CONTEXT, "analysis_period": {"from": "2026-08-01"}}, {})

    def test_bundle_materializes_all_alignment_dimensions(self):
        context = {
            **VALID_CONTEXT,
            "period_evidence": [
                {"period": {"from": "2026-08-01", "to": "2026-08-31"}},
                {"period": {"from": "2026-08-01", "to": "2026-08-31"}},
            ],
            "geo_evidence": [
                {"search_region_id": 213},
                {"metrika_visitor_region": 213},
            ],
            "search_evidence": [
                {"search_type": "SEARCH_TYPE_RU"},
                {"search_type": "SEARCH_TYPE_RU"},
            ],
            "device_evidence": [
                {"device": "desktop"},
                {"device": "desktop"},
            ],
        }
        bundle = new_bundle(context, {})
        self.assertEqual(bundle["alignment"]["period"], "EXACT")
        self.assertEqual(bundle["alignment"]["geo"], "MISMATCHED")
        self.assertEqual(bundle["alignment"]["search"], "EXACT")
        self.assertEqual(bundle["alignment"]["device"], "EXACT")

    def test_evidence_keeps_provenance_and_kinds(self):
        bundle = new_bundle(VALID_CONTEXT, {})
        add_evidence(bundle, {"kind": "OBSERVED", "metric": "wordstat_count", "value": 100, "source": "yandex-wordstat"})
        add_evidence(bundle, {"kind": "OBSERVED", "metric": "webmaster_demand", "value": 80, "source": "yandex-webmaster"})
        self.assertEqual([item["metric"] for item in bundle["evidence"]], ["wordstat_count", "webmaster_demand"])

    def test_ambiguous_demand_is_rejected(self):
        bundle = new_bundle(VALID_CONTEXT, {})
        with self.assertRaises(ValueError):
            add_evidence(bundle, {"kind": "OBSERVED", "metric": "demand", "value": 100, "source": "x"})

    def test_unknown_kind_is_rejected(self):
        bundle = new_bundle(VALID_CONTEXT, {})
        with self.assertRaises(ValueError):
            add_evidence(bundle, {"kind": "FACT", "metric": "clicks", "value": 1, "source": "x"})


if __name__ == "__main__":
    unittest.main()
