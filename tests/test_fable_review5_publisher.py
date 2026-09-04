from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-fable-review5-maintenance.yml"


class FableReview5PublisherTests(unittest.TestCase):
    def _text(self) -> str:
        self.assertTrue(WORKFLOW.is_file(), "FABLE review-5 maintenance publisher workflow is missing")
        return WORKFLOW.read_text(encoding="utf-8")

    def test_declares_exact_release_set(self):
        text = self._text()
        self.assertIn("yandex-direct-v2.0.1", text)
        self.assertIn('"1.0.3"', text)
        self.assertNotIn("yandex-seo-v1.1.3", text)
        for forbidden in (
            "yandex-metrika-v2.0.1",
            "yandex-webmaster-v2.0.1",
            "yandex-wordstat-v",
            "yandex-search-v",
            "yandex-marketing-v",
        ):
            self.assertNotIn(forbidden, text)
        self.assertEqual(text.count('publish_one yandex-direct-v2.0.1'), 1)
        self.assertEqual(text.count('publish_one "1.0.3"'), 1)

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

    def test_serializes_release_attempts(self):
        text = self._text()
        self.assertIn("concurrency:", text)
        self.assertIn("group: fable-review5-maintenance-release-publisher", text)
        self.assertIn("cancel-in-progress: false", text)

    def test_reuses_existing_fable_publisher_shape(self):
        text = self._text()
        for token in (
            "uses: actions/setup-python@v5",
            "python-version: '3.13'",
            'git cat-file -e "$RELEASE_TARGET^{commit}"',
            'git worktree add --detach "$WT" "$RELEASE_TARGET"',
        ):
            self.assertIn(token, text)
        self.assertNotIn("- name: Checkout release target", text)
        self.assertNotIn("release_probe() {", text)

    def test_initial_publish_rejects_stale_main_and_recovery_requires_ancestor(self):
        text = self._text()
        self.assertIn('if [[ "$live_main" != "$TARGET_SHA" ]]', text)
        self.assertIn('git merge-base --is-ancestor "$release_target" "$live_main"', text)
        self.assertIn('initial=true', text)
        self.assertIn('initial=false', text)

    def test_release_state_is_idempotent_and_single_sha(self):
        text = self._text()
        for token in (
            "candidates=()",
            "published=0",
            "drafts=0",
            "Existing FABLE review-5 release state spans multiple commits",
            'if [[ "$published" -eq 2 && "$drafts" -eq 0 ]]',
            "complete=true",
            "complete=false",
            "steps.state.outputs.complete != 'true'",
        ):
            self.assertIn(token, text)

    def test_exact_target_contract_pins_current_versions_and_docs(self):
        text = self._text()
        for token in (
            'verify_manifest_version "plugins/yandex-direct/.codex-plugin/plugin.json" "2.0.1"',
            'verify_manifest_version "plugins/yandex-direct/.claude-plugin/plugin.json" "2.0.1"',
            'verify_manifest_version "plugins/yandex-metrika/.codex-plugin/plugin.json" "2.0.0"',
            'verify_manifest_version "plugins/yandex-webmaster/.codex-plugin/plugin.json" "2.0.0"',
            "## [2.0.1] — 2026-09-04",
            "## [1.0.3] — 2026-09-04",
            'python scripts/validate_repo.py',
            'python -m unittest discover -s tests -v',
            'plugins/yandex-direct" && python -m unittest discover -s tests -v && python -m compileall -q scripts',
        ):
            self.assertIn(token, text)

    def test_draft_reservation_and_publication_require_exact_target_and_immutability(self):
        text = self._text()
        for token in (
            'gh release create "$tag"',
            '--draft --target "$RELEASE_TARGET"',
            'Draft reservation $tag unexpectedly materialized a tag.',
            'gh release edit "$tag"',
            '--draft=false --target "$RELEASE_TARGET"',
            'if [[ "$is_immutable" != "true" ]]',
            'git fetch origin "refs/tags/$tag:refs/tags/$tag" --force',
            '[[ "$tag_sha" == "$RELEASE_TARGET" ]]',
        ):
            self.assertIn(token, text)

    def test_fail_closed_cleanup_checks_release_and_tag_residue(self):
        text = self._text()
        for token in (
            "rollback_published_release()",
            'gh release delete "$tag" --repo "$GITHUB_REPOSITORY" --yes --cleanup-tag',
            'gh release view "$tag" --repo "$GITHUB_REPOSITORY"',
            'git ls-remote --exit-code origin "refs/tags/$tag"',
            "Rollback residue: release $tag remains.",
            "Rollback residue: tag $tag remains.",
        ):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
