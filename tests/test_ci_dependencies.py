from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CIDependencyTests(unittest.TestCase):
    def test_shared_changes_include_ci_and_approved_specs(self):
        content = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('\\.github/workflows/ci\\.yml$', content)
        self.assertIn('docs/superpowers/specs/', content)

    def test_service_changes_trigger_seo_regressions(self):
        content = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        seo_line = next(line for line in content.splitlines() if 'echo "seo=true"' in line)
        prefix = content[:content.index(seo_line)]
        condition = prefix.rsplit('if ', 1)[-1]
        for service in ('yandex-wordstat', 'yandex-search', 'yandex-webmaster', 'yandex-metrika'):
            self.assertIn(f'plugins/{service}/', condition)

    def test_service_changes_trigger_marketing_regressions(self):
        content = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        marketing_line = next(line for line in content.splitlines() if 'echo "marketing=true"' in line)
        prefix = content[:content.index(marketing_line)]
        condition = prefix.rsplit('if ', 1)[-1]
        for service in ('yandex-direct', 'yandex-metrika', 'yandex-wordstat', 'yandex-search'):
            self.assertIn(f'plugins/{service}/', condition)


if __name__ == '__main__':
    unittest.main()
