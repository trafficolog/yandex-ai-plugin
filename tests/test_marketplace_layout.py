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
        data = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        direct = next(item for item in data["plugins"] if item["name"] == "yandex-direct-suite")
        self.assertEqual(direct["source"], {"source": "local", "path": "./plugins/yandex-direct"})

    def test_direct_plugin_manifest_declares_skills_path(self):
        data = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertIn("version", data)
        self.assertEqual(data["skills"], "./skills/")

    def test_direct_router_and_specialized_skills_moved(self):
        expected = {
            "yandex-direct",
            "yandex-direct-api",
            "yandex-direct-audit",
            "yandex-direct-budget",
            "yandex-direct-create",
            "yandex-direct-keywords",
            "yandex-direct-optimize",
            "yandex-direct-reporting",
        }
        actual = {path.parent.name for path in (PLUGIN / "skills").glob("*/SKILL.md")}
        self.assertEqual(actual, expected)

    def test_obsolete_root_direct_plugin_manifest_is_absent(self):
        self.assertFalse((ROOT / ".codex-plugin/plugin.json").exists())
        self.assertFalse((ROOT / ".claude-plugin/plugin.json").exists())

    def test_direct_plugin_has_required_reference_directories(self):
        for path in ["references", "scripts", "tests", "evals"]:
            self.assertTrue((PLUGIN / path).is_dir(), path)

    def test_path_aware_ci_is_present(self):
        workflow = ROOT / ".github/workflows/ci.yml"
        self.assertTrue(workflow.is_file())
        content = workflow.read_text(encoding="utf-8")
        self.assertIn("scripts/validate_repo.py", content)
        self.assertIn("plugins/yandex-direct", content)

    def test_marketplace_exposes_all_available_plugins(self):
        data = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        paths = {item["source"]["path"] for item in data["plugins"]}
        self.assertEqual(
            paths,
            {
                "./plugins/yandex-direct",
                "./plugins/yandex-metrika",
                "./plugins/yandex-webmaster",
                "./plugins/yandex-wordstat",
                "./plugins/yandex-search",
                "./plugins/yandex-seo",
                "./plugins/yandex-marketing",
            },
        )

    def test_ci_has_service_plugin_jobs(self):
        content = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        for job, plugin_dir in [
            ("metrika", "yandex-metrika"),
            ("webmaster", "yandex-webmaster"),
            ("wordstat", "yandex-wordstat"),
            ("search", "yandex-search"),
            ("seo", "yandex-seo"),
            ("marketing", "yandex-marketing"),
        ]:
            with self.subTest(job=job):
                self.assertIn(f"{job}:", content)
                self.assertIn(f"plugins/{plugin_dir}", content)
                self.assertIn(f"steps.detect.outputs.{job}", content)

    def test_marketplace_exposes_yandex_seo(self):
        data = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        paths = {item["source"]["path"] for item in data["plugins"]}
        self.assertIn("./plugins/yandex-seo", paths)

    def test_marketplace_exposes_yandex_marketing_with_manifest_version(self):
        data = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        marketing = next(item for item in data["plugins"] if item["name"] == "yandex-marketing")
        self.assertEqual(marketing["source"], {"source": "local", "path": "./plugins/yandex-marketing"})
        self.assertEqual(marketing["version"], plugin_version("yandex-marketing"))

    def test_marketing_ci_covers_entry_and_terminal_helpers(self):
        content = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("marketing_context.py", content)
        self.assertIn("marketing_prioritize.py", content)

    def test_readme_lists_marketing_plugin_and_regression_command(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("[`yandex-marketing`](plugins/yandex-marketing/)", content)
        self.assertIn("cd plugins/yandex-marketing", content)
        self.assertIn("marketing_prioritize.py", content)
        self.assertIn(f"yandex-marketing     {plugin_version('yandex-marketing')}", content)


if __name__ == "__main__":
    unittest.main()
