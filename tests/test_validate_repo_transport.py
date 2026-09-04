from pathlib import Path
import tempfile
import unittest

from scripts.validate_repo import _validate_cross_service_transport


class CrossServiceTransportValidationTests(unittest.TestCase):
    def validate_relative_path(
        self,
        source: str,
        *,
        relative_path: str = "scripts/helper.py",
        plugin_name: str = "yandex-seo",
    ) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            plugin = Path(tmp) / plugin_name
            target = plugin / relative_path
            target.parent.mkdir(parents=True)
            target.write_text(source, encoding="utf-8")
            errors: list[str] = []
            _validate_cross_service_transport(plugin, errors)
            return errors

    def validate_script(self, source: str, *, plugin_name: str = "yandex-seo") -> list[str]:
        return self.validate_relative_path(source, plugin_name=plugin_name)

    def assert_transport_rejected(self, source: str, *, relative_path: str = "scripts/helper.py") -> None:
        errors = self.validate_relative_path(source, relative_path=relative_path)
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

    def test_forbidden_stdlib_and_dynamic_transport_roots_are_rejected(self):
        variants = [
            "import http.client\n",
            "import socket\n",
            "import ssl\n",
            "import urllib3\n",
            "import pycurl\n",
            "import importlib\nimportlib.import_module('urllib.request')\n",
            "import subprocess\nsubprocess.run(['curl', 'https://example.com'])\n",
        ]
        for source in variants:
            with self.subTest(source=source.splitlines()[0]):
                self.assert_transport_rejected(source)

    def test_builtin_dynamic_import_of_transport_module_is_rejected(self):
        variants = [
            "client = __import__('urllib.request', fromlist=['urlopen'])\nclient.urlopen('https://example.com')\n",
            "requests = __import__('requests')\nrequests.get('https://example.com')\n",
        ]
        for source in variants:
            with self.subTest(source=source.splitlines()[0]):
                self.assert_transport_rejected(source)

    def test_builtin_dynamic_import_of_non_transport_module_is_allowed(self):
        self.assertEqual(self.validate_script("json = __import__('json')\n"), [])

    def test_cross_service_transport_is_scanned_outside_scripts(self):
        self.assert_transport_rejected(
            "from urllib.request import urlopen\n",
            relative_path="skills/yandex-seo/transport_helper.py",
        )

    def test_real_yandex_service_hosts_are_rejected(self):
        hosts = [
            "https://api.direct.yandex.com",
            "https://api.webmaster.yandex.net",
            "https://api.wordstat.yandex.net",
            "https://oauth.yandex.ru",
            "https://searchapi.api.cloud.yandex.net",
        ]
        for host in hosts:
            with self.subTest(host=host):
                self.assert_transport_rejected(f'ENDPOINT = "{host}"\n')

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
