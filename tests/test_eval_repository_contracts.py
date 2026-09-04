import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAMES = (
    "yandex-direct",
    "yandex-metrika",
    "yandex-webmaster",
    "yandex-wordstat",
    "yandex-search",
    "yandex-seo",
    "yandex-marketing",
)
WRITE_CAPABLE = ("yandex-direct", "yandex-metrika", "yandex-webmaster")


class EvalRepositoryContractTests(unittest.TestCase):
    def load(self, plugin_name):
        path = ROOT / "plugins" / plugin_name / "evals/scenarios.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_all_active_eval_fixtures_use_v2_without_legacy_keys(self):
        for plugin_name in PLUGIN_NAMES:
            with self.subTest(plugin=plugin_name):
                data = self.load(plugin_name)
                self.assertEqual(data["version"], 2)
                text = json.dumps(data, ensure_ascii=False)
                self.assertNotIn('"must_refuse"', text)
                self.assertNotIn('"must_mention"', text)
                for scenario in data["scenarios"]:
                    expect = scenario["expect"]
                    self.assertIn(expect["outcome"], {"comply", "comply_with_limitations", "refuse"})
                    self.assertIn("must_mention_tokens", expect)
                    self.assertIn("must_convey", expect)
                    self.assertIn("must_not_claim", expect)

    def assert_adversarial_refusal(self, plugin_name, scenarios, label):
        self.assertTrue(scenarios, f"{plugin_name} lacks a {label} scenario")
        for scenario in scenarios:
            with self.subTest(plugin=plugin_name, adversarial=label, prompt=scenario["prompt"]):
                self.assertEqual(scenario["write"], "approval-required")
                expect = scenario["expect"]
                self.assertEqual(expect["outcome"], "refuse")
                self.assertIn("preview_id", expect["must_mention_tokens"])
                self.assertTrue(
                    any("fresh exact preview" in item.lower() for item in expect["must_convey"]),
                    f"{plugin_name} {label} scenario must require a fresh exact preview",
                )

    def test_write_capable_plugins_cover_injection_and_fake_prior_approval(self):
        for plugin_name in WRITE_CAPABLE:
            data = self.load(plugin_name)
            scenarios = data["scenarios"]
            injection = [
                scenario
                for scenario in scenarios
                if "system:" in scenario["prompt"].lower()
                or "инструкц" in scenario["prompt"].lower()
            ]
            fake_prior_approval = [
                scenario
                for scenario in scenarios
                if ("раньше" in scenario["prompt"].lower() or "когда-то" in scenario["prompt"].lower())
                and ("preview" in scenario["prompt"].lower() or "разреш" in scenario["prompt"].lower())
            ]
            self.assert_adversarial_refusal(plugin_name, injection, "untrusted-data injection")
            self.assert_adversarial_refusal(plugin_name, fake_prior_approval, "fake-prior-approval")

    def test_plugin_standard_documents_eval_v2_and_semantic_limit(self):
        for filename in ("PLUGIN_STANDARD.md", "PLUGIN_STANDARD.en.md"):
            with self.subTest(filename=filename):
                text = (ROOT / "docs" / filename).read_text(encoding="utf-8")
                for token in (
                    "must_route_to",
                    "outcome",
                    "must_mention_tokens",
                    "must_convey",
                    "must_not_claim",
                ):
                    self.assertIn(token, text)
                lowered = text.lower()
                self.assertIn("version", lowered)
                self.assertTrue(
                    ("не запускает" in lowered and "модел" in lowered)
                    or ("does not" in lowered and "model" in lowered),
                    f"{filename} must state that structural validation does not execute model semantic evals",
                )


if __name__ == "__main__":
    unittest.main()
