import unittest
from scripts.marketing_prioritize import (
    APPROVED_EXTERNAL_FINDING_TYPES,
    DEFAULT_GROUP_ORDER,
    DEFERRED_FINDING_TYPES,
    IMPLEMENTED_FINDING_TYPES,
    prioritize,
    delegate_action,
)


EXPECTED_IMPLEMENTED = {
    'MEASUREMENT_RISK','KPI_CONTEXT_MISMATCH','ATTRIBUTION_MISMATCH',
    'BUDGET_CONSTRAINT_CANDIDATE','BUDGET_REALLOCATION_CANDIDATE',
    'DEMAND_EXPANSION_CANDIDATE','SEARCH_TERM_EXPANSION_CANDIDATE',
    'SEARCH_TERM_EXCLUSION_REVIEW','LANDING_MISMATCH_HYPOTHESIS',
}


class MarketingPrioritizeTests(unittest.TestCase):
    def test_taxonomy_matches_actual_local_finding_producers(self):
        self.assertEqual(IMPLEMENTED_FINDING_TYPES, EXPECTED_IMPLEMENTED)
        self.assertEqual(set(DEFAULT_GROUP_ORDER), EXPECTED_IMPLEMENTED)
        self.assertTrue(EXPECTED_IMPLEMENTED.isdisjoint(DEFERRED_FINDING_TYPES))
        self.assertNotIn('NEW_CAMPAIGN_CANDIDATE', IMPLEMENTED_FINDING_TYPES)
        self.assertNotIn('NEW_CAMPAIGN_CANDIDATE', APPROVED_EXTERNAL_FINDING_TYPES)

    def test_default_prioritization_is_categorical_without_score(self):
        findings=[{'type':'LANDING_MISMATCH_HYPOTHESIS','target':{'url':'u'}},{'type':'MEASUREMENT_RISK','target':{'campaign_id':1}},{'type':'DEMAND_EXPANSION_CANDIDATE','target':{'query':'q'}}]
        result=prioritize(findings)
        self.assertEqual(result[0]['type'],'MEASUREMENT_RISK')
        self.assertTrue(all('score' not in item for item in result))
        custom=prioritize(findings,['DEMAND_EXPANSION_CANDIDATE','MEASUREMENT_RISK'])
        self.assertEqual(custom[0]['type'],'DEMAND_EXPANSION_CANDIDATE')
        self.assertEqual(custom[0]['priority_basis']['mode'],'USER_ORDER')

    def test_unknown_or_deferred_types_sort_after_implemented_and_are_marked(self):
        findings=[
            {'type':'SERP_INTENT_CONTEXT','target':{'query':'q'}},
            {'type':'MEASUREMENT_RISK','target':{'campaign_id':1}},
            {'type':'EXTERNAL_FUTURE_TYPE','target':{}},
        ]
        result=prioritize(findings)
        self.assertEqual(result[0]['type'], 'MEASUREMENT_RISK')
        for item in result[1:]:
            self.assertIn('UNKNOWN_OR_DEFERRED_TYPE', item['limitations'])

    def test_empty_priority_order_uses_default_categorical_mode(self):
        findings=[{'type':'MEASUREMENT_RISK','target':{'campaign_id':1}}]
        result=prioritize(findings, [])
        self.assertEqual(result[0]['priority_basis']['mode'], 'DEFAULT_CATEGORICAL')

    def test_delegation_routes_only_implemented_or_explicitly_approved_external_types(self):
        cases=[
            ({'type':'BUDGET_REALLOCATION_CANDIDATE','target':{'campaign_id':1}},'yandex-direct','yandex-direct-budget'),
            ({'type':'SEARCH_TERM_EXCLUSION_REVIEW','target':{'query':'x'}},'yandex-direct','yandex-direct-keywords'),
            ({'type':'GOAL_ALIGNMENT_RISK','target':{'goal_id':1},'recommended_action':'goal_change'},'yandex-metrika','yandex-metrika-goals'),
        ]
        for finding,service,skill in cases:
            action=delegate_action(finding)
            self.assertEqual(action['service'],service)
            self.assertEqual(action['skill'],skill)
            self.assertTrue(action['requires_approval'])
            self.assertEqual(action['mode'],'preview-only')
        self.assertIn('GOAL_ALIGNMENT_RISK', APPROVED_EXTERNAL_FINDING_TYPES)

    def test_dead_or_deferred_routes_are_not_executable(self):
        for type_ in ['NEW_CAMPAIGN_CANDIDATE','SPEND_EFFICIENCY_REVIEW','QUERY_COVERAGE_GAP']:
            self.assertIsNone(delegate_action({'type':type_,'target':{}}))

    def test_unsupported_finding_has_no_executable_delegation(self):
        self.assertIsNone(delegate_action({'type':'LANDING_MISMATCH_HYPOTHESIS','target':{'url':'u'}}))


if __name__ == '__main__':
    unittest.main()
