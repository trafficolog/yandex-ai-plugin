import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    'yandex-marketing',
    'yandex-marketing-audit',
    'yandex-marketing-performance',
    'yandex-marketing-demand',
    'yandex-marketing-queries',
    'yandex-marketing-landings',
    'yandex-marketing-conversions',
    'yandex-marketing-attribution',
    'yandex-marketing-budget',
    'yandex-marketing-opportunities',
    'yandex-marketing-prioritize',
}

class PluginLayoutTests(unittest.TestCase):
    def test_package_contract(self):
        manifest_path = ROOT / '.codex-plugin/plugin.json'
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest['name'], 'yandex-marketing')
        self.assertEqual(manifest['version'], '1.1.0')
        self.assertEqual(manifest['skills'], './skills/')
        self.assertTrue((ROOT / '.claude-plugin/plugin.json').exists())
        self.assertTrue((ROOT / 'evals/scenarios.json').exists())
        for dirname in ('references', 'scripts', 'tests'):
            self.assertTrue((ROOT / dirname).is_dir())
        found = {p.parent.name for p in (ROOT / 'skills').glob('*/SKILL.md')}
        self.assertEqual(found, SKILLS)
        self.assertFalse((ROOT / '.env.example').exists())

    def test_skill_frontmatter(self):
        for skill in SKILLS:
            text = (ROOT / 'skills' / skill / 'SKILL.md').read_text()
            self.assertTrue(text.startswith('---\n'))
            self.assertIn(f'name: {skill}', text)
            self.assertIn('description: Use when', text)

    def test_1_1_contract_docs_are_exposed(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        findings = (ROOT / 'references/findings.md').read_text(encoding='utf-8')
        evidence = (ROOT / 'references/evidence-bundle.md').read_text(encoding='utf-8')
        self.assertIn('canonical', evidence)
        self.assertIn('reconciliation_only', evidence)
        self.assertIn('enrichment', evidence)
        self.assertIn('IMPLEMENTED_FINDING_TYPES', findings)
        self.assertIn('DEFERRED_FINDING_TYPES', findings)
        self.assertIn('1.1.0', readme)

if __name__ == '__main__':
    unittest.main()
