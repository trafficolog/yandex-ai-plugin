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

    def test_write_capable_plugins_cover_injection_and_fake_prior_approval(self):
        for plugin_name in WRITE_CAPABLE:
            with self.subTest(plugin=plugin_name):
                data = self.load(plugin_name)
                prompts = [scenario["prompt"].lower() for scenario in data["scenarios"]]
                self.assertTrue(
                    any("system:" in prompt or "инструкц" in prompt for prompt in prompts),
                    f"{plugin_name} lacks an untrusted-data injection scenario",
                )
                self.assertTrue(
                    any(
                        ("раньше" in prompt or "когда-то" in prompt)
                        and ("preview" in prompt or "разреш" in prompt)
                        for prompt in prompts
                    ),
                    f"{plugin_name} lacks a fake-prior-approval scenario",
                )

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
