import unittest
from scripts.ys_overlap import pairwise_overlap, cluster_queries
def snap(q,urls): return {'query':q,'config_fingerprint':'same','group_mode':'GROUP_MODE_FLAT','docs_in_group':1,'results':[{'url_key':u} for u in urls]}
class TestOverlap(unittest.TestCase):
    def test_pairwise_metrics(self):
        m=pairwise_overlap(snap('a',['u1','u2','u3']),snap('b',['u2','u3','u4']),top_k=3); self.assertEqual(m['shared_urls'],2); self.assertAlmostEqual(m['jaccard'],0.5)
    def test_threshold_is_required(self):
        with self.assertRaises(TypeError): cluster_queries([snap('a',['u1'])])
    def test_incompatible_fingerprints_rejected(self):
        a=snap('a',['u1']); b=snap('b',['u1']); b['config_fingerprint']='other'
        with self.assertRaises(ValueError): cluster_queries([a,b],min_shared_urls=1)
    def test_disjoint_queries_stay_separate(self): self.assertEqual(len(cluster_queries([snap('a',['u1']),snap('b',['u2'])],min_shared_urls=1)['clusters']),2)
    def test_bridge_risk_is_reported(self):
        snaps=[snap('a',['1','2','3']),snap('b',['1','2','4']),snap('c',['2','4','5'])]; c=cluster_queries(snaps,min_shared_urls=2,top_k=3); self.assertEqual(len(c['clusters']),1); self.assertTrue(c['clusters'][0]['bridge_risk']); self.assertEqual(c['clusters'][0]['weakest_pair']['shared_urls'],1)
