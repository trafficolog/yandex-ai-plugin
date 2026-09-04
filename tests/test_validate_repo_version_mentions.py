from pathlib import Path
import json
import tempfile
import unittest

import scripts.validate_repo as validator


class VersionMentionValidationTests(unittest.TestCase):
    def make_docs(self, root: Path, *, version: str = "1.1.2") -> Path:
        plugin = root / "plugins/yandex-seo"
        plugin.mkdir(parents=True)
        (root / "docs").mkdir(parents=True)
        root_table = f"| [`yandex-seo`](plugins/yandex-seo/) | {version} | cross-service | SEO | no |\n"
        root_versions = f"## Versions\n\n```text\nyandex-seo           {version}\n```\n"
        for filename in ("README.md", "README.en.md"):
            (root / filename).write_text(root_table + "\n" + root_versions, encoding="utf-8")
        (plugin / "README.md").write_text(f"Версия `{version}`.\n", encoding="utf-8")
        (plugin / "README.en.md").write_text(f"Version `{version}`.\n", encoding="utf-8")
        for filename in ("CHANGELOG.md", "CHANGELOG.en.md"):
            (plugin / filename).write_text(f"## [{version}] — 2026-09-04\n", encoding="utf-8")
        matrix = (
            "| Service plugin | Tier | Status | Version | Scope | Source |\n"
            "|---|---:|---|---|---|---|\n"
            f"| Yandex SEO | X | **available** | {version} | SEO | pure-data |\n"
        )
        (root / "docs/SERVICE_MATRIX.md").write_text(matrix, encoding="utf-8")
        (root / "docs/SERVICE_MATRIX.en.md").write_text(matrix, encoding="utf-8")
        return plugin

    def validate(self, root: Path, plugin: Path, version: str = "1.1.2") -> list[str]:
        errors: list[str] = []
        validator._validate_plugin_version_mentions(root, plugin, version, errors)
        return errors

    def test_each_canonical_version_location_rejects_stale_value(self):
        cases = (
            ("plugin README RU", "plugins/yandex-seo/README.md", "Версия `1.1.1`.\n"),
            ("plugin README EN", "plugins/yandex-seo/README.en.md", "Version `1.1.1`.\n"),
            ("plugin changelog RU", "plugins/yandex-seo/CHANGELOG.md", "## [1.1.1] — 2026-09-04\n"),
            ("plugin changelog EN", "plugins/yandex-seo/CHANGELOG.en.md", "## [1.1.1] — 2026-09-04\n"),
            (
                "root README RU",
                "README.md",
                "| [`yandex-seo`](plugins/yandex-seo/) | 1.1.1 | cross-service | SEO | no |\n\n"
                "## Versions\n\n```text\nyandex-seo           1.1.1\n```\n",
            ),
            (
                "root README EN",
                "README.en.md",
                "| [`yandex-seo`](plugins/yandex-seo/) | 1.1.1 | cross-service | SEO | no |\n\n"
                "## Versions\n\n```text\nyandex-seo           1.1.1\n```\n",
            ),
            (
                "service matrix RU",
                "docs/SERVICE_MATRIX.md",
                "| Service plugin | Tier | Status | Version | Scope | Source |\n"
                "|---|---:|---|---|---|---|\n"
                "| Yandex SEO | X | **available** | 1.1.1 | SEO | pure-data |\n",
            ),
            (
                "service matrix EN",
                "docs/SERVICE_MATRIX.en.md",
                "| Service plugin | Tier | Status | Version | Scope | Source |\n"
                "|---|---:|---|---|---|---|\n"
                "| Yandex SEO | X | **available** | 1.1.1 | SEO | pure-data |\n",
            ),
        )
        for label, relative, stale in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                plugin = self.make_docs(root)
                (root / relative).write_text(stale, encoding="utf-8")
                errors = self.validate(root, plugin)
                self.assertTrue(any("version mention" in error for error in errors), errors)

    def test_current_seo_readmes_match_manifest_version(self):
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads(
            (root / "plugins/yandex-seo/.codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        version = manifest["version"]
        for filename, label in (("README.md", "Версия"), ("README.en.md", "Version")):
            with self.subTest(filename=filename):
                text = (root / "plugins/yandex-seo" / filename).read_text(encoding="utf-8")
                self.assertIn(f"{label} `{version}`", text)


if __name__ == "__main__":
    unittest.main()
