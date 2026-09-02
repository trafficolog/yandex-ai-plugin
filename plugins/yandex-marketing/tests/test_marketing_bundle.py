import unittest
from scripts.marketing_bundle import new_bundle, add_evidence

class MarketingBundleTests(unittest.TestCase):
    def test_bundle_requires_explicit_direct_coverage_key(self):
        with self.assertRaises(ValueError):
            new_bundle({}, {'metrika':True})
        bundle = new_bundle({'period':{'from':'2026-08-01','to':'2026-08-31'}}, {'direct':False,'metrika':True})
        self.assertTrue(bundle['routing_required'])

    def test_evidence_kinds_and_overlapping_metrics_stay_separate(self):
        bundle = new_bundle({}, {'direct':True,'metrika':True,'wordstat':False,'search':False})
        add_evidence(bundle, {'kind':'OBSERVED','metric':'cost','value':100,'source':'yandex-direct','role':'canonical_paid_cost'})
        add_evidence(bundle, {'kind':'OBSERVED','metric':'cost','value':98,'source':'yandex-metrika','role':'reconciliation_only'})
        self.assertEqual(len(bundle['evidence']), 2)
        self.assertEqual({x['source'] for x in bundle['evidence']}, {'yandex-direct','yandex-metrika'})
        with self.assertRaises(ValueError):
            add_evidence(bundle, {'kind':'GUESS','metric':'cost','value':1,'source':'x'})

if __name__ == '__main__': unittest.main()
