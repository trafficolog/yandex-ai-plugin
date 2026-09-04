from pathlib import Path
import tempfile
import unittest

import scripts.validate_repo as validator
from test_validate_repo import ValidateRepositoryTests


class ValidatorRobustnessTests(unittest.TestCase):
    def test_invalid_marketplace_source_does_not_pollute_known_plugins(self):
        fixture = ValidateRepositoryTests()
        tmp, root, _ = fixture.make_repo()
        self.addCleanup(tmp.cleanup)

        import json

        marketplace_path = root / ".agents/plugins/marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        marketplace["plugins"][0]["source"]["path"] = "../outside-yandex"
        marketplace_path.write_text(json.dumps(marketplace), encoding="utf-8")

        errors = validator.validate_repository(root)
        self.assertTrue(any("escapes repository root" in error for error in errors), errors)
        self.assertFalse(
            any("plugins/outside-yandex" in error and "bilingual" in error for error in errors),
            errors,
        )

    def test_orphan_plugin_directory_is_reported(self):
        fixture = ValidateRepositoryTests()
        tmp, root, _ = fixture.make_repo()
        self.addCleanup(tmp.cleanup)
        (root / "plugins/yandex-orphan").mkdir(parents=True)

        errors = validator.validate_repository(root)
        self.assertTrue(
            any("plugin directory absent from marketplace" in error and "yandex-orphan" in error for error in errors),
            errors,
        )

    def test_cross_service_non_utf8_python_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = Path(tmp) / "yandex-seo"
            plugin.mkdir()
            path = plugin / "broken.py"
            path.write_bytes(b"\xff\xfeimport socket\n")

            errors: list[str] = []
            validator._validate_cross_service_transport(plugin, errors)
            self.assertTrue(
                any("unable to scan cross-service Python file" in error for error in errors),
                errors,
            )

    def test_runtime_specific_home_variants_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = Path(tmp) / "yandex-direct"
            plugin.mkdir()
            (plugin / "notes.md").write_text(
                "cache: ~/.agents/cache\nconfig: $HOME/.config/yandex\nalt: ${HOME}/tmp\n",
                encoding="utf-8",
            )

            errors: list[str] = []
            validator._validate_plugin_text(plugin, errors)
            self.assertTrue(any("~/.agents/" in error for error in errors), errors)
            self.assertTrue(any("$HOME/" in error for error in errors), errors)
            self.assertTrue(any("${HOME}/" in error for error in errors), errors)

    def test_frontmatter_accepts_bom_crlf_and_terminal_delimiter(self):
        text = (
            "\ufeff---\r\n"
            "name: router\r\n"
            "description: Use when working with a repository plugin.\r\n"
            "---"
        )
        fm = validator._frontmatter(text)
        self.assertIsNotNone(fm)
        self.assertEqual(fm["name"], "router")
        self.assertEqual(fm["description"], "Use when working with a repository plugin.")


if __name__ == "__main__":
    unittest.main()
