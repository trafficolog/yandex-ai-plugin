import importlib.util
import io
from pathlib import Path
import sys
import unittest
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
SERVICES = {
    "direct": ROOT / "plugins/yandex-direct/scripts/_http.py",
    "metrika": ROOT / "plugins/yandex-metrika/scripts/_http.py",
    "webmaster": ROOT / "plugins/yandex-webmaster/scripts/_http.py",
    "wordstat": ROOT / "plugins/yandex-wordstat/scripts/_http.py",
    "search": ROOT / "plugins/yandex-search/scripts/_http.py",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(f"http_contract_{name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULES = {name: load_module(name, path) for name, path in SERVICES.items()}


class RecordingBody(io.BytesIO):
    def __init__(self, payload: bytes):
        super().__init__(payload)
        self.read_sizes: list[int] = []

    def read(self, size: int = -1) -> bytes:
        self.read_sizes.append(size)
        return super().read(size)


class RaisingOpener:
    def __init__(self, exc: Exception):
        self.exc = exc
        self.calls = 0

    def __call__(self, request, *, timeout):
        self.calls += 1
        raise self.exc


class FakeResponse:
    status = 200
    headers = {}

    def __init__(self, raw: bytes = b"{}"):
        self.raw = raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.raw

    def getcode(self):
        return self.status


class RecordingOpener:
    def __init__(self):
        self.calls: list[int] = []

    def __call__(self, request, *, timeout):
        self.calls.append(timeout)
        return FakeResponse()


class ServiceLocalHTTPContractTests(unittest.TestCase):
    def test_authorization_redaction_preserves_scheme(self):
        cases = [
            ("direct", "Bearer secret", "Bearer ***"),
            ("metrika", "OAuth secret", "OAuth ***"),
            ("webmaster", "OAuth secret", "OAuth ***"),
            ("wordstat", "Api-Key secret", "Api-Key ***"),
            ("search", "Bearer secret", "Bearer ***"),
        ]
        for service, value, expected in cases:
            with self.subTest(service=service):
                result = MODULES[service].redact_headers({"Authorization": value})
                self.assertEqual(result["Authorization"], expected)
                self.assertNotIn("secret", result["Authorization"])

    def _invoke_error(self, service: str, opener):
        module = MODULES[service]
        if service == "direct":
            return module.request_json("https://example.invalid", {"Authorization": "Bearer x"}, {"method": "get", "params": {}}, opener=opener)
        if service in {"metrika", "webmaster"}:
            return module.request_json("GET", "https://example.invalid", "token", opener=opener)
        return module.request_json("GET", "https://example.invalid", {"Authorization": "Api-Key x"}, opener=opener)

    def test_http_error_body_reads_are_bounded_to_4096(self):
        for service in MODULES:
            with self.subTest(service=service):
                body = RecordingBody(b"x" * 5000)
                exc = HTTPError("https://example.invalid", 500, "boom", {}, body)
                with self.assertRaises(Exception):
                    self._invoke_error(service, RaisingOpener(exc))
                self.assertTrue(body.read_sizes, service)
                self.assertTrue(all(0 <= size <= 4096 for size in body.read_sizes), body.read_sizes)

    def test_injected_openers_receive_explicit_timeout(self):
        for service in MODULES:
            with self.subTest(service=service):
                opener = RecordingOpener()
                module = MODULES[service]
                if service == "direct":
                    module.request_json("https://example.invalid", {"Authorization": "Bearer x"}, {"method": "get", "params": {}}, timeout=13, opener=opener)
                elif service in {"metrika", "webmaster"}:
                    module.request_json("GET", "https://example.invalid", "token", timeout=13, opener=opener)
                else:
                    module.request_json("GET", "https://example.invalid", {"Authorization": "Api-Key x"}, timeout=13, opener=opener)
                self.assertEqual(opener.calls, [13])

    def test_direct_post_transport_does_not_auto_retry(self):
        direct = MODULES["direct"]
        body = RecordingBody(b"failure")
        exc = HTTPError("https://example.invalid", 500, "boom", {}, body)
        opener = RaisingOpener(exc)
        with self.assertRaises(Exception):
            direct.request_json(
                "https://example.invalid",
                {"Authorization": "Bearer x"},
                {"method": "update", "params": {"Campaigns": [{"Id": 1}]}},
                opener=opener,
            )
        self.assertEqual(opener.calls, 1)


if __name__ == "__main__":
    unittest.main()
