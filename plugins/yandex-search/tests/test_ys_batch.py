import unittest
from scripts.ys_batch import plan_batch
class TestBatch(unittest.TestCase):
    def test_small_workload_recommends_sync(self): self.assertEqual(plan_batch(['a','b'])['recommended_mode'],'sync')
    def test_large_workload_recommends_async_and_shows_both_costs(self):
        p=plan_batch([f'q{i}' for i in range(50)]); self.assertEqual(p['recommended_mode'],'async'); self.assertIn('sync',p['cost_preview']); self.assertIn('async',p['cost_preview']); self.assertLess(p['cost_preview']['async']['estimated_rub'],p['cost_preview']['sync']['estimated_rub'])
    def test_dedupes_queries_without_reordering(self): self.assertEqual(plan_batch(['a','b','a'])['queries'],['a','b'])
