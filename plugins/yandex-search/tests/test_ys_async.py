import unittest
from datetime import datetime, timezone
from scripts.ys_async import operation_record, operation_status_request, retention_state, collect_operation_response
class TestAsync(unittest.TestCase):
    def test_operation_record_preserves_id_and_query(self):
        r=operation_record('q',{'id':'op1','done':False,'createdAt':'2026-09-01T10:00:00Z'}); self.assertEqual(r['operation_id'],'op1'); self.assertEqual(r['query'],'q'); self.assertEqual(r['state'],'pending')
    def test_status_request_uses_operation_url(self):
        r=operation_status_request('op1',api_key='k'); self.assertTrue(r['url'].endswith('/operations/op1')); self.assertEqual(r['preview']['headers']['Authorization'],'Api-Key ***')
    def test_collect_requires_done_operation(self):
        with self.assertRaises(ValueError): collect_operation_response({'done':False})
    def test_retention_state(self):
        now=datetime(2026,9,1,20,0,tzinfo=timezone.utc); self.assertEqual(retention_state('2026-09-01T10:00:00+00:00',now=now)['state'],'expiring_soon'); self.assertEqual(retention_state('2026-09-01T07:00:00+00:00',now=now)['state'],'expired')
