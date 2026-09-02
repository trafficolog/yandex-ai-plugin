import unittest
from scripts.marketing_quality import canonical_metric, reconcile_metric, propagate_limitations, capability_mode

class MarketingQualityTests(unittest.TestCase):
    def test_canonical_source_rules_prevent_double_counting(self):
        records = [{'metric':'cost','value':100,'source':'yandex-direct'},{'metric':'cost','value':98,'source':'yandex-metrika'}]
        self.assertEqual(canonical_metric('cost', records)['source'], 'yandex-direct')
        conversions = [{'metric':'conversions','value':10,'source':'yandex-direct'},{'metric':'conversions','value':12,'source':'yandex-metrika'}]
        self.assertEqual(canonical_metric('conversions', conversions)['source'], 'yandex-metrika')

    def test_reconciliation_uses_context_not_automatic_sum_or_threshold(self):
        kpi={'business_objective':'purchase','goal_ids':['1'],'attribution_model':'automatic','metric_basis':'converted_sessions','currency':'RUB','vat_basis':'excluded','period':{'from':'2026-08-01','to':'2026-08-31'}}
        records=[{'metric':'conversions','value':10,'source':'yandex-direct','kpi':kpi},{'metric':'conversions','value':10,'source':'yandex-metrika','kpi':kpi}]
        result=reconcile_metric('conversions', records, {})
        self.assertEqual(result['status'], 'ALIGNED')
        self.assertNotIn('total', result)
        changed=[dict(records[0]), dict(records[1])]; changed[1]['value']=12
        self.assertEqual(reconcile_metric('conversions', changed, {})['status'], 'REVIEW')
        self.assertEqual(reconcile_metric('conversions', changed, {'known_difference_reason':'click-date vs conversion-date'})['status'], 'EXPLAINABLE_DIFFERENCE')
        bad=dict(changed[1]); bad['kpi']={**kpi,'goal_ids':['9']}
        self.assertEqual(reconcile_metric('conversions', [changed[0],bad], {})['status'], 'INCOMPARABLE')

    def test_limitations_and_capability_modes(self):
        limits=propagate_limitations([{'source':'yandex-metrika','sampled':True,'sample_share':0.2,'data_lag':120},{'source':'yandex-direct','maturity':'IMMATURE'},{'source':'yandex-search','bridge_risk':True}])
        codes={x['code'] for x in limits}
        self.assertTrue({'METRIKA_SAMPLED','DATA_LAG','IMMATURE','SEARCH_BRIDGE_RISK'} <= codes)
        self.assertEqual(capability_mode({'direct':True}), 'DIRECT_ONLY')
        self.assertEqual(capability_mode({'direct':True,'metrika':True}), 'PAID_PERFORMANCE')
        self.assertEqual(capability_mode({'direct':True,'wordstat':True}), 'DEMAND_PLANNING')
        self.assertEqual(capability_mode({'direct':True,'wordstat':True,'workflow':'queries'}), 'QUERY_INTELLIGENCE')
        self.assertEqual(capability_mode({'direct':True,'metrika':True,'wordstat':True}), 'FULL_ACQUISITION')
        self.assertEqual(capability_mode({'direct':True,'search':True}), 'COMPETITIVE_CONTEXT')
        with self.assertRaises(ValueError): capability_mode({'direct':False,'metrika':True})

if __name__ == '__main__': unittest.main()
