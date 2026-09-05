from pathlib import Path
import unittest

from scripts import bilingual_docs


ROOT = Path(__file__).resolve().parents[1]
RU_LONG_ON_USE = "schema-compatible deferred-auth metadata"
EN_LONG_ON_USE = "schema-compatible deferred-auth metadata"
CLOSURE_RU = "docs/reviews/2026-09-05-fable-round2-closure.md"
CLOSURE_EN = "docs/reviews/2026-09-05-fable-round2-closure.en.md"


class FableRound2GovernanceBaselineTests(unittest.TestCase):
    def test_architecture_is_the_single_long_form_on_use_owner(self):
        ru_paths = (
            "docs/ARCHITECTURE.md",
            "docs/PLUGIN_STANDARD.md",
            "docs/SERVICE_MATRIX.md",
            "plugins/yandex-seo/README.md",
            "plugins/yandex-marketing/README.md",
        )
        en_paths = (
            "docs/ARCHITECTURE.en.md",
            "docs/PLUGIN_STANDARD.en.md",
            "docs/SERVICE_MATRIX.en.md",
            "plugins/yandex-seo/README.en.md",
            "plugins/yandex-marketing/README.en.md",
        )
        ru_counts = {path: (ROOT / path).read_text(encoding="utf-8").count(RU_LONG_ON_USE) for path in ru_paths}
        en_counts = {path: (ROOT / path).read_text(encoding="utf-8").count(EN_LONG_ON_USE) for path in en_paths}
        self.assertEqual(ru_counts["docs/ARCHITECTURE.md"], 1, ru_counts)
        self.assertEqual(en_counts["docs/ARCHITECTURE.en.md"], 1, en_counts)
        self.assertEqual(sum(ru_counts.values()), 1, ru_counts)
        self.assertEqual(sum(en_counts.values()), 1, en_counts)

    def test_architecture_search_evidence_node_remains_explicit(self):
        en = (ROOT / "docs/ARCHITECTURE.en.md").read_text(encoding="utf-8")
        self.assertIn("S[Search] --> E", en)

    def test_roadmap_marks_initial_versions_and_ru_primary_prose(self):
        ru = (ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
        en = (ROOT / "docs/ROADMAP.en.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(ru.count("Изначально выпущен"), 5)
        self.assertGreaterEqual(en.count("Initially shipped"), 5)
        self.assertIn("девятью initial workflow skills", ru)
        self.assertIn("nine initial workflow skills", en)
        self.assertNotIn("The plugin contains no Yandex API clients and performs no live writes.", ru)
        self.assertIn("обычные предложения", ru.casefold())
        self.assertIn("русск", ru.casefold())

    def test_roadmap_tracks_model_eval_runner_and_backend_equivalence(self):
        for relative in ("docs/ROADMAP.md", "docs/ROADMAP.en.md"):
            text = (ROOT / relative).read_text(encoding="utf-8").casefold()
            with self.subTest(relative=relative):
                self.assertIn("model eval runner", text)
                self.assertIn("judge", text)
                self.assertIn("outcome", text)
                self.assertIn("must_convey", text)
                self.assertIn("must_not_claim", text)
                self.assertIn("runtime", text)
                self.assertIn("model", text)
                self.assertIn("version", text)
                self.assertIn("timestamp", text)
                self.assertIn("backend-equivalence", text)
                self.assertIn("mcp/app", text)
                self.assertIn("bundled", text)
                self.assertIn("exact-preview", text)
                self.assertIn("later-turn", text)

    def test_community_governance_files_exist_and_route_sensitive_reports(self):
        required = (
            "CODE_OF_CONDUCT.md",
            "CODE_OF_CONDUCT.en.md",
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/feature_request.md",
            ".github/pull_request_template.md",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)
        bug = (ROOT / ".github/ISSUE_TEMPLATE/bug_report.md").read_text(encoding="utf-8").casefold()
        self.assertIn("security.md", bug)
        self.assertIn("public", bug)
        pr = (ROOT / ".github/pull_request_template.md").read_text(encoding="utf-8").casefold()
        for token in ("scope", "tests", "ci", "documentation", "semver", "secrets", "safety", "review"):
            with self.subTest(token=token):
                self.assertIn(token, pr)

    def test_root_readmes_link_governance_entrypoints(self):
        for relative in ("README.md", "README.en.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(relative=relative):
                for target in ("SECURITY", "CONTRIBUTING.md", "CODE_OF_CONDUCT", "docs/reviews/README"):
                    self.assertIn(target, text)
                self.assertIn("2026-09-05-fable-round2-closure", text)

    def test_root_policy_pairs_are_mechanically_registered(self):
        self.assertEqual(set(bilingual_docs.ROOT_POLICY_NAMES), {"SECURITY", "CODE_OF_CONDUCT"})

    def test_fable_round2_closure_artifacts_are_indexed_and_truthful(self):
        for relative in (CLOSURE_RU, CLOSURE_EN):
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            text = path.read_text(encoding="utf-8").casefold()
            self.assertIn("closed", text)
            self.assertIn("closed as explicit backlog", text)
            self.assertIn("previously closed", text)
            self.assertIn("mechanical", text)
            self.assertIn("semantic", text)
            self.assertNotIn("final merge sha:", text)
            self.assertNotIn("post-merge ci:", text)
            self.assertNotIn("release id:", text)
        for relative in ("docs/reviews/README.md", "docs/reviews/README.en.md"):
            self.assertIn("2026-09-05-fable-round2-closure", (ROOT / relative).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
