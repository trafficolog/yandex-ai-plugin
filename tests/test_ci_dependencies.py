from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def changed_files_condition(content: str, output_name: str) -> str:
    lines = content.splitlines()
    marker = f'echo "{output_name}=true"'
    for index, line in enumerate(lines):
        if marker in line and index > 0 and 'changed_files' in lines[index - 1]:
            return lines[index - 1]
    raise AssertionError(f'No changed_files condition found for {output_name}')


class CIDependencyTests(unittest.TestCase):
    def test_shared_changes_include_ci_and_approved_specs(self):
        content = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('\\.github/workflows/ci\\.yml$', content)
        self.assertIn('docs/superpowers/specs/', content)

    def test_service_changes_trigger_seo_regressions(self):
        content = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        condition = changed_files_condition(content, 'seo')
        for service in ('yandex-wordstat', 'yandex-search', 'yandex-webmaster', 'yandex-metrika'):
            self.assertIn(f'plugins/{service}/', condition)

    def test_service_changes_trigger_marketing_regressions(self):
        content = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        condition = changed_files_condition(content, 'marketing')
        for service in ('yandex-direct', 'yandex-metrika', 'yandex-wordstat', 'yandex-search'):
            self.assertIn(f'plugins/{service}/', condition)


if __name__ == '__main__':
    unittest.main()
