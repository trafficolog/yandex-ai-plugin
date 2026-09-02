import unittest
from scripts.ys_request import build_search_request, config_fingerprint
class TestSearchRequest(unittest.TestCase):
    def test_sync_rest_body_uses_camel_case(self):
        r=build_search_request('hello',folder_id='folder',api_key='key',region=213); self.assertTrue(r['url'].endswith('/v2/web/search')); self.assertEqual(r['body']['query']['queryText'],'hello'); self.assertEqual(r['body']['folderId'],'folder'); self.assertEqual(r['body']['groupSpec']['groupMode'],'GROUP_MODE_FLAT'); self.assertEqual(r['body']['groupSpec']['docsInGroup'],'1'); self.assertEqual(r['preview']['headers']['Authorization'],'Api-Key ***')
    def test_async_endpoint(self): self.assertTrue(build_search_request('hello',folder_id='f',iam_token='t',mode='async')['url'].endswith('/v2/web/searchAsync'))
    def test_invalid_search_type_rejected(self):
        with self.assertRaises(ValueError): build_search_request('x',folder_id='f',api_key='k',search_type='SEARCH_TYPE_EN')
    def test_fingerprint_is_stable_and_ignores_query_text(self):
        a=build_search_request('one',folder_id='f',api_key='k',region=213); b=build_search_request('two',folder_id='f',api_key='k',region=213); self.assertEqual(config_fingerprint(a['body']),config_fingerprint(b['body']))
