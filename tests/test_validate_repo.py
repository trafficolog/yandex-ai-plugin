import json
from pathlib import Path
import tempfile
import unittest

from scripts.validate_repo import validate_repository


class ValidateRepositoryTests(unittest.TestCase):
    def make_repo(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / '.agents/plugins').mkdir(parents=True)
        plugin = root / 'plugins/yandex-direct'
        (plugin / '.codex-plugin').mkdir(parents=True)
        (plugin / 'skills/yandex-direct').mkdir(parents=True)
        (plugin / 'evals').mkdir(parents=True)
        (root / '.agents/plugins/marketplace.json').write_text(json.dumps({
            'name': 'test-marketplace',
            'plugins': [{
                'name': 'yandex-direct-suite',
                'source': {'source': 'local', 'path': './plugins/yandex-direct'}
            }]
        }), encoding='utf-8')
        (plugin / '.codex-plugin/plugin.json').write_text(json.dumps({
            'name': 'yandex-direct-suite',
            'version': '1.0.0',
            'skills': './skills/'
        }), encoding='utf-8')
        (plugin / 'skills/yandex-direct/SKILL.md').write_text(
            '---\nname: yandex-direct\ndescription: Use when working with Yandex Direct.\n---\n',
            encoding='utf-8'
        )
        (plugin / 'evals/scenarios.json').write_text(json.dumps({
            'version': 1,
            'scenarios': [{'prompt': 'audit', 'skill': 'yandex-direct', 'write': False}]
        }), encoding='utf-8')
        return tmp, root, plugin

    def test_valid_repository_has_no_errors(self):
        tmp, root, _ = self.make_repo()
        self.addCleanup(tmp.cleanup)
        self.assertEqual(validate_repository(root), [])

    def test_missing_marketplace_source_path_is_reported(self):
        tmp, root, _ = self.make_repo()
        self.addCleanup(tmp.cleanup)
        data = json.loads((root / '.agents/plugins/marketplace.json').read_text())
        data['plugins'][0]['source']['path'] = './plugins/missing'
        (root / '.agents/plugins/marketplace.json').write_text(json.dumps(data))
        self.assertTrue(any('does not exist' in e for e in validate_repository(root)))

    def test_missing_codex_manifest_is_reported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (plugin / '.codex-plugin/plugin.json').unlink()
        self.assertTrue(any('.codex-plugin/plugin.json' in e for e in validate_repository(root)))

    def test_missing_skills_target_is_reported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        for path in (plugin / 'skills').rglob('*'):
            if path.is_file():
                path.unlink()
        (plugin / 'skills/yandex-direct').rmdir()
        (plugin / 'skills').rmdir()
        self.assertTrue(any('skills target' in e for e in validate_repository(root)))

    def test_missing_skill_frontmatter_is_reported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (plugin / 'skills/yandex-direct/SKILL.md').write_text('# no frontmatter\n')
        self.assertTrue(any('frontmatter' in e for e in validate_repository(root)))

    def test_skill_description_must_start_use_when(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (plugin / 'skills/yandex-direct/SKILL.md').write_text(
            '---\nname: yandex-direct\ndescription: Yandex Direct helper.\n---\n'
        )
        self.assertTrue(any('Use when' in e for e in validate_repository(root)))

    def test_runtime_specific_absolute_paths_are_reported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        skill = plugin / 'skills/yandex-direct/SKILL.md'
        skill.write_text(skill.read_text() + '\nRun ~/.openclaw/workspace/tool.sh\n')
        self.assertTrue(any('runtime-specific absolute path' in e for e in validate_repository(root)))

    def test_malformed_evals_are_reported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (plugin / 'evals/scenarios.json').write_text('{bad json')
        self.assertTrue(any('evals/scenarios.json' in e for e in validate_repository(root)))


if __name__ == '__main__':
    unittest.main()
