import io
import unittest
from urllib.error import HTTPError

from scripts._http import DirectHTTPError, redact_headers, request_json


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


class DirectHTTPTests(unittest.TestCase):
    def test_http_error_body_read_is_bounded_to_4096_bytes(self):
        body = RecordingBody(b"A" * 4096 + b"TAIL-SENTINEL")
        exc = HTTPError("https://example.invalid", 500, "boom", {}, body)
        opener = RaisingOpener(exc)

        with self.assertRaises(DirectHTTPError) as caught:
            request_json(
                "https://example.invalid",
                {"Authorization": "Bearer secret"},
                {"method": "get", "params": {}},
                opener=opener,
            )

        self.assertEqual(opener.calls, 1)
        self.assertEqual(body.read_sizes, [4096])
        self.assertNotIn("TAIL-SENTINEL", str(caught.exception))

    def test_http_error_invalid_utf8_uses_replacement_decoding(self):
        body = RecordingBody(b"prefix-\xff-suffix")
        exc = HTTPError("https://example.invalid", 400, "bad", {}, body)

        with self.assertRaises(DirectHTTPError) as caught:
            request_json(
                "https://example.invalid",
                {"Authorization": "Bearer secret"},
                {"method": "get", "params": {}},
                opener=RaisingOpener(exc),
            )

        self.assertIn("prefix-�-suffix", str(caught.exception))

    def test_redact_headers_preserves_authorization_scheme(self):
        redacted = redact_headers(
            {
                "Authorization": "Bearer super-secret-token",
                "Client-Login": "client-login",
            }
        )
        self.assertEqual(redacted["Authorization"], "Bearer ***")
        self.assertEqual(redacted["Client-Login"], "client-login")
        self.assertNotIn("super-secret-token", str(redacted))


if __name__ == "__main__":
    unittest.main()
