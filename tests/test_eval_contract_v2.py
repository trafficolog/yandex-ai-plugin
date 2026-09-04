import json
from pathlib import Path
import tempfile
import unittest

from scripts.validate_repo import _validate_evals


class EvalContractV2Tests(unittest.TestCase):
    def make_plugin(self, *, data=None):
        tmp = tempfile.TemporaryDirectory()
        plugin = Path(tmp.name) / "plugins/yandex-direct"
        (plugin / "evals").mkdir(parents=True)
        (plugin / "skills/router").mkdir(parents=True)
        (plugin / "skills/router/SKILL.md").write_text(
            "---\nname: router\ndescription: Use when routing.\n---\n\n"
            "Exact contract tokens: SAFE_TOKEN, wordstat_count\n",
            encoding="utf-8",
        )
        if data is None:
            data = {
                "version": 2,
                "scenarios": [
                    {
                        "prompt": "audit",
                        "skill": "router",
                        "write": False,
                        "expect": {
                            "must_route_to": "router",
                            "outcome": "comply_with_limitations",
                            "must_mention_tokens": ["SAFE_TOKEN", "wordstat_count"],
                            "must_convey": ["Explain the limitation"],
                            "must_not_claim": ["A live write completed"],
                        },
                    }
                ],
            }
        (plugin / "evals/scenarios.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )
        return tmp, plugin

    def validate(self, data=None):
        tmp, plugin = self.make_plugin(data=data)
        self.addCleanup(tmp.cleanup)
        errors = []
        _validate_evals(plugin, errors)
        return errors

    def base_data(self):
        return {
            "version": 2,
            "scenarios": [
                {
                    "prompt": "audit",
                    "skill": "router",
                    "write": False,
                    "expect": {
                        "must_route_to": "router",
                        "outcome": "comply",
                        "must_mention_tokens": ["SAFE_TOKEN"],
                        "must_convey": ["Explain the result"],
                        "must_not_claim": ["A live write completed"],
                    },
                }
            ],
        }

    def test_valid_v2_fixture_passes(self):
        self.assertEqual(self.validate(), [])

    def test_schema_v1_is_rejected(self):
        data = self.base_data()
        data["version"] = 1
        errors = self.validate(data)
        self.assertTrue(any("version 2" in error.lower() for error in errors), errors)

    def test_outcome_is_required_and_limited_to_enum(self):
        for value in (None, "sometimes"):
            with self.subTest(value=value):
                data = self.base_data()
                if value is None:
                    data["scenarios"][0]["expect"].pop("outcome")
                else:
                    data["scenarios"][0]["expect"]["outcome"] = value
                errors = self.validate(data)
                self.assertTrue(any("outcome" in error for error in errors), errors)

    def test_outcome_non_string_values_are_reported_not_raised(self):
        for value in ([], {}, 123, True):
            with self.subTest(value=value):
                data = self.base_data()
                data["scenarios"][0]["expect"]["outcome"] = value
                errors = self.validate(data)
                self.assertTrue(any("outcome" in error for error in errors), errors)

    def test_write_non_scalar_values_are_reported_not_raised(self):
        for value in ([], {}, 123, True, "unknown"):
            with self.subTest(value=value):
                data = self.base_data()
                data["scenarios"][0]["write"] = value
                errors = self.validate(data)
                self.assertTrue(any("write mode" in error for error in errors), errors)

    def test_v2_string_lists_require_nonempty_strings(self):
        for field in ("must_mention_tokens", "must_convey", "must_not_claim"):
            for value in ("not-a-list", [""], [123]):
                with self.subTest(field=field, value=value):
                    data = self.base_data()
                    data["scenarios"][0]["expect"][field] = value
                    errors = self.validate(data)
                    self.assertTrue(any(field in error for error in errors), errors)

    def test_legacy_expectation_keys_are_rejected(self):
        for field, value in (("must_refuse", False), ("must_mention", ["SAFE_TOKEN"])):
            with self.subTest(field=field):
                data = self.base_data()
                data["scenarios"][0]["expect"][field] = value
                errors = self.validate(data)
                self.assertTrue(any(field in error and "legacy" in error.lower() for error in errors), errors)

    def test_route_must_match_skill(self):
        data = self.base_data()
        data["scenarios"][0]["expect"]["must_route_to"] = "other"
        errors = self.validate(data)
        self.assertTrue(any("must_route_to" in error for error in errors), errors)

    def test_skill_must_resolve_to_real_skill_file(self):
        data = self.base_data()
        data["scenarios"][0]["skill"] = "missing-skill"
        data["scenarios"][0]["expect"]["must_route_to"] = "missing-skill"
        errors = self.validate(data)
        self.assertTrue(any("missing-skill" in error and "SKILL.md" in error for error in errors), errors)

    def test_skill_must_be_a_discoverable_immediate_child_name(self):
        data = self.base_data()
        data["scenarios"][0]["skill"] = "../skills/router"
        data["scenarios"][0]["expect"]["must_route_to"] = "../skills/router"
        errors = self.validate(data)
        self.assertTrue(any("discoverable" in error.lower() or "skill name" in error.lower() for error in errors), errors)

    def test_must_mention_tokens_rejects_prose(self):
        data = self.base_data()
        data["scenarios"][0]["expect"]["must_mention_tokens"] = [
            "visitor geography is not ranking region"
        ]
        errors = self.validate(data)
        self.assertTrue(any("must_mention_tokens" in error and "token" in error.lower() for error in errors), errors)

    def test_must_mention_tokens_must_exist_in_plugin_vocabulary(self):
        data = self.base_data()
        data["scenarios"][0]["expect"]["must_mention_tokens"] = ["MISSPELLED_TOKEN"]
        errors = self.validate(data)
        self.assertTrue(any("MISSPELLED_TOKEN" in error and "vocabulary" in error.lower() for error in errors), errors)

    def test_must_mention_tokens_require_exact_vocabulary_identifier_match(self):
        data = self.base_data()
        data["scenarios"][0]["expect"]["must_mention_tokens"] = ["SAFE"]
        errors = self.validate(data)
        self.assertTrue(any("SAFE" in error and "vocabulary" in error.lower() for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
