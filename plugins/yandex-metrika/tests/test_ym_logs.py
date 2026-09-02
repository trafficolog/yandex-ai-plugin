from datetime import date
import io
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from scripts import ym_logs
from scripts.ym_logs import download_part, logs_endpoint, prepare_logs_request, validate_period


class _Response:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return b"a\tb\n1\t2\n"
    def getcode(self): return 200


class TestMetrikaLogs(unittest.TestCase):
    def test_endpoint_lifecycle(self):
        self.assertTrue(logs_endpoint(123, "evaluate").endswith("/counter/123/logrequests/evaluate"))
        self.assertTrue(logs_endpoint(123, "create").endswith("/counter/123/logrequests"))
        self.assertTrue(logs_endpoint(123, "status", request_id=7).endswith("/counter/123/logrequest/7"))
        self.assertTrue(logs_endpoint(123, "download", request_id=7, part_number=2).endswith("/counter/123/logrequest/7/part/2/download"))
        self.assertTrue(logs_endpoint(123, "clean", request_id=7).endswith("/counter/123/logrequest/7/clean"))

    def test_period_must_not_exceed_one_year(self):
        validate_period("2026-01-01", "2027-01-01", today=date(2030, 1, 1))
        with self.assertRaises(ValueError):
            validate_period("2026-01-01", "2027-01-02", today=date(2030, 1, 1))
        with self.assertRaises(ValueError):
            validate_period("2026-02-01", "2026-01-31", today=date(2030, 1, 1))

    def test_current_or_future_date2_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_period("2026-08-01", "2026-09-01", today=date(2026, 9, 1))
        with self.assertRaises(ValueError):
            validate_period("2026-08-01", "2026-09-02", today=date(2026, 9, 1))

    def test_evaluate_cli_preserves_attribution(self):
        captured = {}

        def fake_execute(counter_id, action, *, token, request_id=None, query=None):
            captured["action"] = action
            captured["query"] = query
            return {"ok": True}

        argv = [
            "ym_logs.py", "evaluate", "123",
            "--date1", "2026-08-01", "--date2", "2026-08-02",
            "--fields", "ym:s:visitID", "--source", "visits",
            "--attribution", "automatic",
        ]
        with patch.object(ym_logs.sys, "argv", argv):
            with patch.object(ym_logs, "execute_json_action", side_effect=fake_execute):
                with redirect_stdout(io.StringIO()):
                    rc = ym_logs.main()
        self.assertEqual(rc, 0)
        self.assertEqual(captured["action"], "evaluate")
        self.assertEqual(captured["query"]["attribution"], "automatic")

    def test_clean_preview_redacts_token(self):
        preview = prepare_logs_request(123, "clean", token="secret", request_id=7)
        self.assertEqual(preview["headers"]["Authorization"], "OAuth ***")
        self.assertTrue(preview["consequential"])

    def test_download_part_writes_file(self):
        seen = {}
        def opener(request, timeout=30):
            seen["authorization"] = request.headers.get("Authorization")
            return _Response()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "part.tsv"
            result = download_part(123, 7, 2, "secret", out, opener=opener)
            self.assertEqual(result, out)
            self.assertEqual(out.read_bytes(), b"a\tb\n1\t2\n")
            self.assertEqual(seen["authorization"], "OAuth secret")


if __name__ == "__main__":
    unittest.main()
