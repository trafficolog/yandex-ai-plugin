import unittest
from scripts.ys_compare import compare_rankings, competitor_presence
def snap(q,rows,fp='same'): return {'query':q,'config_fingerprint':fp,'results':[{'rank':rank,'url_key':url,'host':host} for rank,url,host in rows]}
class TestCompare(unittest.TestCase):
    def test_different_queries_rejected(self):
        with self.assertRaises(ValueError): compare_rankings(snap('a',[]),snap('b',[]))
    def test_incompatible_fingerprints_rejected(self):
        with self.assertRaises(ValueError): compare_rankings(snap('q',[],fp='a'),snap('q',[],fp='b'))
    def test_rank_delta(self): self.assertEqual(compare_rankings(snap('q',[(4,'https://x/a','x')]),snap('q',[(2,'https://x/a','x')]))['changes'][0]['delta'],2)
    def test_competitor_presence(self):
        out=competitor_presence([snap('a',[(2,'u1','example.com')]),snap('b',[(8,'u2','example.com')]),snap('c',[(1,'u3','other.com')])],'example.com'); self.assertEqual(out['queries_present'],2); self.assertEqual(out['top_3_presence'],1); self.assertEqual(out['top_10_presence'],2); self.assertEqual(out['median_rank_when_present'],5.0); self.assertEqual(out['metric_name'],'SERP presence rate')
