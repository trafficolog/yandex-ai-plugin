import io
import unittest
from urllib.error import HTTPError

from scripts._http import WebmasterAPIError, request_json


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


class WebmasterHTTPTests(unittest.TestCase):
    def test_http_error_body_is_bounded_and_response_is_closed(self):
        body = RecordingBody(b"A" * 4096 + b"TAIL-SENTINEL")
        exc = HTTPError("https://example.invalid", 500, "boom", {}, body)
        opener = RaisingOpener(exc)

        with self.assertRaises(WebmasterAPIError):
            request_json(
                "GET",
                "https://example.invalid",
                "token",
                opener=opener,
            )

        self.assertEqual(opener.calls, 1)
        self.assertEqual(body.read_sizes, [4096])
        self.assertTrue(body.closed)


if __name__ == "__main__":
    unittest.main()
