from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SecurityPolicyContactTests(unittest.TestCase):
    def test_security_policy_does_not_invent_email_or_response_sla(self):
        for relative in ("SECURITY.md", "SECURITY.en.md"):
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            text = path.read_text(encoding="utf-8")
            with self.subTest(relative=relative):
                self.assertIsNone(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text))
                self.assertNotRegex(text.lower(), r"respond within|response within|ответим в течение|sla")


if __name__ == "__main__":
    unittest.main()
