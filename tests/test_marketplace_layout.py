import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "yandex-direct"

class MarketplaceLayoutTests(unittest.TestCase):
    def test_root_marketplace_points_to_direct_plugin(self):
        data=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text()); direct=next(item for item in data['plugins'] if item['name']=='yandex-direct-suite'); self.assertEqual(direct['source'],{'source':'local','path':'./plugins/yandex-direct'})
    def test_direct_plugin_preserves_version(self):
        data=json.loads((PLUGIN/'.codex-plugin/plugin.json').read_text()); self.assertEqual(data['version'],'1.0.0'); self.assertEqual(data['skills'],'./skills/')
    def test_direct_router_and_specialized_skills_moved(self):
        expected={'yandex-direct','yandex-direct-api','yandex-direct-audit','yandex-direct-budget','yandex-direct-create','yandex-direct-keywords','yandex-direct-optimize','yandex-direct-reporting'}; self.assertEqual({path.parent.name for path in (PLUGIN/'skills').glob('*/SKILL.md')},expected)
    def test_obsolete_root_direct_plugin_manifest_is_absent(self): self.assertFalse((ROOT/'.codex-plugin/plugin.json').exists()); self.assertFalse((ROOT/'.claude-plugin/plugin.json').exists())
    def test_direct_plugin_has_required_reference_directories(self):
        for path in ['references','scripts','tests','evals']: self.assertTrue((PLUGIN/path).is_dir(),path)
    def test_repository_foundation_docs_exist(self):
        for path in ['docs/PLUGIN_STANDARD.md','docs/SERVICE_MATRIX.md','docs/ROADMAP.md','packages/README.md','workflows/README.md']: self.assertTrue((ROOT/path).is_file(),path)
    def test_plugin_standard_contains_safety_contract(self): self.assertIn('read → analyze → preview → explicit approval → write → verify',(ROOT/'docs/PLUGIN_STANDARD.md').read_text(encoding='utf-8'))
    def test_path_aware_ci_is_present(self):
        content=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8'); self.assertIn('scripts/validate_repo.py',content); self.assertIn('plugins/yandex-direct',content)
    def test_marketplace_exposes_all_tier1_plugins(self):
        data=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text(encoding='utf-8')); paths={item['source']['path'] for item in data['plugins']}; self.assertEqual(paths,{'./plugins/yandex-direct','./plugins/yandex-metrika','./plugins/yandex-webmaster','./plugins/yandex-wordstat','./plugins/yandex-search'})
    def test_ci_has_metrika_plugin_job(self):
        c=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8'); self.assertIn('metrika:',c); self.assertIn('plugins/yandex-metrika',c)
    def test_ci_has_webmaster_plugin_job(self):
        c=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8'); self.assertIn('webmaster:',c); self.assertIn('plugins/yandex-webmaster',c); self.assertIn('steps.detect.outputs.webmaster',c)
    def test_service_matrix_marks_webmaster_available(self): self.assertIn('| Yandex Webmaster | 1 | **available** | 1.0.0 |',(ROOT/'docs/SERVICE_MATRIX.md').read_text(encoding='utf-8'))
    def test_ci_has_wordstat_plugin_job(self):
        c=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8'); self.assertIn('wordstat:',c); self.assertIn('plugins/yandex-wordstat',c); self.assertIn('steps.detect.outputs.wordstat',c)
    def test_service_matrix_marks_wordstat_available(self): self.assertIn('| Yandex Wordstat | 1 | **available** | 1.0.0 |',(ROOT/'docs/SERVICE_MATRIX.md').read_text(encoding='utf-8'))
    def test_roadmap_marks_phase4_implemented_and_phase5_search_next(self):
        c=(ROOT/'docs/ROADMAP.md').read_text(encoding='utf-8'); self.assertIn('## Phase 4 — Yandex Wordstat',c); self.assertIn('Implemented as plugin `1.0.0`',c); self.assertIn('## Phase 5 — Yandex Search',c)
    def test_ci_has_search_plugin_job(self):
        c=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8'); self.assertIn('search:',c); self.assertIn('plugins/yandex-search',c); self.assertIn('steps.detect.outputs.search',c)
    def test_service_matrix_marks_search_available(self): self.assertIn('| Yandex Search | 1 | **available** | 1.0.0 |',(ROOT/'docs/SERVICE_MATRIX.md').read_text(encoding='utf-8'))
    def test_roadmap_marks_phase5_implemented_and_phase6_next(self):
        c=(ROOT/'docs/ROADMAP.md').read_text(encoding='utf-8'); self.assertIn('## Phase 5 — Yandex Search',c); self.assertIn('## Phase 6 — Cross-service workflows',c); self.assertIn('Implemented as plugin `1.0.0`',c)

if __name__ == '__main__': unittest.main()
