import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "yandex-direct"
SERVICE_PLUGINS = {
    "Yandex Direct": "yandex-direct",
    "Yandex Metrika": "yandex-metrika",
    "Yandex Webmaster": "yandex-webmaster",
    "Yandex Wordstat": "yandex-wordstat",
    "Yandex Search": "yandex-search",
    "Yandex SEO": "yandex-seo",
    "Yandex Marketing": "yandex-marketing",
}


def plugin_version(plugin_dir: str) -> str:
    manifest = ROOT / "plugins" / plugin_dir / ".codex-plugin" / "plugin.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return data["version"]


def matrix_version(service: str, content: str) -> str:
    for line in content.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] == service:
            return cells[3]
    raise AssertionError(f"missing service row: {service}")


class MarketplaceLayoutTests(unittest.TestCase):
    def test_service_matrix_versions_match_plugin_manifests(self):
        for matrix_path in ["docs/SERVICE_MATRIX.md", "docs/SERVICE_MATRIX.en.md"]:
            content = (ROOT / matrix_path).read_text(encoding="utf-8")
            for service, plugin_dir in SERVICE_PLUGINS.items():
                with self.subTest(matrix=matrix_path, service=service):
                    self.assertEqual(matrix_version(service, content), plugin_version(plugin_dir))

    def test_root_marketplace_points_to_direct_plugin(self):
        data = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        direct = next(item for item in data["plugins"] if item["name"] == "yandex-direct-suite")
        self.assertEqual(direct["source"], {"source": "local", "path": "./plugins/yandex-direct"})

    def test_direct_plugin_manifest_declares_skills_path(self):
        data = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
        self.assertIn("version", data)
        self.assertEqual(data["skills"], "./skills/")

    def test_direct_router_and_specialized_skills_moved(self):
        expected = {
            "yandex-direct", "yandex-direct-api", "yandex-direct-audit",
            "yandex-direct-budget", "yandex-direct-create", "yandex-direct-keywords",
            "yandex-direct-optimize", "yandex-direct-reporting",
        }
        actual = {path.parent.name for path in (PLUGIN / "skills").glob("*/SKILL.md")}
        self.assertEqual(actual, expected)

    def test_obsolete_root_direct_plugin_manifest_is_absent(self):
        self.assertFalse((ROOT / ".codex-plugin/plugin.json").exists())
        self.assertFalse((ROOT / ".claude-plugin/plugin.json").exists())

    def test_direct_plugin_has_required_reference_directories(self):
        for path in ["references", "scripts", "tests", "evals"]:
            self.assertTrue((PLUGIN / path).is_dir(), path)

    def test_repository_foundation_docs_exist(self):
        for path in [
            "docs/CONTRACT_MATRIX.json", "docs/PLUGIN_STANDARD.md", "docs/SERVICE_MATRIX.md",
            "docs/ROADMAP.md", "packages/README.md", "workflows/README.md",
        ]:
            self.assertTrue((ROOT / path).is_file(), path)

    def test_plugin_standard_contains_safety_contract(self):
        standard = (ROOT / "docs/PLUGIN_STANDARD.md").read_text(encoding="utf-8")
        self.assertIn("read → analyze → preview → explicit approval → write → verify", standard)

    def test_path_aware_ci_is_present(self):
        workflow = ROOT / ".github/workflows/ci.yml"
        self.assertTrue(workflow.is_file())
        content = workflow.read_text(encoding="utf-8")
        self.assertIn("scripts/validate_repo.py", content)
        self.assertIn("plugins/yandex-direct", content)

    def test_marketplace_exposes_all_available_plugins(self):
        data = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        paths = {item["source"]["path"] for item in data["plugins"]}
        self.assertEqual(paths, {
            "./plugins/yandex-direct", "./plugins/yandex-metrika", "./plugins/yandex-webmaster",
            "./plugins/yandex-wordstat", "./plugins/yandex-search", "./plugins/yandex-seo",
            "./plugins/yandex-marketing",
        })

    def test_ci_has_metrika_plugin_job(self):
        content = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("metrika:", content)
        self.assertIn("plugins/yandex-metrika", content)

    def test_ci_has_webmaster_plugin_job(self):
        content = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("webmaster:", content)
        self.assertIn("plugins/yandex-webmaster", content)
        self.assertIn("steps.detect.outputs.webmaster", content)

    def test_ci_has_wordstat_plugin_job(self):
        content = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("wordstat:", content)
        self.assertIn("plugins/yandex-wordstat", content)
        self.assertIn("steps.detect.outputs.wordstat", content)

    def test_roadmap_marks_phase4_implemented_and_phase5_search_next(self):
        content = (ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn("### Phase 4 — Yandex Wordstat", content)
        self.assertIn("Implemented as plugin `1.0.0`", content)
        self.assertIn("### Phase 5 — Yandex Search", content)

    def test_ci_has_search_plugin_job(self):
        content=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('search:',content)
        self.assertIn('plugins/yandex-search',content)
        self.assertIn('steps.detect.outputs.search',content)

    def test_roadmap_marks_phase5_implemented_and_phase6_next(self):
        content=(ROOT/'docs/ROADMAP.md').read_text(encoding='utf-8')
        self.assertIn('### Phase 5 — Yandex Search',content)
        self.assertIn('### Phase 6A — Yandex SEO',content)
        self.assertIn('Implemented as plugin `1.0.0`',content)

    def test_marketplace_exposes_yandex_seo(self):
        data=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
        paths={item['source']['path'] for item in data['plugins']}
        self.assertIn('./plugins/yandex-seo',paths)

    def test_ci_has_seo_plugin_job(self):
        content=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('seo:',content)
        self.assertIn('plugins/yandex-seo',content)
        self.assertIn('steps.detect.outputs.seo',content)

    def test_roadmap_marks_phase6a_and_phase6b(self):
        content=(ROOT/'docs/ROADMAP.md').read_text(encoding='utf-8')
        self.assertIn('### Phase 6A — Yandex SEO',content)
        self.assertIn('Implemented as plugin `1.0.0`',content)
        self.assertIn('### Phase 6B — Yandex Marketing',content)

    def test_roadmap_marks_phase7_shipped(self):
        content=(ROOT/'docs/ROADMAP.md').read_text(encoding='utf-8')
        self.assertIn('### Phase 7 — Topical Architecture', content)
        self.assertIn('Wordstat `1.1.0`', content)
        self.assertIn('SEO `1.1.0`', content)
        self.assertIn('Search `1.0.2`', content)

    def test_marketplace_exposes_yandex_marketing(self):
        data=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
        marketing=next(item for item in data['plugins'] if item['name']=='yandex-marketing')
        self.assertEqual(marketing['source'], {'source':'local','path':'./plugins/yandex-marketing'})
        self.assertEqual(marketing['version'], plugin_version('yandex-marketing'))

    def test_ci_has_marketing_plugin_job(self):
        content=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('marketing:',content)
        self.assertIn('plugins/yandex-marketing',content)
        self.assertIn('steps.detect.outputs.marketing',content)
        self.assertIn('marketing_context.py',content)
        self.assertIn('marketing_prioritize.py',content)

    def test_roadmap_marks_phase6b_implemented(self):
        content=(ROOT/'docs/ROADMAP.md').read_text(encoding='utf-8')
        marker='### Phase 6B — Yandex Marketing'
        self.assertIn(marker,content)
        phase=content.split(marker,1)[1].split('# Future release backlog',1)[0]
        self.assertIn('Implemented as plugin `1.0.0`',phase)
        self.assertIn('no Yandex API clients',phase)

    def test_readme_lists_marketing_plugin_and_regression_command(self):
        content=(ROOT/'README.md').read_text(encoding='utf-8')
        self.assertIn('[`yandex-marketing`](plugins/yandex-marketing/)',content)
        self.assertIn('cd plugins/yandex-marketing',content)
        self.assertIn('marketing_prioritize.py',content)
        self.assertIn(f"yandex-marketing     {plugin_version('yandex-marketing')}", content)

    def test_release_changelog_tracks_phase7_and_prior_releases(self):
        self.assertTrue((ROOT/'CHANGELOG.md').is_file())
        self.assertTrue((ROOT/'docs/REVIEW_FIRST_RELEASE.md').is_file())
        changelog=(ROOT/'CHANGELOG.md').read_text(encoding='utf-8')
        review=(ROOT/'docs/REVIEW_FIRST_RELEASE.md').read_text(encoding='utf-8')
        self.assertIn('## [PHASE 7 1.0.1] — 2026-09-03', changelog)
        self.assertIn('## [PHASE 7 1.0.0] — 2026-09-02', changelog)
        self.assertIn('## [OPUS 1.1.1] — 2026-09-02', changelog)
        self.assertIn('## [OPUS 1.1.0] — 2026-09-02', changelog)
        self.assertIn('## [1.0.0] — 2026-09-02',changelog)
        self.assertIn('First Release Independent Review Guide',review)

    def test_operations_ai_mobile_are_backlog_not_first_release(self):
        roadmap=(ROOT/'docs/ROADMAP.md').read_text(encoding='utf-8')
        matrix=(ROOT/'docs/SERVICE_MATRIX.md').read_text(encoding='utf-8')
        self.assertIn('# Future release backlog',roadmap)
        self.assertNotIn('## Phase 7 — Operations, AI, mobile',roadmap)
        for service in ['Yandex Tracker','Yandex 360','Yandex Maps','AppMetrica','YandexGPT','SpeechKit']:
            self.assertIn(service,roadmap)
        self.assertIn('| Yandex Tracker | 2 | backlog |',matrix)
        self.assertIn('| SpeechKit | 3 | backlog |',matrix)


if __name__ == "__main__":
    unittest.main()
