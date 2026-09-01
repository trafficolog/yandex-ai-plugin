import unittest
from scripts.seo_context import normalize_query, normalize_url, classify_period_alignment

class ContextTests(unittest.TestCase):
    def test_query_normalization_is_conservative(self):
        self.assertEqual(normalize_query('  КУПИТЬ\u00a0  Пасту  '), 'купить пасту')
        self.assertNotEqual(normalize_query('купить пасту'), normalize_query('купить зубную пасту'))

    def test_url_keeps_query_parameters(self):
        self.assertEqual(normalize_url('HTTPS://Example.COM:443/path?b=2&a=1#x'), 'https://example.com/path?a=1&b=2')
        self.assertNotEqual(normalize_url('https://x.test/p?id=1'), normalize_url('https://x.test/p?id=2'))

    def test_period_alignment(self):
        exact=[{'period':{'from':'2026-08-01','to':'2026-08-31'}},{'period':{'from':'2026-08-01','to':'2026-08-31'}}]
        self.assertEqual(classify_period_alignment(exact),'EXACT')
        approx=[{'period':{'from':'2026-08-01','to':'2026-08-31'}},{'window':'rolling_30_days'}]
        self.assertEqual(classify_period_alignment(approx),'APPROXIMATE')
        mismatch=[{'period':{'from':'2026-07-01','to':'2026-07-31'}},{'period':{'from':'2026-08-01','to':'2026-08-31'}}]
        self.assertEqual(classify_period_alignment(mismatch),'MISMATCHED')
