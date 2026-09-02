import unittest
from scripts.seo_join import join_queries, join_pages


class JoinTests(unittest.TestCase):
    def test_query_join_is_exact_normalized_only(self):
        records=[{'query':'Купить  пасту','source':'a'},{'query':'купить пасту','source':'b'},{'query':'купить зубную пасту','source':'c'}]
        joined=join_queries(records)
        self.assertEqual(len(joined['купить пасту']),2)
        self.assertEqual(len(joined['купить зубную пасту']),1)

    def test_page_join_keeps_functional_query_parameters(self):
        records=[{'url':'HTTPS://X.test:443/p?id=1#x'},{'url':'https://x.test/p?id=1'},{'url':'https://x.test/p?id=2'}]
        joined=join_pages(records)
        self.assertEqual(len(joined['https://x.test/p?id=1']),2)
        self.assertEqual(len(joined['https://x.test/p?id=2']),1)

    def test_tracking_parameters_do_not_split_same_page(self):
        records=[
            {'url':'https://x.test/p?id=1&utm_source=yandex'},
            {'url':'https://x.test/p?id=1&yclid=abc'},
            {'url':'https://x.test/p?id=1'},
        ]
        joined=join_pages(records)
        self.assertEqual(list(joined), ['https://x.test/p?id=1'])
        self.assertEqual(joined['https://x.test/p?id=1'][0]['tracking_params']['utm_source'], ['yandex'])
        self.assertEqual(joined['https://x.test/p?id=1'][1]['tracking_params']['yclid'], ['abc'])
        self.assertNotIn('tracking_params', joined['https://x.test/p?id=1'][2])


if __name__ == '__main__':
    unittest.main()
