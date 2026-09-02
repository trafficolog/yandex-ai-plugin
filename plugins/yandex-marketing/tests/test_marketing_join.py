import unittest
from scripts.marketing_join import join_campaigns, join_goals, join_queries, join_landings


class MarketingJoinTests(unittest.TestCase):
    def test_campaigns_and_goals_join_by_ids_not_names(self):
        campaigns = join_campaigns([{'campaign_id':1,'campaign_name':'Search'},{'campaign_id':2,'campaign_name':'Search'}])
        self.assertEqual(set(campaigns), {'1','2'})
        goals = join_goals([{'goal_id':10,'goal_name':'Purchase'},{'goal_id':11,'goal_name':'Purchase'}])
        self.assertEqual(set(goals), {'10','11'})

    def test_query_join_is_exact_normalized_only(self):
        joined = join_queries([{'query':' Купить  пасту '},{'query':'купить пасту'},{'query':'купить зубную пасту'}])
        self.assertEqual(len(joined['купить пасту']), 2)
        self.assertIn('купить зубную пасту', joined)

    def test_landing_join_preserves_functional_parameters(self):
        joined = join_landings([{'url':'https://example.com/p?id=1'},{'url':'https://example.com/p?id=2'}])
        self.assertEqual(len(joined), 2)

    def test_tracking_parameters_do_not_split_same_landing(self):
        joined = join_landings([
            {'url':'https://example.com/p?id=1&utm_source=yandex&utm_medium=cpc'},
            {'url':'https://example.com/p?yclid=123&id=1'},
            {'url':'https://example.com/p?id=1&_openstat=x'},
            {'url':'https://example.com/p?id=1'},
        ])
        self.assertEqual(list(joined), ['https://example.com/p?id=1'])
        rows = joined['https://example.com/p?id=1']
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]['url_key'], 'https://example.com/p?id=1')
        self.assertEqual(rows[0]['tracking_params']['utm_source'], ['yandex'])
        self.assertEqual(rows[0]['tracking_params']['utm_medium'], ['cpc'])
        self.assertEqual(rows[1]['tracking_params']['yclid'], ['123'])
        self.assertEqual(rows[2]['tracking_params']['_openstat'], ['x'])
        self.assertNotIn('tracking_params', rows[3])


if __name__ == '__main__':
    unittest.main()
