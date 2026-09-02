import unittest
from scripts.seo_prioritize import prioritize, delegate_action

class PrioritizeTests(unittest.TestCase):
    def test_default_has_no_hidden_score(self):
        findings=[
          {'type':'DISCOVERY_CANDIDATE','confidence':'LOW'},
          {'type':'TECHNICAL_BLOCKER','confidence':'HIGH'},
        ]
        out=prioritize(findings)
        self.assertEqual(out[0]['type'],'TECHNICAL_BLOCKER')
        self.assertTrue(all('score' not in x and 'seo_score' not in x for x in out))

    def test_user_priority_order_is_explicit(self):
        findings=[{'type':'CONTENT_GAP'},{'type':'CTR_OPPORTUNITY'}]
        out=prioritize(findings, ['CTR_OPPORTUNITY','CONTENT_GAP'])
        self.assertEqual([x['type'] for x in out],['CTR_OPPORTUNITY','CONTENT_GAP'])
        self.assertEqual(out[0]['priority_basis'],'user-provided-order')

    def test_recrawl_delegates_to_webmaster(self):
        f={'type':'TECHNICAL_BLOCKER','issue':'NOT_INDEXED','url_key':'https://x/p'}
        d=delegate_action(f)
        self.assertEqual(d['service'],'yandex-webmaster')
        self.assertEqual(d['skill'],'yandex-webmaster-recrawl')
        self.assertTrue(d['requires_approval'])

    def test_sitemap_delegation_and_unsupported(self):
        d=delegate_action({'type':'SITEMAP_ACTION','target':'https://x/sitemap.xml'})
        self.assertEqual(d['skill'],'yandex-webmaster-sitemaps')
        self.assertIsNone(delegate_action({'type':'CONTENT_GAP','query_key':'x'}))
