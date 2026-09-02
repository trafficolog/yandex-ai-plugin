import unittest
from scripts.marketing_prioritize import prioritize, delegate_action

class MarketingPrioritizeTests(unittest.TestCase):
    def test_default_prioritization_is_categorical_without_score(self):
        findings=[{'type':'LANDING_MISMATCH_HYPOTHESIS','target':{'url':'u'}},{'type':'MEASUREMENT_RISK','target':{'campaign_id':1}},{'type':'DEMAND_EXPANSION_CANDIDATE','target':{'query':'q'}}]
        result=prioritize(findings); self.assertEqual(result[0]['type'],'MEASUREMENT_RISK'); self.assertTrue(all('score' not in item for item in result))
        custom=prioritize(findings,['DEMAND_EXPANSION_CANDIDATE','MEASUREMENT_RISK']); self.assertEqual(custom[0]['type'],'DEMAND_EXPANSION_CANDIDATE'); self.assertEqual(custom[0]['priority_basis']['mode'],'USER_ORDER')
    def test_delegation_routes_to_owning_plugins_and_requires_approval(self):
        cases=[({'type':'BUDGET_REALLOCATION_CANDIDATE','target':{'campaign_id':1}},'yandex-direct','yandex-direct-budget'),({'type':'SEARCH_TERM_EXCLUSION_REVIEW','target':{'query':'x'}},'yandex-direct','yandex-direct-keywords'),({'type':'SPEND_EFFICIENCY_REVIEW','target':{'campaign_id':1}},'yandex-direct','yandex-direct-optimize'),({'type':'NEW_CAMPAIGN_CANDIDATE','target':{'topic':'x'}},'yandex-direct','yandex-direct-create'),({'type':'GOAL_ALIGNMENT_RISK','target':{'goal_id':1},'recommended_action':'goal_change'},'yandex-metrika','yandex-metrika-goals')]
        for finding,service,skill in cases:
            action=delegate_action(finding); self.assertEqual(action['service'],service); self.assertEqual(action['skill'],skill); self.assertTrue(action['requires_approval']); self.assertEqual(action['mode'],'preview-only')
    def test_unsupported_finding_has_no_executable_delegation(self):
        self.assertIsNone(delegate_action({'type':'LANDING_MISMATCH_HYPOTHESIS','target':{'url':'u'}}))
if __name__ == '__main__': unittest.main()
