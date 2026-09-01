import unittest
from scripts.seo_join import join_queries, join_pages

class JoinTests(unittest.TestCase):
    def test_query_join_is_exact_normalized_only(self):
        records=[{'query':'Купить  пасту','source':'a'},{'query':'купить пасту','source':'b'},{'query':'купить зубную пасту','source':'c'}]
        joined=join_queries(records)
        self.assertEqual(len(joined['купить пасту']),2)
        self.assertEqual(len(joined['купить зубную пасту']),1)

    def test_page_join_keeps_query_parameters(self):
        records=[{'url':'HTTPS://X.test:443/p?id=1#x'},{'url':'https://x.test/p?id=1'},{'url':'https://x.test/p?id=2'}]
        joined=join_pages(records)
        self.assertEqual(len(joined['https://x.test/p?id=1']),2)
        self.assertEqual(len(joined['https://x.test/p?id=2']),1)
