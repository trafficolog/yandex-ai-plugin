from pathlib import Path
import tempfile
import unittest

from scripts.validate_repo import _validate_plugin_text


class SecretLiteralValidationTests(unittest.TestCase):
    def validate_text(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = Path(tmp) / "yandex-direct"
            plugin.mkdir(parents=True)
            (plugin / "fixture.md").write_text(text, encoding="utf-8")
            errors: list[str] = []
            _validate_plugin_text(plugin, errors)
            return errors

    def assert_secret_rejected(self, literal: str) -> None:
        errors = self.validate_text(f"token = {literal}\n")
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
