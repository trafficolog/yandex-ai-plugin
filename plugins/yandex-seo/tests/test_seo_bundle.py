import unittest
from scripts.seo_bundle import new_bundle, add_evidence

class BundleTests(unittest.TestCase):
    def test_bundle_contract(self):
        b=new_bundle({'site':'example.com'},{'wordstat':True,'search':False,'webmaster':True,'metrika':False})
        self.assertEqual(b['version'],1)
        self.assertEqual(b['coverage']['wordstat'],True)
        self.assertEqual(b['evidence'],[])

    def test_evidence_keeps_provenance_and_kinds(self):
        b=new_bundle({}, {})
        add_evidence(b, {'kind':'OBSERVED','metric':'wordstat_count','value':100,'source':'yandex-wordstat'})
        add_evidence(b, {'kind':'OBSERVED','metric':'webmaster_demand','value':80,'source':'yandex-webmaster'})
        self.assertEqual([x['metric'] for x in b['evidence']], ['wordstat_count','webmaster_demand'])

    def test_ambiguous_demand_is_rejected(self):
        b=new_bundle({}, {})
        with self.assertRaises(ValueError):
            add_evidence(b, {'kind':'OBSERVED','metric':'demand','value':100,'source':'x'})

    def test_unknown_kind_is_rejected(self):
        b=new_bundle({}, {})
        with self.assertRaises(ValueError):
            add_evidence(b, {'kind':'FACT','metric':'clicks','value':1,'source':'x'})
