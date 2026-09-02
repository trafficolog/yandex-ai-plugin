import unittest
from scripts.marketing_quality import canonical_metric, reconcile_metric, propagate_limitations, capability_mode


class MarketingQualityTests(unittest.TestCase):
    def test_canonical_source_rules_select_source_of_truth(self):
        records = [
            {'metric':'cost','value':100,'source':'yandex-direct'},
            {'metric':'cost','value':98,'source':'yandex-metrika'},
        ]
        self.assertEqual(canonical_metric('cost', records)['source'], 'yandex-direct')
        conversions = [
            {'metric':'conversions','value':10,'source':'yandex-direct'},
            {'metric':'conversions','value':12,'source':'yandex-metrika'},
        ]
        self.assertEqual(canonical_metric('conversions', conversions)['source'], 'yandex-metrika')

    def test_reconciliation_returns_canonical_record_without_summing(self):
        kpi={
            'business_objective':'purchase','goal_ids':['1'],'attribution_model':'automatic',
            'metric_basis':'converted_sessions','currency':'RUB','vat_basis':'excluded',
            'period':{'from':'2026-08-01','to':'2026-08-31'},
        }
        records=[
            {'metric':'conversions','value':10,'source':'yandex-direct','kpi':kpi},
            {'metric':'conversions','value':10,'source':'yandex-metrika','kpi':kpi},
        ]
        result=reconcile_metric('conversions', records, {})
        self.assertEqual(result['status'], 'ALIGNED')
        self.assertEqual(result['canonical']['source'], 'yandex-metrika')
        self.assertNotIn('total', result)
        changed=[dict(records[0]), dict(records[1])]
        changed[1]['value']=12
        review=reconcile_metric('conversions', changed, {})
        self.assertEqual(review['status'], 'REVIEW')
        self.assertEqual(review['canonical']['source'], 'yandex-metrika')
        explainable=reconcile_metric('conversions', changed, {'known_difference_reason':'click-date vs conversion-date'})
        self.assertEqual(explainable['status'], 'EXPLAINABLE_DIFFERENCE')
        self.assertEqual(explainable['canonical']['source'], 'yandex-metrika')
        bad=dict(changed[1])
        bad['kpi']={**kpi,'goal_ids':['9']}
        incomparable=reconcile_metric('conversions', [changed[0],bad], {})
        self.assertEqual(incomparable['status'], 'INCOMPARABLE')
        self.assertEqual(incomparable['canonical']['source'], 'yandex-metrika')

    def test_metrika_limitations_use_nested_producer_quality_shape(self):
        metrika_artifact = {
            'source': 'yandex-metrika',
            'data': {'sampled': True, 'sample_share': 0.2, 'data_lag': 120},
            'quality': {'sampled': True, 'sample_share': 0.2, 'data_lag': 120},
            'metadata': {'attribution_model': 'last'},
        }
        limits=propagate_limitations([
            metrika_artifact,
            {'source':'yandex-direct','maturity':'IMMATURE'},
            {'source':'yandex-search','bridge_risk':True},
        ])
        codes={x['code'] for x in limits}
        self.assertTrue({'METRIKA_SAMPLED','DATA_LAG','IMMATURE','SEARCH_BRIDGE_RISK'} <= codes)
        sampled=next(item for item in limits if item['code']=='METRIKA_SAMPLED')
        self.assertEqual(sampled['sample_share'], 0.2)

    def test_missing_metrika_quality_metadata_is_explicit(self):
        limits=propagate_limitations([{'source':'yandex-metrika','data':{},'metadata':{}}])
        self.assertIn('QUALITY_METADATA_MISSING', {item['code'] for item in limits})

    def test_capability_modes(self):
        self.assertEqual(capability_mode({'direct':True}), 'DIRECT_ONLY')
        self.assertEqual(capability_mode({'direct':True,'metrika':True}), 'PAID_PERFORMANCE')
        self.assertEqual(capability_mode({'direct':True,'wordstat':True}), 'DEMAND_PLANNING')
        self.assertEqual(capability_mode({'direct':True,'wordstat':True,'workflow':'queries'}), 'QUERY_INTELLIGENCE')
        self.assertEqual(capability_mode({'direct':True,'metrika':True,'wordstat':True}), 'FULL_ACQUISITION')
        self.assertEqual(capability_mode({'direct':True,'search':True}), 'COMPETITIVE_CONTEXT')
        self.assertEqual(capability_mode({'direct':False,'metrika':True}), 'ROUTING_REQUIRED')


if __name__ == '__main__':
    unittest.main()
