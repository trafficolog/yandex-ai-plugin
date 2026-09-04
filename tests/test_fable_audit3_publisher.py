from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-fable-audit3-maintenance.yml"


class FableAudit3PublisherTests(unittest.TestCase):
    def _text(self) -> str:
        self.assertTrue(WORKFLOW.is_file(), "FABLE audit-3 maintenance publisher workflow is missing")
        return WORKFLOW.read_text(encoding="utf-8")

    def test_declares_repository_only_release_set(self):
        text = self._text()
        self.assertEqual(text.count('publish_one "1.0.4"'), 1)
        for forbidden in (
            "yandex-direct-v2.0.2",
            "yandex-metrika-v2.0.1",
            "yandex-webmaster-v2.0.1",
            "yandex-wordstat-v1.1.3",
            "yandex-search-v1.0.3",
            "yandex-seo-v1.1.3",
            "yandex-marketing-v1.1.1",
        ):
            self.assertNotIn(forbidden, text)

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

    def test_reuses_hardened_fable_publisher_shape(self):
        text = self._text()
        for token in (
            "group: fable-audit3-maintenance-release-publisher",
            "cancel-in-progress: false",
            "uses: actions/setup-python@v5",
            "python-version: '3.13'",
            'git cat-file -e "$RELEASE_TARGET^{commit}"',
            'git worktree add --detach "$WT" "$RELEASE_TARGET"',
            "set -Eeuo pipefail",
            "rollback_published_release()",
            'gh release delete "$tag" --repo "$GITHUB_REPOSITORY" --yes --cleanup-tag',
        ):
            self.assertIn(token, text)

    def test_release_state_is_idempotent_exact_sha_and_fail_closed(self):
        text = self._text()
        for token in (
            "candidates=()",
            "published=0",
            "drafts=0",
            'if [[ ! "$target" =~ ^[0-9a-fA-F]{40}$ ]]',
            'git merge-base --is-ancestor "$release_target" "$live_main"',
            'if [[ "$published" -eq 1 && "$drafts" -eq 0 ]]',
            "steps.state.outputs.complete != 'true'",
            'git ls-remote --exit-code origin "refs/tags/$tag"',
            '[[ "$tag_sha" == "$RELEASE_TARGET" ]]',
        ):
            self.assertIn(token, text)

    def test_exact_target_contract_pins_unchanged_plugin_matrix_and_repository_docs(self):
        text = self._text()
        for token in (
            'verify_manifest_version "plugins/yandex-direct/.codex-plugin/plugin.json" "2.0.1"',
            'verify_manifest_version "plugins/yandex-metrika/.codex-plugin/plugin.json" "2.0.0"',
            'verify_manifest_version "plugins/yandex-webmaster/.codex-plugin/plugin.json" "2.0.0"',
            'verify_manifest_version "plugins/yandex-wordstat/.codex-plugin/plugin.json" "1.1.2"',
            'verify_manifest_version "plugins/yandex-search/.codex-plugin/plugin.json" "1.0.2"',
            'verify_manifest_version "plugins/yandex-seo/.codex-plugin/plugin.json" "1.1.2"',
            'verify_manifest_version "plugins/yandex-marketing/.codex-plugin/plugin.json" "1.1.0"',
            "## [1.0.4] — 2026-09-04",
            'python scripts/validate_repo.py',
            'python -m unittest discover -s tests -v',
        ):
            self.assertIn(token, text)

    def test_repository_release_state_is_1_0_4_in_bilingual_docs(self):
        for filename in ("README.md", "README.en.md"):
            text = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn("release-1.0.4", text, filename)
            self.assertIn("1.0.4", text, filename)
        for filename in ("CHANGELOG.md", "CHANGELOG.en.md"):
            text = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn("## [1.0.4] — 2026-09-04", text, filename)


if __name__ == "__main__":
    unittest.main()
