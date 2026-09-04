import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILLS=['yandex-marketing','yandex-marketing-audit','yandex-marketing-performance','yandex-marketing-demand','yandex-marketing-queries','yandex-marketing-landings','yandex-marketing-conversions','yandex-marketing-attribution','yandex-marketing-budget','yandex-marketing-opportunities','yandex-marketing-prioritize']
REFS=['evidence-bundle.md','kpi-context.md','reconciliation.md','findings.md','quality.md','safety.md','sources.md']

class AgentContractTests(unittest.TestCase):
    def text(self, skill): return (ROOT/'skills'/skill/'SKILL.md').read_text().lower()
    def test_router_requires_direct_and_search_is_optional(self):
        text=self.text('yandex-marketing'); self.assertIn('direct is required',text); self.assertIn('search is optional',text); self.assertIn('route',text)
    def test_reconciliation_and_kpi_contracts_are_explicit(self):
        conversions=self.text('yandex-marketing-conversions'); self.assertIn('never sum',conversions); self.assertIn('kpi fingerprint',conversions)
        attribution=self.text('yandex-marketing-attribution'); self.assertIn('incomparable',attribution); self.assertIn('volatile attribution',attribution)
        performance=self.text('yandex-marketing-performance'); self.assertIn('currency',performance); self.assertIn('vat',performance); self.assertIn('maturity',performance)
    def test_demand_query_and_budget_stop_conditions(self):
        demand=self.text('yandex-marketing-demand'); self.assertIn('not guaranteed ad inventory',demand); self.assertIn('missed traffic',demand)
        queries=self.text('yandex-marketing-queries'); self.assertIn('zero conversions',queries); self.assertIn('not an automatic negative',queries)
        budget=self.text('yandex-marketing-budget'); self.assertIn('preview',budget); self.assertIn('explicit approval',budget); self.assertIn('no universal',budget)
    def test_no_transport_credentials_or_runtime_specific_paths(self):
        forbidden=('https://','authorization:','oauth','api-key','bearer ','yandex_direct_token','yandex_metrika_token','~/.claude','~/.codex','~/.openclaw')
        for skill in SKILLS:
            text=self.text(skill)
            for token in forbidden: self.assertNotIn(token,text,(skill,token))
    def test_readme_capability_matrix_and_reference_date(self):
        readme=(ROOT/'README.md').read_text(); self.assertIn('| Capability | Read | Write |',readme)
        sources=(ROOT/'references'/'sources.md').read_text(); self.assertIn('Verified: 2026-09-02',sources)
    def test_references_and_eval_contract(self):
        for ref in REFS: self.assertTrue((ROOT/'references'/ref).exists(),ref)
        data=json.loads((ROOT/'evals/scenarios.json').read_text())
        self.assertEqual(data['version'],2)
        self.assertGreaterEqual(len(data['scenarios']),len(SKILLS))
        self.assertEqual({s['skill'] for s in data['scenarios']},set(SKILLS))
        self.assertTrue(all(s['write'] in (False,'preview-first') for s in data['scenarios']))
        self.assertTrue(all(isinstance(s['prompt'],str) and s['prompt'].strip() for s in data['scenarios']))
        self.assertTrue(all(isinstance(s.get('expect'),dict) for s in data['scenarios']))
        self.assertTrue(all(s['expect'].get('must_route_to') == s['skill'] for s in data['scenarios']))
        self.assertTrue(all(s['expect'].get('outcome') in ('comply','comply_with_limitations','refuse') for s in data['scenarios']))
        self.assertTrue(all(isinstance(s['expect'].get('must_mention_tokens'),list) for s in data['scenarios']))
        self.assertTrue(all(isinstance(s['expect'].get('must_convey'),list) for s in data['scenarios']))
        self.assertTrue(all(isinstance(s['expect'].get('must_not_claim'),list) for s in data['scenarios']))
if __name__=='__main__': unittest.main()
