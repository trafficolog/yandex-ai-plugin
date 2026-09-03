from pathlib import Path
import tempfile
import unittest

from scripts.validate_repo import _validate_cross_service_transport


class CrossServiceTransportValidationTests(unittest.TestCase):
    def validate_script(self, source: str, *, plugin_name: str = "yandex-seo") -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = Path(tmp) / plugin_name
            scripts = plugin / "scripts"
            scripts.mkdir(parents=True)
            (scripts / "helper.py").write_text(source, encoding="utf-8")
            errors: list[str] = []
            _validate_cross_service_transport(plugin, errors)
            return errors

    def assert_transport_rejected(self, source: str) -> None:
        errors = self.validate_script(source)
        self.assertTrue(any("cross-service transport" in error for error in errors), errors)

    def test_forbidden_transport_import_variants_are_rejected(self):
        variants = [
            "import urllib.request as ur\nur.urlopen('https://example.com')\n",
            "from urllib import request as req\nreq.urlopen('https://example.com')\n",
            "from urllib.request import urlopen as open_url\nopen_url('https://example.com')\n",
            "import requests as r\nr.get('https://example.com')\n",
            "from httpx import Client as C\nclient = C()\n",
            "import aiohttp as ah\nsession = ah.ClientSession\n",
        ]
        for source in variants:
            with self.subTest(source=source.splitlines()[0]):
                self.assert_transport_rejected(source)

    def test_transport_words_in_strings_and_comments_are_not_imports(self):
        source = (
            'DOC = "example only: import requests as r"\n'
            '# from httpx import Client\n'
            'NOTE = "from urllib.request import urlopen as open_url"\n'
        )
        self.assertEqual(self.validate_script(source), [])

    def test_urllib_parse_is_allowed(self):
        self.assertEqual(
            self.validate_script("from urllib.parse import urlencode\nVALUE = urlencode({'q': 'test'})\n"),
            [],
        )

    def test_non_cross_service_plugins_are_not_scanned_by_this_boundary(self):
        self.assertEqual(
            self.validate_script("import requests\n", plugin_name="yandex-direct"),
            [],
        )


if __name__ == "__main__":
    unittest.main()
