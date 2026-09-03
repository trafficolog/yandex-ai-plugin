import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

DIRECT_DOCS = [
    "plugins/yandex-direct/references/safety.md",
    "plugins/yandex-direct/skills/yandex-direct/SKILL.md",
    "plugins/yandex-direct/skills/yandex-direct-api/SKILL.md",
    "plugins/yandex-direct/skills/yandex-direct-create/SKILL.md",
    "plugins/yandex-direct/skills/yandex-direct-budget/SKILL.md",
    "plugins/yandex-direct/skills/yandex-direct-keywords/SKILL.md",
    "plugins/yandex-direct/skills/yandex-direct-optimize/SKILL.md",
]
METRIKA_DOCS = [
    "plugins/yandex-metrika/references/safety.md",
    "plugins/yandex-metrika/skills/yandex-metrika/SKILL.md",
    "plugins/yandex-metrika/skills/yandex-metrika-api/SKILL.md",
    "plugins/yandex-metrika/skills/yandex-metrika-goals/SKILL.md",
    "plugins/yandex-metrika/skills/yandex-metrika-imports/SKILL.md",
    "plugins/yandex-metrika/skills/yandex-metrika-logs/SKILL.md",
]
WEBMASTER_DOCS = [
    "plugins/yandex-webmaster/references/safety.md",
    "plugins/yandex-webmaster/skills/yandex-webmaster/SKILL.md",
    "plugins/yandex-webmaster/skills/yandex-webmaster-api/SKILL.md",
    "plugins/yandex-webmaster/skills/yandex-webmaster-site-management/SKILL.md",
    "plugins/yandex-webmaster/skills/yandex-webmaster-recrawl/SKILL.md",
    "plugins/yandex-webmaster/skills/yandex-webmaster-sitemaps/SKILL.md",
    "plugins/yandex-webmaster/skills/yandex-webmaster-feeds/SKILL.md",
    "plugins/yandex-webmaster/skills/yandex-webmaster-indexing/SKILL.md",
    "plugins/yandex-webmaster/skills/yandex-webmaster-exports/SKILL.md",
]
OWNING_DOCS = DIRECT_DOCS + METRIKA_DOCS + WEBMASTER_DOCS

MARKERS = (
    "approval-contract: exact-preview",
    "approval-turn-policy: later-turn-only",
    "untrusted-data-policy: data-not-instructions",
    "permission-policy: payload-specific",
    "adjacent-routing-policy: owning-plugin",
)


class SafetyContractTests(unittest.TestCase):
    def test_every_write_capable_owning_doc_declares_safety_contract(self):
        for relative in OWNING_DOCS:
            with self.subTest(path=relative):
                text = (ROOT / relative).read_text(encoding="utf-8").casefold()
                for marker in MARKERS:
                    self.assertIn(marker, text)

    def test_plugin_standard_declares_human_approval_and_untrusted_data_rules(self):
        for relative in ("docs/PLUGIN_STANDARD.md", "docs/PLUGIN_STANDARD.en.md"):
            with self.subTest(path=relative):
                text = (ROOT / relative).read_text(encoding="utf-8").casefold()
                for marker in MARKERS:
                    self.assertIn(marker, text)
                self.assertIn("preview_id", text)
                self.assertIn("--approve", text)

    def test_contract_matrix_has_preview_bound_write_traceability(self):
        matrix = json.loads((ROOT / "docs/CONTRACT_MATRIX.json").read_text(encoding="utf-8"))
        contracts = {item["id"]: item for item in matrix["contracts"]}
        expected = {
            "direct.preview-bound-write": (
                "plugins/yandex-direct/scripts/yd_api.py",
                "plugins/yandex-direct/tests/test_yd_api.py",
                "plugins/yandex-direct/references/safety.md",
            ),
            "metrika.preview-bound-write": (
                "plugins/yandex-metrika/scripts/ym_api.py",
                "plugins/yandex-metrika/tests/test_ym_api.py",
                "plugins/yandex-metrika/references/safety.md",
            ),
            "webmaster.preview-bound-write": (
                "plugins/yandex-webmaster/scripts/yw_api.py",
                "plugins/yandex-webmaster/tests/test_yw_api.py",
                "plugins/yandex-webmaster/references/safety.md",
            ),
        }
        for contract_id, (helper, test, reference) in expected.items():
            with self.subTest(contract=contract_id):
                item = contracts[contract_id]
                self.assertIn(helper, item["helpers"])
                self.assertIn(test, item["tests"])
                self.assertIn(reference, item["references"])
                self.assertTrue(item["skills"])


if __name__ == "__main__":
    unittest.main()
