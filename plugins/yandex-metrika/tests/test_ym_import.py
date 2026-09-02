from pathlib import Path
import tempfile
import unittest

from scripts.ym_import import (
    IMPORT_PATHS,
    build_multipart_file,
    guard_expense_source,
    inspect_csv,
    prepare_import,
)


class TestMetrikaImport(unittest.TestCase):
    def _csv(self, directory: str, content: str = "ClientId,Target,DateTime\n1,lead,1710000000\n") -> Path:
        path = Path(directory) / "data.csv"
        path.write_text(content, encoding="utf-8")
        return path

    def test_import_paths(self):
        self.assertEqual(IMPORT_PATHS["offline-conversions"], "offline_conversions/upload")
        self.assertEqual(IMPORT_PATHS["calls"], "offline_conversions/upload_calls")
        self.assertEqual(IMPORT_PATHS["expenses"], "expense/upload")

    def test_inspect_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._csv(tmp)
            info = inspect_csv(path)
            self.assertEqual(info["rows"], 1)
            self.assertEqual(info["columns"], ["ClientId", "Target", "DateTime"])
            self.assertEqual(info["encoding"], "utf-8")
            self.assertGreater(info["size_bytes"], 0)

    def test_non_utf8_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_bytes(b"name\n\xff\n")
            with self.assertRaises(ValueError):
                inspect_csv(path)

    def test_direct_expense_source_aliases_are_rejected(self):
        aliases = [
            "Yandex Direct",
            "Яндекс Директ",
            "direct",
            "Директ",
            "yandex-direct",
            "yandexdirect",
            "ЯндексДирект",
            "direct_yandex",
            "ya.direct",
        ]
        for source in aliases:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    guard_expense_source(source)

    def test_direct_like_utm_expense_csv_requires_explicit_override(self):
        content = "Date,UTMSource,UTMMedium,Expenses\n2026-08-01,yandex,cpc,100\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = self._csv(tmp, content)
            with self.assertRaisesRegex(ValueError, "DIRECT_DUPLICATION_RISK"):
                prepare_import("expenses", 123, path, "secret", source="agency")

            preview = prepare_import(
                "expenses",
                123,
                path,
                "secret",
                source="agency",
                allow_direct_risk=True,
            )
            self.assertIn("DIRECT_DUPLICATION_RISK", preview["warnings"])

    def test_non_direct_expense_csv_is_not_flagged(self):
        content = "Date,UTMSource,UTMMedium,Expenses\n2026-08-01,newsletter,email,100\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = self._csv(tmp, content)
            preview = prepare_import("expenses", 123, path, "secret", source="agency")
            self.assertEqual(preview.get("warnings"), [])

    def test_preview_redacts_token_and_keeps_file_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._csv(tmp)
            preview = prepare_import("offline-conversions", 123, path, "secret", comment="batch")
            self.assertEqual(preview["headers"]["Authorization"], "OAuth ***")
            self.assertEqual(preview["file"]["rows"], 1)
            self.assertNotIn("1,lead", str(preview))
            self.assertIn("comment=batch", preview["url"])

    def test_multipart_builder_contains_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._csv(tmp)
            content_type, body = build_multipart_file(path, boundary="TESTBOUNDARY")
            self.assertEqual(content_type, "multipart/form-data; boundary=TESTBOUNDARY")
            self.assertIn(b'filename="data.csv"', body)
            self.assertIn(b"ClientId,Target,DateTime", body)


if __name__ == "__main__":
    unittest.main()
