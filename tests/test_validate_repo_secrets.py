from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts import validate_repo
from scripts.validate_repo import _validate_plugin_text


class SecretLiteralValidationTests(unittest.TestCase):
    def validate_file(self, filename: str, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = Path(tmp) / "yandex-direct"
            plugin.mkdir(parents=True)
            target = plugin / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            errors: list[str] = []
            _validate_plugin_text(plugin, errors)
            return errors

    def validate_text(self, text: str) -> list[str]:
        return self.validate_file("fixture.md", text)

    def assert_secret_rejected(self, literal: str, *, filename: str = "fixture.md") -> None:
        errors = self.validate_file(filename, f"token = {literal}\n")
        self.assertTrue(any("credential-like secret" in error for error in errors), errors)

    def test_yandex_credential_prefixes_with_realistic_payloads_are_rejected(self):
        literals = [
            "y0_AgAAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
            "AQAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
            "t1.AgAAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        ]
        for literal in literals:
            with self.subTest(prefix=literal[:4]):
                self.assert_secret_rejected(literal)

    def test_committed_dotenv_files_are_scanned_for_realistic_secrets(self):
        for filename, literal in [
            (".env", "y0_AgAAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"),
            (".env.production", "AQAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"),
            ("config/.env.local", "t1.AgAAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"),
        ]:
            with self.subTest(filename=filename):
                self.assert_secret_rejected(literal, filename=filename)

    def test_ignored_local_dotenv_is_not_scanned_but_tracked_dotenv_is(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins/yandex-direct"
            plugin.mkdir(parents=True)
            ignored = plugin / ".env"
            tracked = plugin / ".env.production"
            ignored.write_text(
                "YANDEX_DIRECT_TOKEN=y0_AgAAAACCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC\n",
                encoding="utf-8",
            )
            tracked.write_text(
                "YANDEX_DIRECT_TOKEN=y0_AgAAAADDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD\n",
                encoding="utf-8",
            )
            (root / ".gitignore").write_text("plugins/yandex-direct/.env\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                ["git", "add", ".gitignore", "plugins/yandex-direct/.env.production"],
                cwd=root,
                check=True,
            )

            errors: list[str] = []
            _validate_plugin_text(plugin, errors)

            tracked_error = f"credential-like secret found in plugin file: {tracked}"
            ignored_error = f"credential-like secret found in plugin file: {ignored}"
            self.assertIn(tracked_error, errors)
            self.assertNotIn(ignored_error, errors)

    def test_tracked_repository_dotenv_outside_plugins_is_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "plugins/yandex-direct").mkdir(parents=True)
            target = root / ".env.production"
            target.write_text(
                "YANDEX_DIRECT_TOKEN=y0_AgAAAAEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", ".env.production"], cwd=root, check=True)

            errors: list[str] = []
            validate_repo._validate_repository_dotenv(root, errors)

            self.assertIn(
                f"credential-like secret found in repository dotenv file: {target.resolve()}",
                errors,
            )

    def test_dotenv_example_placeholder_is_allowed(self):
        placeholder = (
            "YANDEX_DIRECT_TOKEN=y0_demo\n"
            "YANDEX_API_KEY=AQAA-short\n"
            "YANDEX_SESSION=t1.sample\n"
        )
        self.assertEqual(self.validate_file(".env.example", placeholder), [])

    def test_short_prefix_examples_in_prose_are_allowed(self):
        prose = (
            "Document token families as y0_, AQAA, and t1. without embedding credentials.\n"
            "Examples may mention y0_demo, AQAA-short, or t1.sample as placeholders.\n"
        )
        self.assertEqual(self.validate_text(prose), [])

    def test_existing_authorization_header_detection_remains_active(self):
        self.assert_secret_rejected("Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456")


if __name__ == "__main__":
    unittest.main()
