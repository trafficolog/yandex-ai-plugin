from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-opus-1.1.3.yml"


class Opus113PublisherTests(unittest.TestCase):
    def _text(self) -> str:
        self.assertTrue(WORKFLOW.is_file(), "OPUS 1.1.3 publisher workflow is missing")
        return WORKFLOW.read_text(encoding="utf-8")

    def _publish_function(self) -> str:
        text = self._text()
        start = text.index("publish_release() {")
        end = text.index("          cat > /tmp/opus-1.1.3.md", start)
        return text[start:end]

    def test_publisher_declares_exact_three_tag_release_set(self):
        text = self._text()
        expected = (
            '"opus-1.1.3"',
            '"yandex-wordstat-v1.1.2"',
            '"yandex-seo-v1.1.2"',
        )
        for tag in expected:
            self.assertIn(tag, text)
        for forbidden in (
            "yandex-direct-v",
            "yandex-metrika-v",
            "yandex-webmaster-v",
            "yandex-search-v",
            "yandex-marketing-v",
        ):
            self.assertNotIn(forbidden, text)
        for tag in ("opus-1.1.3", "yandex-wordstat-v1.1.2", "yandex-seo-v1.1.2"):
            self.assertEqual(text.count(f'publish_release "{tag}"'), 1)

    def test_publisher_is_securely_gated_to_exact_successful_main_ci_sha(self):
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
            'test "$(git rev-parse HEAD)" = "$TARGET_SHA"',
        ):
            self.assertIn(token, text)

    def test_publisher_serializes_release_attempts(self):
        text = self._text()
        self.assertIn("concurrency:", text)
        self.assertIn("group: opus-1.1.3-release-publisher", text)
        self.assertIn("cancel-in-progress: false", text)

    def test_initial_publication_rejects_stale_main_workflow_run(self):
        text = self._text()
        no_tags = text.index('if [[ "$tag_count" -eq 0 ]]')
        fetch_current_main = text.index('git fetch origin main --prune', no_tags)
        read_current_main = text.index('current_main_sha="$(git rev-parse origin/main)"', fetch_current_main)
        stale_guard = text.index('if [[ "$current_main_sha" != "$TARGET_SHA" ]]', read_current_main)
        target_selection = text.index('release_target_sha=$TARGET_SHA', stale_guard)
        self.assertLess(no_tags, fetch_current_main)
        self.assertLess(fetch_current_main, read_current_main)
        self.assertLess(read_current_main, stale_guard)
        self.assertLess(stale_guard, target_selection)

    def test_initial_publication_rechecks_main_immediately_before_first_release(self):
        text = self._text()
        first_publish = text.index('publish_release "opus-1.1.3"')
        publish_step = text.rfind('- name: Publish repository and plugin releases', 0, first_publish)
        late_gate = text.index("if [[ \"${{ steps.release_state.outputs.initial_publication }}\" == \"true\" ]]", publish_step)
        late_fetch = text.index('git fetch origin main --prune', late_gate)
        late_read = text.index('current_main_sha="$(git rev-parse origin/main)"', late_fetch)
        late_guard = text.index('if [[ "$current_main_sha" != "$TARGET_SHA" ]]', late_read)
        self.assertLess(publish_step, late_gate)
        self.assertLess(late_gate, late_fetch)
        self.assertLess(late_fetch, late_read)
        self.assertLess(late_read, late_guard)
        self.assertLess(late_guard, first_publish)

    def test_recovery_ancestry_is_checked_against_live_main_tip(self):
        text = self._text()
        recovery = text.index('echo "initial_publication=false"')
        fetch_live_main = text.index('git fetch origin main --prune', recovery)
        live_main = text.index('live_main_sha="$(git rev-parse origin/main)"', fetch_live_main)
        ancestry = text.index('git merge-base --is-ancestor "$immutable_sha" "$live_main_sha"', live_main)
        target_output = text.index('release_target_sha=$immutable_sha', ancestry)
        self.assertLess(recovery, fetch_live_main)
        self.assertLess(fetch_live_main, live_main)
        self.assertLess(live_main, ancestry)
        self.assertLess(ancestry, target_output)

    def test_exact_target_verification_does_not_reject_valid_recovery_against_stale_event_sha(self):
        text = self._text()
        verify_step = text.index('- name: Verify exact release target')
        publish_step = text.index('- name: Publish repository and plugin releases', verify_step)
        segment = text[verify_step:publish_step]
        self.assertIn("if [[ \"${{ steps.release_state.outputs.initial_publication }}\" == \"true\" ]]", segment)
        self.assertIn('test "$RELEASE_TARGET_SHA" = "$TARGET_SHA"', segment)
        self.assertIn('git merge-base --is-ancestor "$RELEASE_TARGET_SHA" "$live_main_sha"', segment)
        self.assertNotIn('git merge-base --is-ancestor "$RELEASE_TARGET_SHA" "$TARGET_SHA"', segment)

    def test_publication_has_no_administration_token_dependency(self):
        text = self._text()
        for forbidden in (
            "IMMUTABILITY_TOKEN",
            "RELEASE_ADMIN_TOKEN",
            "/immutable-releases",
            "/rulesets",
            "OPUS 1.1.3 immutable release tags",
        ):
            self.assertNotIn(forbidden, text)

    def test_draft_release_reserves_exact_target_before_tag_materializes(self):
        function = self._publish_function()
        for token in (
            'gh release create "$tag"',
            '--draft',
            '--target "$RELEASE_TARGET_SHA"',
            '--json isDraft,isImmutable,targetCommitish',
            'draft_target_commitish',
            'if [[ "$draft_target_commitish" != "$RELEASE_TARGET_SHA" ]]',
            'git ls-remote --exit-code origin "refs/tags/$tag"',
            'Draft release $tag unexpectedly materialized a Git tag before publication.',
        ):
            self.assertIn(token, function)
        self.assertNotIn('gh api --method POST "repos/$GITHUB_REPOSITORY/git/refs"', function)

    def test_exact_target_draft_can_resume_but_wrong_target_draft_fails(self):
        function = self._publish_function()
        self.assertIn('if [[ "$release_is_draft" == "true" ]]', function)
        self.assertIn('release_target_commitish', function)
        self.assertIn('Draft release $tag targets $release_target_commitish, expected $RELEASE_TARGET_SHA', function)
        self.assertIn('Reusing exact-target draft release $tag.', function)

    def test_tag_only_state_is_not_converted_without_draft_reservation(self):
        function = self._publish_function()
        self.assertIn('Standalone tag $tag exists without a GitHub Release; refusing unsafe recovery without a draft reservation.', function)

    def test_draft_is_published_with_exact_target_and_must_become_immutable(self):
        function = self._publish_function()
        publish = function.index('gh release edit "$tag"')
        self.assertIn('--draft=false', function[publish:])
        self.assertIn('--target "$RELEASE_TARGET_SHA"', function[publish:])
        for token in (
            'published_is_draft',
            'published_is_immutable',
            'published_target_commitish',
            'if [[ "$published_is_draft" == "true" ]]',
            'if [[ "$published_is_immutable" != "true" ]]',
            'if [[ "$published_target_commitish" != "$RELEASE_TARGET_SHA" ]]',
        ):
            self.assertIn(token, function)

    def test_non_immutable_publication_is_rolled_back_fail_closed(self):
        function = self._publish_function()
        for token in (
            'gh release delete "$tag" --repo "$GITHUB_REPOSITORY" --yes --cleanup-tag',
            'gh release view "$tag" --repo "$GITHUB_REPOSITORY"',
            'git ls-remote --exit-code origin "refs/tags/$tag"',
            'GitHub release immutability is not enabled. Enable it in repository Settings > Releases, then rerun the publisher.',
        ):
            self.assertIn(token, function)
        immutable_guard = function.index('if [[ "$published_is_immutable" != "true" ]]')
        rollback = function.index('gh release delete "$tag"', immutable_guard)
        self.assertLess(immutable_guard, rollback)

    def test_published_release_requires_github_immutability_and_exact_tag_sha(self):
        function = self._publish_function()
        for token in (
            'Published release $tag is not immutable.',
            'git fetch origin "refs/tags/$tag:refs/tags/$tag" --force',
            'existing_sha="$(git rev-list -n 1 "$tag")"',
            'if [[ "$existing_sha" != "$RELEASE_TARGET_SHA" ]]',
            'published_sha="$(git rev-list -n 1 "$tag")"',
            'if [[ "$published_sha" != "$RELEASE_TARGET_SHA" ]]',
        ):
            self.assertIn(token, function)

    def test_publisher_supports_noop_partial_recovery_and_rejects_multi_sha_state(self):
        text = self._text()
        for token in (
            "Detect immutable OPUS 1.1.3 release state",
            "id: release_state",
            "published_release_count=0",
            "tag_count=0",
            "immutable_shas=()",
            "already_published=true",
            "partial_release=true",
            "Existing OPUS 1.1.3 tags/releases point to multiple commits",
            "release_target_sha=$immutable_sha",
            "steps.release_state.outputs.already_published == 'true'",
            "steps.release_state.outputs.partial_release == 'true'",
            "steps.release_state.outputs.already_published != 'true'",
            "RELEASE_TARGET_SHA: ${{ steps.release_state.outputs.release_target_sha }}",
        ):
            self.assertIn(token, text)

    def test_release_target_contract_pins_exact_plugin_matrix_and_docs(self):
        text = self._text()
        expected_checks = (
            'plugins/yandex-direct/.codex-plugin/plugin.json" | grep -F \'"version": "1.0.1"\'',
            'plugins/yandex-metrika/.codex-plugin/plugin.json" | grep -F \'"version": "1.0.3"\'',
            'plugins/yandex-webmaster/.codex-plugin/plugin.json" | grep -F \'"version": "1.0.3"\'',
            'plugins/yandex-wordstat/.codex-plugin/plugin.json" | grep -F \'"version": "1.1.2"\'',
            'plugins/yandex-search/.codex-plugin/plugin.json" | grep -F \'"version": "1.0.2"\'',
            'plugins/yandex-seo/.codex-plugin/plugin.json" | grep -F \'"version": "1.1.2"\'',
            'plugins/yandex-marketing/.codex-plugin/plugin.json" | grep -F \'"version": "1.1.0"\'',
            'git show "$RELEASE_TARGET_SHA:CHANGELOG.md" | grep -F \'## [OPUS 1.1.3] — 2026-09-03\'',
            'git show "$RELEASE_TARGET_SHA:CHANGELOG.en.md" | grep -F \'## [OPUS 1.1.3] — 2026-09-03\'',
            'git show "$RELEASE_TARGET_SHA:docs/superpowers/specs/2026-09-03-opus-1.1.3-phase7-audit-hardening-amendment.md"',
        )
        for token in expected_checks:
            self.assertIn(token, text)

    def test_partial_recovery_validates_release_target_tree_and_released_plugin_suites(self):
        text = self._text()
        for token in (
            'RELEASE_WORKTREE="$(mktemp -d)"',
            'git worktree add --detach "$RELEASE_WORKTREE" "$RELEASE_TARGET_SHA"',
            '(cd "$RELEASE_WORKTREE"',
            'python scripts/validate_repo.py',
            'python -m unittest discover -s tests -v',
            'python scripts/check_reference_freshness.py',
            '(cd "$RELEASE_WORKTREE/plugins/yandex-wordstat" && python -m unittest discover -s tests -v)',
            '(cd "$RELEASE_WORKTREE/plugins/yandex-seo" && python -m unittest discover -s tests -v)',
        ):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
