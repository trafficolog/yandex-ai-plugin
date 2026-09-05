from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class P0ExecutableSafetyContractTests(unittest.TestCase):
    def test_direct_has_local_v2_kernel(self):
        path = ROOT / "plugins/yandex-direct/scripts/_safety.py"
        self.assertTrue(path.is_file(), "Direct must provide a local v2 safety kernel")
        text = path.read_text(encoding="utf-8")
        self.assertIn('APPROVAL_SCHEMA = "yandex-ai-approval/v2"', text)
        self.assertIn("BULK_THRESHOLD = 20", text)


if __name__ == "__main__":
    unittest.main()
