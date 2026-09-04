import io
import json
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


class FailingErrorBody:
    def __init__(self, exc: OSError):
        self.exc = exc
        self.read_sizes: list[int] = []
        self.closed = False

    def read(self, size: int = -1) -> bytes:
        self.read_sizes.append(size)
        raise self.exc

    def close(self) -> None:
        self.closed = True


class RaisingOpener:
    def __init__(self, exc: Exception):
        self.exc = exc
        self.calls = 0

    def __call__(self, request, *, timeout):
        self.calls += 1
        raise self.exc


class FakeResponse:
    def __init__(self, payload: dict, headers: dict[str, str]):
        self._raw = json.dumps(payload).encode("utf-8")
        self.headers = headers

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._raw


class FailingReadResponse:
    def __init__(self, exc: OSError):
        self.exc = exc
        self.headers: dict[str, str] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
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

    def test_http_error_response_is_closed_after_bounded_read(self):
        body = RecordingBody(b"A" * 4096 + b"TAIL-SENTINEL")
        exc = HTTPError("https://example.invalid", 500, "boom", {}, body)

        with self.assertRaises(DirectHTTPError):
            request_json(
                "https://example.invalid",
                {"Authorization": "Bearer secret"},
                {"method": "get", "params": {}},
                opener=RaisingOpener(exc),
            )

        self.assertTrue(body.closed)

    def test_http_error_body_read_os_errors_are_network_failures_and_close_response(self):
        for read_exc in [TimeoutError("error body timed out"), ConnectionResetError("error body reset")]:
            with self.subTest(exc=type(read_exc).__name__):
                body = FailingErrorBody(read_exc)
                exc = HTTPError("https://example.invalid", 503, "unavailable", {}, body)

                with self.assertRaises(DirectHTTPError) as caught:
                    request_json(
                        "https://example.invalid",
                        {"Authorization": "Bearer secret"},
                        {"method": "get", "params": {}},
                        opener=RaisingOpener(exc),
                    )

                self.assertEqual(body.read_sizes, [4096])
                self.assertTrue(body.closed)
                self.assertEqual(caught.exception.error_type, "network")
                self.assertIn(str(read_exc), str(caught.exception))

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

    def test_response_read_os_errors_are_network_failures(self):
        for exc in [TimeoutError("read timed out"), ConnectionResetError("connection reset")]:
            with self.subTest(exc=type(exc).__name__):
                response = FailingReadResponse(exc)
                with self.assertRaises(DirectHTTPError) as caught:
                    request_json(
                        "https://example.invalid",
                        {"Authorization": "Bearer secret"},
                        {"method": "get", "params": {}},
                        opener=lambda request, timeout, response=response: response,
                    )
                self.assertEqual(caught.exception.error_type, "network")
                self.assertIn(str(exc), str(caught.exception))

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

    def test_response_payload_and_transport_metadata_are_separate(self):
        api_payload = {"result": {"Campaigns": [{"Id": 123}]}}
        response = FakeResponse(
            api_payload,
            {
                "RequestId": "req-123",
                "Units": "10/999/1000",
                "Units-Used-Login": "7",
                "Authorization": "must-not-leak",
                "X-Other": "ignored",
            },
        )

        payload, transport = request_json(
            "https://example.invalid",
            {"Authorization": "Bearer secret"},
            {"method": "get", "params": {}},
            opener=lambda request, timeout: response,
        )

        self.assertEqual(payload, api_payload)
        self.assertEqual(
            transport,
            {
                "request_id": "req-123",
                "units": "10/999/1000",
                "units_used_login": "7",
            },
        )

    def test_absent_transport_headers_are_omitted(self):
        response = FakeResponse({"result": {}}, {"X-Other": "ignored"})
        _payload, transport = request_json(
            "https://example.invalid",
            {"Authorization": "Bearer secret"},
            {"method": "get", "params": {}},
            opener=lambda request, timeout: response,
        )
        self.assertEqual(transport, {})


if __name__ == "__main__":
    unittest.main()
