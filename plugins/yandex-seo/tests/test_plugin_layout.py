import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    'yandex-seo','yandex-seo-audit','yandex-seo-opportunities','yandex-seo-clusters',
    'yandex-seo-content-gaps','yandex-seo-cannibalization','yandex-seo-ctr',
    'yandex-seo-conversions','yandex-seo-technical','yandex-seo-prioritize'
}

class PluginLayoutTests(unittest.TestCase):
    def test_manifest_contract(self):
        p = ROOT / '.codex-plugin/plugin.json'
        data = json.loads(p.read_text(encoding='utf-8'))
        self.assertEqual(data['name'], 'yandex-seo')
        self.assertEqual(data['version'], '1.0.1')
        self.assertEqual(data['skills'], './skills/')

    def test_exact_skill_set(self):
        got = {p.parent.name for p in (ROOT/'skills').glob('*/SKILL.md')}
        self.assertEqual(got, SKILLS)

    def test_docs_and_dirs(self):
        for rel in ['README.md','CHANGELOG.md','THIRD_PARTY_NOTICES.md','evals/scenarios.json','references','scripts','tests']:
            self.assertTrue((ROOT/rel).exists(), rel)

    def test_no_credentials_contract(self):
        self.assertFalse((ROOT/'.env.example').exists())
        text = (ROOT/'.codex-plugin/plugin.json').read_text(encoding='utf-8')
        for token in ['YANDEX_TOKEN','API_KEY','OAuth','credential']:
            self.assertNotIn(token, text)

if __name__ == '__main__': unittest.main()
