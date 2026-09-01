import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class AgentContractTests(unittest.TestCase):
    def test_reference_set(self):
        for name in ['evidence-bundle.md','alignment.md','findings.md','quality.md','safety.md','sources.md']:
            self.assertTrue((ROOT/'references'/name).is_file(), name)

    def test_skills_are_production_workflows(self):
        requirements={
          'yandex-seo':['coverage','partial','OBSERVED'],
          'yandex-seo-audit':['OBSERVED','DERIVED','HYPOTHESIS','limitations'],
          'yandex-seo-opportunities':['Wordstat','Webmaster','demand','transparent'],
          'yandex-seo-clusters':['min_shared_urls','bridge_risk','Search'],
          'yandex-seo-content-gaps':['DISCOVERY_CANDIDATE','CONTENT_GAP','Webmaster'],
          'yandex-seo-cannibalization':['CANNIBALIZATION_CANDIDATE','Search','Webmaster'],
          'yandex-seo-ctr':['own','baseline','Webmaster'],
          'yandex-seo-conversions':['Metrika','Webmaster','HYPOTHESIS'],
          'yandex-seo-technical':['delegated','approval','Webmaster'],
          'yandex-seo-prioritize':['opaque','priority','requires_approval'],
        }
        for skill, needles in requirements.items():
            text=(ROOT/'skills'/skill/'SKILL.md').read_text(encoding='utf-8')
            self.assertGreater(len(text), 250, skill)
            for needle in needles: self.assertIn(needle,text,skill)
            for forbidden in ['http://','https://','YANDEX_','API_KEY','OAuth']:
                self.assertNotIn(forbidden,text,skill)

    def test_evals_cover_all_skills_and_are_read_only(self):
        data=json.loads((ROOT/'evals/scenarios.json').read_text(encoding='utf-8'))
        skills={x['skill'] for x in data['scenarios']}
        expected={p.parent.name for p in (ROOT/'skills').glob('*/SKILL.md')}
        self.assertEqual(skills,expected)
        self.assertTrue(all(x['write'] in (False,'preview-first') for x in data['scenarios']))
