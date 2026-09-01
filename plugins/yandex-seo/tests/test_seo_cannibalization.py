import unittest
from scripts.seo_cannibalization import find_cannibalization

class CannibalizationTests(unittest.TestCase):
    def test_requires_multi_source_evidence(self):
        one={'clusters':[{'cluster_id':'C1','own_urls':['/a','/b'],'search_evidence':True,'webmaster_evidence':False}]}
        self.assertEqual(find_cannibalization(one),[])
        two={'clusters':[{'cluster_id':'C1','own_urls':['/a','/b'],'search_evidence':True,'webmaster_evidence':True,'position_instability':True}]}
        out=find_cannibalization(two)
        self.assertEqual(out[0]['type'],'CANNIBALIZATION_CANDIDATE')
        self.assertEqual(out[0]['kind'],'HYPOTHESIS')
        self.assertEqual(out[0]['confidence'],'HIGH')
