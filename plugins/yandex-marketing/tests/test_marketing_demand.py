import unittest
from scripts.marketing_demand import find_demand_candidates

class MarketingDemandTests(unittest.TestCase):
    def test_demand_is_candidate_not_missed_traffic(self):
        bundle={'demand':[{'query':'детская паста','wordstat_count':12000,'direct_coverage':'weak','context_compatible':True,'source':'yandex-wordstat'},{'query':'другая','wordstat_count':5000,'direct_coverage':'strong','context_compatible':True,'source':'yandex-wordstat'}]}
        findings=find_demand_candidates(bundle)
        self.assertEqual(len(findings),1); self.assertEqual(findings[0]['type'],'DEMAND_EXPANSION_CANDIDATE'); self.assertNotIn('missed_traffic', findings[0]); self.assertEqual(findings[0]['kind'],'DERIVED')
    def test_incompatible_context_does_not_create_candidate(self):
        self.assertEqual(find_demand_candidates({'demand':[{'query':'x','wordstat_count':10000,'direct_coverage':'weak','context_compatible':False}]}), [])
if __name__ == '__main__': unittest.main()
