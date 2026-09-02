import unittest
from scripts.seo_opportunities import find_content_gaps, find_ctr_opportunities, find_conversion_opportunities, find_technical_blockers

class OpportunityTests(unittest.TestCase):
    def test_discovery_candidate_vs_validated_gap(self):
        partial={'coverage':{'wordstat':True},'queries':[{'query_key':'a','wordstat_count':1000}]}
        self.assertEqual(find_content_gaps(partial)[0]['type'],'DISCOVERY_CANDIDATE')
        full={'coverage':{'wordstat':True,'search':True,'webmaster':True},'queries':[{'query_key':'a','wordstat_count':1000,'search_site_present':False,'webmaster_impressions':0}]}
        finding=find_content_gaps(full)[0]
        self.assertEqual(finding['type'],'CONTENT_GAP')
        self.assertEqual(finding['kind'],'DERIVED')

    def test_ctr_uses_own_baseline_only(self):
        b={'queries':[{'query_key':'a','webmaster_ctr':0.04,'own_baseline_ctr':0.07},{'query_key':'b','webmaster_ctr':0.04}]}
        out=find_ctr_opportunities(b)
        self.assertEqual([x['query_key'] for x in out],['a'])
        self.assertNotIn('benchmark',out[0])

    def test_conversion_mismatch_is_hypothesis(self):
        b={'pages':[{'url_key':'https://x/p','organic_conversion_rate':0.01,'own_comparable_conversion_rate':0.04,'intent_evidence':True}]}
        out=find_conversion_opportunities(b)
        self.assertEqual(out[0]['kind'],'HYPOTHESIS')
        self.assertEqual(out[0]['type'],'LANDING_OR_INTENT_MISMATCH')

    def test_technical_blocker_is_correlation_not_cause(self):
        b={'pages':[{'url_key':'https://x/p','technical_issue':'NOT_INDEXED','opportunity_evidence':True}]}
        out=find_technical_blockers(b)
        self.assertEqual(out[0]['kind'],'DERIVED')
        self.assertFalse(out[0]['causal_claim'])
