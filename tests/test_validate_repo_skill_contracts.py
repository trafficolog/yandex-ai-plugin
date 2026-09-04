from pathlib import Path
import json
import tempfile
import unittest

import scripts.validate_repo as validator


class SkillContractValidationTests(unittest.TestCase):
    def write_skill(
        self,
        root: Path,
        plugin: str,
        directory: str,
        *,
        name: str | None = None,
        description: str = "Use when a concrete Yandex workflow requires this specialized capability.",
        body: str = "# Skill\n",
    ) -> Path:
        path = root / "plugins" / plugin / "skills" / directory / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        skill_name = name if name is not None else directory
        path.write_text(
            f"---\nname: {skill_name}\ndescription: {description}\n---\n\n{body}",
            encoding="utf-8",
        )
        return path

    def test_skill_name_must_match_discoverable_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_skill(Path(tmp), "yandex-test", "expected-name", name="wrong-name")
            errors: list[str] = []
            validator._validate_skill(path, errors)
            self.assertTrue(any("must match directory" in error for error in errors), errors)

    def test_skill_description_has_bounded_router_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            too_short = self.write_skill(root, "yandex-test", "short", description="Use when needed.")
            too_long = self.write_skill(
                root,
                "yandex-test",
                "long",
                description="Use when " + "specific routing context " * 30,
            )
            for path in (too_short, too_long):
                with self.subTest(path=path.parent.name):
                    errors: list[str] = []
                    validator._validate_skill(path, errors)
                    self.assertTrue(any("description length" in error for error in errors), errors)

    def test_skill_file_size_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_skill(
                Path(tmp),
                "yandex-test",
                "oversized",
                body="x" * (16 * 1024),
            )
            errors: list[str] = []
            validator._validate_skill(path, errors)
            self.assertTrue(any("size limit" in error for error in errors), errors)

    def test_skill_names_are_unique_across_marketplace_plugins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self.write_skill(root, "yandex-a", "shared-skill")
            second = self.write_skill(root, "yandex-b", "shared-skill")
            errors: list[str] = []
            validator._validate_marketplace_skill_names([first, second], errors)
            self.assertTrue(any("duplicate skill name" in error for error in errors), errors)

    def test_write_eval_requires_generic_safety_markers_in_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins" / "yandex-test"
            self.write_skill(root, "yandex-test", "writer", body="# Write flow\n")
            evals = plugin / "evals" / "scenarios.json"
            evals.parent.mkdir(parents=True, exist_ok=True)
            evals.write_text(
                json.dumps(
                    {
                        "version": 2,
                        "scenarios": [
                            {
                                "prompt": "perform a write",
                                "skill": "writer",
                                "write": "approval-required",
                                "expect": {
                                    "must_route_to": "writer",
                                    "outcome": "comply",
                                    "must_mention_tokens": [],
                                    "must_convey": ["approval required"],
                                    "must_not_claim": ["automatic execution"],
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            validator._validate_evals(plugin, errors)
            self.assertTrue(any("write-capable skill missing safety marker" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
