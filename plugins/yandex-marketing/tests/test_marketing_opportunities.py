import unittest
from scripts.marketing_opportunities import find_query_candidates, find_landing_hypotheses, find_budget_candidates, find_measurement_risks

class MarketingOpportunityTests(unittest.TestCase):
    def test_zero_conversions_alone_never_auto_excludes(self):
        self.assertEqual(find_query_candidates({'search_queries':[{'query':'x','clicks':100,'conversions':0}]}), [])
        mature={'search_queries':[{'query':'x','clicks':100,'conversions':0,'performance_sufficient':True,'maturity':'MATURE','business_goal_aligned':True,'exclusion_signal':True}]}
        result=find_query_candidates(mature); self.assertEqual(result[0]['type'],'SEARCH_TERM_EXCLUSION_REVIEW'); self.assertNotEqual(result[0]['type'],'AUTO_EXCLUDE')
    def test_expansion_and_search_context_are_evidence_only(self):
        result=find_query_candidates({'search_queries':[{'query':'купить пасту','expansion_signal':True,'wordstat_context':{'trend':'GROWING'},'search_context':{'intent':'ecommerce'}}]})[0]
        self.assertEqual(result['type'],'SEARCH_TERM_EXPANSION_CANDIDATE'); self.assertIn('search_context', result['evidence']); self.assertNotIn('cpa_adjustment', result)
    def test_landing_mismatch_remains_hypothesis(self):
        result=find_landing_hypotheses({'landings':[{'url':'https://example.com/a','intent_mismatch_signal':True,'evidence':['query','landing_behavior']} ]})[0]
        self.assertEqual(result['type'],'LANDING_MISMATCH_HYPOTHESIS'); self.assertEqual(result['kind'],'HYPOTHESIS')
    def test_budget_candidates_require_compatible_mature_sufficient_evidence(self):
        base={'campaign_id':1,'budget_constraint_signal':True,'kpi_compatible':True,'performance_sufficient':True,'maturity':'MATURE'}
        self.assertEqual(find_budget_candidates({'campaigns':[base]})[0]['type'],'BUDGET_CONSTRAINT_CANDIDATE')
        for key,value in [('kpi_compatible',False),('performance_sufficient',False),('maturity','IMMATURE')]:
            bad=dict(base); bad[key]=value; self.assertEqual(find_budget_candidates({'campaigns':[bad]}), [])
    def test_measurement_risks_surface_context_mismatches(self):
        types={x['type'] for x in find_measurement_risks({'campaigns':[{'campaign_id':1,'kpi_compatible':False,'attribution_compatible':False}]})}
        self.assertIn('KPI_CONTEXT_MISMATCH',types); self.assertIn('ATTRIBUTION_MISMATCH',types)
if __name__ == '__main__': unittest.main()
