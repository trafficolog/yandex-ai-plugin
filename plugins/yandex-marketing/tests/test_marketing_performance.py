import unittest
from scripts.marketing_performance import derive_performance, compare_performance, reconcile_conversions

KPI={'business_objective':'purchase','goal_ids':['1'],'attribution_model':'automatic','metric_basis':'converted_sessions','currency':'RUB','vat_basis':'excluded','period':{'from':'2026-08-01','to':'2026-08-31'}}

class MarketingPerformanceTests(unittest.TestCase):
    def test_derives_only_supported_metrics(self):
        result=derive_performance({'impressions':1000,'clicks':100,'cost':5000,'conversions':10,'revenue':15000,'maturity':'MATURE'}, KPI)
        self.assertEqual(result['cpc'],50); self.assertEqual(result['ctr'],0.1); self.assertEqual(result['cr'],0.1); self.assertEqual(result['cpa'],500); self.assertEqual(result['roas'],3)
        no_revenue=derive_performance({'clicks':10,'cost':100,'conversions':1}, KPI)
        self.assertNotIn('roas', no_revenue); self.assertNotIn('drr', no_revenue)

    def test_compare_blocks_different_goals_and_currency(self):
        a=derive_performance({'cost':100,'conversions':2}, KPI)
        b=derive_performance({'cost':100,'conversions':5}, {**KPI,'goal_ids':['micro']})
        self.assertEqual(compare_performance(a,b)['status'], 'INCOMPARABLE')
        c=derive_performance({'cost':100,'conversions':5}, {**KPI,'currency':'EUR'})
        self.assertEqual(compare_performance(a,c)['status'], 'INCOMPARABLE')

    def test_immature_data_is_disclosed(self):
        result=derive_performance({'cost':100,'conversions':1,'maturity':'IMMATURE'}, KPI)
        self.assertIn('IMMATURE', result['limitations'])

    def test_conversion_reconciliation_can_be_explainable(self):
        direct={'metric':'conversions','value':10,'source':'yandex-direct','kpi':KPI}; metrika={'metric':'conversions','value':12,'source':'yandex-metrika','kpi':KPI}
        self.assertEqual(reconcile_conversions(direct,metrika,{'known_difference_reason':'different date basis'})['status'],'EXPLAINABLE_DIFFERENCE')
        bad={**metrika,'kpi':{**KPI,'attribution_model':'other'}}
        self.assertEqual(reconcile_conversions(direct,bad,{})['status'],'INCOMPARABLE')

if __name__ == '__main__': unittest.main()
