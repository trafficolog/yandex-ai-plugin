from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-opus-1.1.3.yml"


class Opus113PublisherTests(unittest.TestCase):
    def _text(self) -> str:
        self.assertTrue(WORKFLOW.is_file(), "OPUS 1.1.3 publisher workflow is missing")
        return WORKFLOW.read_text(encoding="utf-8")

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
        self.assertIn('Stale main CI run: current main is $current_main_sha, target is $TARGET_SHA.', text)

    def test_initial_publication_rechecks_main_immediately_before_first_release(self):
        text = self._text()
        for token in (
            'initial_publication=true',
            'initial_publication=false',
            'Late stale main CI run: current main is $current_main_sha, target is $TARGET_SHA.',
        ):
            self.assertIn(token, text)
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
        self.assertNotIn('publish_release "', text[late_gate:late_guard])

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
        self.assertIn('Existing OPUS 1.1.3 immutable commit $immutable_sha is not an ancestor of live main $live_main_sha', text)

    def test_publication_checks_immutability_before_optional_admin_put(self):
        text = self._text()
        publish_step = text.index('- name: Publish repository and plugin releases')
        first_release = text.index('publish_release "opus-1.1.3"', publish_step)
        segment = text[publish_step:first_release]
        get_setting = segment.index(
            'immutable_enabled="$(GH_TOKEN="$IMMUTABILITY_TOKEN" gh api "repos/$GITHUB_REPOSITORY/immutable-releases" --jq \'.enabled\' 2>/dev/null || true)"'
        )
        conditional = segment.index('if [[ "$immutable_enabled" != "true" ]]', get_setting)
        put_setting = segment.index(
            'GH_TOKEN="$IMMUTABILITY_TOKEN" gh api --method PUT "repos/$GITHUB_REPOSITORY/immutable-releases"',
            conditional,
        )
        second_get = segment.index(
            'immutable_enabled="$(GH_TOKEN="$IMMUTABILITY_TOKEN" gh api "repos/$GITHUB_REPOSITORY/immutable-releases" --jq \'.enabled\')"',
            put_setting,
        )
        final_guard = segment.index('if [[ "$immutable_enabled" != "true" ]]', second_get)
        self.assertLess(get_setting, conditional)
        self.assertLess(conditional, put_setting)
        self.assertLess(put_setting, second_get)
        self.assertLess(second_get, final_guard)

    def test_release_tags_are_locked_against_updates_and_deletions_before_publication(self):
        text = self._text()
        publish_step = text.index('- name: Publish repository and plugin releases')
        first_publish = text.index('publish_release "opus-1.1.3"', publish_step)
        segment = text[publish_step:first_publish]
        for token in (
            'OPUS 1.1.3 immutable release tags',
            '"target":"tag"',
            '"enforcement":"active"',
            '"refs/tags/opus-1.1.3"',
            '"refs/tags/yandex-wordstat-v1.1.2"',
            '"refs/tags/yandex-seo-v1.1.2"',
            '"type":"update"',
            '"type":"deletion"',
            '"bypass_actors":[]',
            'GH_TOKEN="$IMMUTABILITY_TOKEN" gh api --method POST "repos/$GITHUB_REPOSITORY/rulesets" --input -',
            'GH_TOKEN="$IMMUTABILITY_TOKEN" gh api "repos/$GITHUB_REPOSITORY/rulesets/$release_tag_ruleset_id"',
            'release_tag_ruleset_verified=true',
        ):
            self.assertIn(token, segment)
        self.assertNotIn('"type":"creation"', segment)
        verify_index = segment.index('release_tag_ruleset_verified=true')
        self.assertLess(verify_index, segment.index('publish_release() {'))

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

    def test_draft_release_is_rejected_as_mutable_not_published_state(self):
        text = self._text()
        for token in (
            'if [[ "$release_is_draft" == "true" ]]',
            'Draft release $tag is mutable and cannot count as published.',
        ):
            self.assertIn(token, text)

    def test_published_release_requires_github_immutability_and_new_release_is_rechecked(self):
        text = self._text()
        for token in (
            '--json isDraft,isImmutable',
            'release_is_immutable',
            'if [[ "$release_is_immutable" != "true" ]]',
            'Published release $tag is not immutable.',
            'created_is_immutable="$(gh release view "$tag"',
            'if [[ "$created_is_immutable" != "true" ]]',
            'New release $tag was published without GitHub immutability.',
        ):
            self.assertIn(token, text)
        self.assertGreaterEqual(text.count('--json isDraft,isImmutable'), 2)

    def test_tag_only_state_contributes_to_immutable_recovery_target(self):
        text = self._text()
        for token in (
            'if git show-ref --verify --quiet "refs/tags/$tag"; then',
            'tag_sha="$(git rev-list -n 1 "$tag")"',
            'immutable_shas+=("$tag_sha")',
            'tag_count=$((tag_count + 1))',
            'if [[ "$tag_count" -eq 0 ]]',
            'immutable_sha="${immutable_shas[0]}"',
            'release_target_sha=$immutable_sha',
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
        self.assertIn('trap \'git worktree remove --force "$RELEASE_WORKTREE" >/dev/null 2>&1 || true\' EXIT', text)

    def test_publish_release_atomically_creates_and_verifies_target_tag(self):
        text = self._text()
        function_start = text.index('publish_release() {')
        function_end = text.index("          cat > /tmp/opus-1.1.3.md", function_start)
        function = text[function_start:function_end]
        for token in (
            'gh api --method POST "repos/$GITHUB_REPOSITORY/git/refs"',
            '-f ref="refs/tags/$tag"',
            '-f sha="$RELEASE_TARGET_SHA"',
            'git fetch origin "refs/tags/$tag:refs/tags/$tag" --force',
            'existing_sha="$(git rev-list -n 1 "$tag")"',
            'if [[ "$existing_sha" != "$RELEASE_TARGET_SHA" ]]',
            'gh release create "$tag"',
            '--verify-tag',
        ):
            self.assertIn(token, function)
        self.assertNotIn('--target "$RELEASE_TARGET_SHA"', function)
        verify_sha = function.index('if [[ "$existing_sha" != "$RELEASE_TARGET_SHA" ]]', function.index('gh api --method POST'))
        create_release = function.index('gh release create "$tag"', verify_sha)
        self.assertLess(verify_sha, create_release)

    def test_existing_tags_and_releases_are_verified_against_immutable_target(self):
        text = self._text()
        for token in (
            'existing_sha="$(git rev-list -n 1 "$tag")"',
            'if [[ "$existing_sha" != "$RELEASE_TARGET_SHA" ]]',
            '--verify-tag',
        ):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
