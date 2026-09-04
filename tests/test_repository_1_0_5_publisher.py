from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-repository-1.0.5.yml"

PLUGIN_VERSIONS = {
    "yandex-direct": "2.0.1",
    "yandex-metrika": "2.0.0",
    "yandex-webmaster": "2.0.0",
    "yandex-wordstat": "1.1.2",
    "yandex-search": "1.0.2",
    "yandex-seo": "1.1.2",
    "yandex-marketing": "1.1.0",
}


class Repository105PublisherTests(unittest.TestCase):
    def _text(self) -> str:
        self.assertTrue(WORKFLOW.is_file(), "repository 1.0.5 publisher workflow is missing")
        return WORKFLOW.read_text(encoding="utf-8")

    def test_declares_repository_only_release_set(self):
        text = self._text()
        self.assertEqual(text.count('publish_one "1.0.5"'), 1)
        self.assertNotIn('publish_one "1.0.4"', text)
        for plugin, version in PLUGIN_VERSIONS.items():
            self.assertNotIn(f"{plugin}-v{version}", text)

    def test_is_gated_to_exact_successful_main_ci_sha(self):
        text = self._text()
        for token in (
            'workflows: ["CI"]',
            "github.repository == 'trafficolog/yandex-ai-plugins-skills'",
            "github.event.workflow_run.conclusion == 'success'",
            "github.event.workflow_run.event == 'push'",
            "github.event.workflow_run.head_repository.full_name == github.repository",
            "github.event.workflow_run.head_branch == 'main'",
            "TARGET_SHA: ${{ github.event.workflow_run.head_sha }}",
            "ref: ${{ env.TARGET_SHA }}",
        ):
            self.assertIn(token, text)

    def test_reuses_hardened_exact_target_and_fail_closed_shape(self):
        text = self._text()
        for token in (
            "group: repository-1-0-5-release-publisher",
            "cancel-in-progress: false",
            "uses: actions/setup-python@v5",
            "python-version: '3.13'",
            "candidates=()",
            "published=0",
            "drafts=0",
            'git merge-base --is-ancestor "$release_target" "$live_main"',
            'git cat-file -e "$RELEASE_TARGET^{commit}"',
            'git worktree add --detach "$WT" "$RELEASE_TARGET"',
            "set -Eeuo pipefail",
            "rollback_published_release()",
            'gh release delete "$tag" --repo "$GITHUB_REPOSITORY" --yes --cleanup-tag',
            '[[ "$tag_sha" == "$RELEASE_TARGET" ]]',
        ):
            self.assertIn(token, text)

    def test_exact_target_contract_pins_plugin_matrix_and_human_docs(self):
        text = self._text()
        for plugin, version in PLUGIN_VERSIONS.items():
            for family in (".codex-plugin", ".claude-plugin"):
                self.assertIn(
                    f'verify_manifest_version "plugins/{plugin}/{family}/plugin.json" "{version}"',
                    text,
                )
        for token in (
            "## [1.0.5] — 2026-09-04",
            "release-1.0.5",
            "docs/GETTING_STARTED.md",
            "docs/GETTING_STARTED.en.md",
            "docs/ARCHITECTURE.md",
            "docs/ARCHITECTURE.en.md",
            "docs/GLOSSARY.md",
            "docs/GLOSSARY.en.md",
            "docs/RELEASE_POLICY.md",
            "docs/RELEASE_POLICY.en.md",
            "CONTRIBUTING.md",
            "python scripts/validate_repo.py",
            "python -m unittest discover -s tests -v",
        ):
            self.assertIn(token, text)

    def test_repository_release_state_is_1_0_5_in_bilingual_docs(self):
        for filename in ("README.md", "README.en.md"):
            text = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn("release-1.0.5", text, filename)
            self.assertIn("1.0.5", text, filename)
        for filename in ("CHANGELOG.md", "CHANGELOG.en.md"):
            text = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn("## [1.0.5] — 2026-09-04", text, filename)


if __name__ == "__main__":
    unittest.main()
