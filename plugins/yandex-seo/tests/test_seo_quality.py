import unittest
from scripts.seo_quality import propagate_limitations, capability_mode

class QualityTests(unittest.TestCase):
    def test_capability_modes(self):
        self.assertEqual(capability_mode({'wordstat':1,'search':1,'webmaster':1,'metrika':1}),'FULL')
        self.assertEqual(capability_mode({'wordstat':1,'search':1}),'DISCOVERY')
        self.assertEqual(capability_mode({'search':1,'webmaster':1}),'VISIBILITY')
        self.assertEqual(capability_mode({'webmaster':1,'metrika':1}),'PERFORMANCE')
        self.assertEqual(capability_mode({'wordstat':1}),'PARTIAL')

    def test_limitations_are_propagated(self):
        records=[
          {'source':'yandex-metrika','quality':{'sampled':True,'sample_share':0.1}},
          {'source':'yandex-webmaster','coverage':{'top_n':500}},
          {'source':'yandex-search','cluster':{'bridge_risk':True,'cluster_id':'C1'}},
        ]
        out=propagate_limitations(records)
        kinds={x['kind'] for x in out}
        self.assertEqual(kinds, {'METRIKA_SAMPLING','WEBMASTER_TOP_N','SEARCH_BRIDGE_RISK'})
        self.assertTrue(any(x.get('sample_share')==0.1 for x in out))
