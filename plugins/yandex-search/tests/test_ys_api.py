import unittest
from scripts._http import auth_headers, redact_headers
from scripts.ys_api import validate_query_text, estimate_cost, recommend_mode, QUOTAS

class TestSearchApi(unittest.TestCase):
    def test_api_key_and_iam_are_mutually_exclusive(self):
        with self.assertRaises(ValueError): auth_headers(api_key='a', iam_token='b')
        with self.assertRaises(ValueError): auth_headers()
    def test_auth_and_redaction(self):
        h=auth_headers(api_key='abc'); self.assertEqual(h['Authorization'],'Api-Key abc'); self.assertEqual(redact_headers(h)['Authorization'],'Api-Key ***'); h=auth_headers(iam_token='tok'); self.assertEqual(h['Authorization'],'Bearer tok')
    def test_query_limits(self):
        self.assertEqual(validate_query_text('  test query  '),'test query')
        with self.assertRaises(ValueError): validate_query_text('x'*401)
        with self.assertRaises(ValueError): validate_query_text(' '.join(['x']*41))
    def test_current_quota_and_cost_baseline(self):
        self.assertEqual(QUOTAS['sync_per_hour'],10000); self.assertEqual(QUOTAS['async_per_hour'],35000); self.assertEqual(estimate_cost(500,mode='sync',period='day')['estimated_rub'],244.0); p=estimate_cost(500,mode='async',period='day'); self.assertEqual(p['estimated_rub'],15.25); self.assertFalse(p['billing_guarantee'])
    def test_mode_recommendation(self):
        self.assertEqual(recommend_mode(3)['mode'],'sync'); self.assertEqual(recommend_mode(50)['mode'],'async')
