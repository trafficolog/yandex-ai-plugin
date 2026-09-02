import json
from pathlib import Path
import tempfile
import unittest

from scripts.validate_repo import validate_repository


CAPABILITY_TABLE = """| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Example | yes | no | optional | yes | yes |
"""


class ValidateRepositoryTests(unittest.TestCase):
    def make_repo(self, *, plugin_dir='yandex-direct', plugin_name='yandex-direct-suite'):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / '.agents/plugins').mkdir(parents=True)
        (root / '.claude-plugin').mkdir(parents=True)
        plugin = root / f'plugins/{plugin_dir}'
        (plugin / '.codex-plugin').mkdir(parents=True)
        (plugin / '.claude-plugin').mkdir(parents=True)
        (plugin / 'skills/router').mkdir(parents=True)
        (plugin / 'evals').mkdir(parents=True)
        (plugin / 'references').mkdir(parents=True)
        (plugin / 'scripts').mkdir(parents=True)

        agents_entry = {
            'name': plugin_name,
            'version': '1.0.0',
            'source': {'source': 'local', 'path': f'./plugins/{plugin_dir}'},
        }
        (root / '.agents/plugins/marketplace.json').write_text(json.dumps({
            'name': 'test-marketplace',
            'plugins': [agents_entry],
        }), encoding='utf-8')
        (root / '.claude-plugin/marketplace.json').write_text(json.dumps({
            'name': 'test-marketplace',
            'plugins': [{
                'name': plugin_name,
                'source': f'./plugins/{plugin_dir}',
                'version': '1.0.0',
            }],
        }), encoding='utf-8')
        manifest = {
            'name': plugin_name,
            'version': '1.0.0',
            'skills': './skills/',
        }
        (plugin / '.codex-plugin/plugin.json').write_text(json.dumps(manifest), encoding='utf-8')
        (plugin / '.claude-plugin/plugin.json').write_text(json.dumps(manifest), encoding='utf-8')
        (plugin / 'skills/router/SKILL.md').write_text(
            '---\nname: router\ndescription: Use when working with the plugin.\n---\n',
            encoding='utf-8',
        )
        (plugin / 'evals/scenarios.json').write_text(json.dumps({
            'version': 1,
            'scenarios': [{
                'prompt': 'audit',
                'skill': 'router',
                'write': False,
                'expect': {
                    'must_route_to': 'router',
                    'must_refuse': False,
                    'must_mention': [],
                    'must_not_claim': ['live write completed'],
                },
            }],
        }), encoding='utf-8')
        (plugin / 'README.md').write_text(
            f'# {plugin_name}\n\nVersion 1.0.0\n\n{CAPABILITY_TABLE}',
            encoding='utf-8',
        )
        (plugin / 'CHANGELOG.md').write_text(
            '# Changelog\n\n## 1.0.0 — 2026-09-02\n\n- Initial.\n',
            encoding='utf-8',
        )
        (root / 'README.md').write_text(
            f'| [`{plugin_dir}`](plugins/{plugin_dir}/) | 1.0.0 | service | test | No |\n',
            encoding='utf-8',
        )
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
        self.assertTrue(any('does not exist' in error for error in validate_repository(root)))

    def test_missing_codex_manifest_is_reported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (plugin / '.codex-plugin/plugin.json').unlink()
        self.assertTrue(any('.codex-plugin/plugin.json' in error for error in validate_repository(root)))

    def test_missing_claude_manifest_or_marketplace_is_reported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (plugin / '.claude-plugin/plugin.json').unlink()
        self.assertTrue(any('.claude-plugin/plugin.json' in error for error in validate_repository(root)))
        (plugin / '.claude-plugin/plugin.json').write_text('{}')
        (root / '.claude-plugin/marketplace.json').unlink()
        self.assertTrue(any('.claude-plugin/marketplace.json' in error for error in validate_repository(root)))

    def test_version_mismatch_across_manifests_is_reported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        manifest_path = plugin / '.claude-plugin/plugin.json'
        data = json.loads(manifest_path.read_text())
        data['version'] = '1.0.1'
        manifest_path.write_text(json.dumps(data))
        self.assertTrue(any('version mismatch' in error for error in validate_repository(root)))

    def test_root_readme_and_changelog_version_are_checked(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (root / 'README.md').write_text('| wrong | 9.9.9 |\n')
        self.assertTrue(any('root README version' in error for error in validate_repository(root)))
        (root / 'README.md').write_text('| [`yandex-direct`](plugins/yandex-direct/) | 1.0.0 | service | test | No |\n')
        (plugin / 'CHANGELOG.md').write_text('# Changelog\n\n## 0.9.0\n')
        self.assertTrue(any('CHANGELOG version' in error for error in validate_repository(root)))

    def test_missing_skills_target_is_reported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        for path in (plugin / 'skills').rglob('*'):
            if path.is_file():
                path.unlink()
        (plugin / 'skills/router').rmdir()
        (plugin / 'skills').rmdir()
        self.assertTrue(any('skills target' in error for error in validate_repository(root)))

    def test_missing_skill_frontmatter_is_reported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (plugin / 'skills/router/SKILL.md').write_text('# no frontmatter\n')
        self.assertTrue(any('frontmatter' in error for error in validate_repository(root)))

    def test_skill_description_must_start_use_when(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (plugin / 'skills/router/SKILL.md').write_text(
            '---\nname: router\ndescription: Plugin helper.\n---\n'
        )
        self.assertTrue(any('Use when' in error for error in validate_repository(root)))

    def test_folded_frontmatter_description_is_supported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (plugin / 'skills/router/SKILL.md').write_text(
            '---\nname: router\ndescription: >\n  Use when working with\n  this plugin.\n---\n'
        )
        self.assertEqual(validate_repository(root), [])

    def test_runtime_specific_absolute_paths_are_reported_anywhere_in_plugin(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (plugin / 'references/bad.md').write_text('Run ~/.openclaw/workspace/tool.sh\n')
        self.assertTrue(any('runtime-specific absolute path' in error for error in validate_repository(root)))

    def test_credential_like_literal_is_reported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        with (plugin / 'README.md').open('a', encoding='utf-8') as handle:
            handle.write('\nAuthorization: Bearer abcdefghijklmnopqrstuvwxyz123456\n')
        self.assertTrue(any('credential-like secret' in error for error in validate_repository(root)))

    def test_cross_service_transport_is_rejected(self):
        tmp, root, plugin = self.make_repo(plugin_dir='yandex-seo', plugin_name='yandex-seo')
        self.addCleanup(tmp.cleanup)
        (plugin / 'scripts/seo_join.py').write_text('import urllib.request\n')
        self.assertTrue(any('cross-service transport' in error for error in validate_repository(root)))

    def test_evals_require_verifiable_expectations(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        data = json.loads((plugin / 'evals/scenarios.json').read_text())
        data['scenarios'][0].pop('expect')
        (plugin / 'evals/scenarios.json').write_text(json.dumps(data))
        self.assertTrue(any('missing expect' in error for error in validate_repository(root)))

    def test_eval_route_expectation_must_match_skill(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        data = json.loads((plugin / 'evals/scenarios.json').read_text())
        data['scenarios'][0]['expect']['must_route_to'] = 'other-skill'
        (plugin / 'evals/scenarios.json').write_text(json.dumps(data))
        self.assertTrue(any('must_route_to' in error for error in validate_repository(root)))

    def test_capability_matrix_is_required(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (plugin / 'README.md').write_text('# No capability table\nVersion 1.0.0\n')
        self.assertTrue(any('capability matrix' in error for error in validate_repository(root)))

    def test_malformed_evals_are_reported(self):
        tmp, root, plugin = self.make_repo()
        self.addCleanup(tmp.cleanup)
        (plugin / 'evals/scenarios.json').write_text('{bad json')
        self.assertTrue(any('evals/scenarios.json' in error for error in validate_repository(root)))


if __name__ == '__main__':
    unittest.main()
