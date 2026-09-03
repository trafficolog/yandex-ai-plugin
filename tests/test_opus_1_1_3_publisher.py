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

    def test_publisher_supports_noop_partial_recovery_and_rejects_multi_sha_state(self):
        text = self._text()
        for token in (
            "Detect immutable OPUS 1.1.3 release state",
            "id: release_state",
            "release_count=0",
            "release_shas=()",
            "already_published=true",
            "partial_release=true",
            "Existing OPUS 1.1.3 releases point to multiple commits",
            'git merge-base --is-ancestor "$released_sha" "$TARGET_SHA"',
            "release_target_sha=$released_sha",
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

    def test_partial_recovery_validates_release_target_tree(self):
        text = self._text()
        for token in (
            'RELEASE_WORKTREE="$(mktemp -d)"',
            'git worktree add --detach "$RELEASE_WORKTREE" "$RELEASE_TARGET_SHA"',
            '(cd "$RELEASE_WORKTREE"',
            'python scripts/validate_repo.py',
            'python -m unittest discover -s tests -v',
            'python scripts/check_reference_freshness.py',
        ):
            self.assertIn(token, text)
        self.assertIn('trap \'git worktree remove --force "$RELEASE_WORKTREE" >/dev/null 2>&1 || true\' EXIT', text)

    def test_existing_tags_and_releases_are_verified_against_immutable_target(self):
        text = self._text()
        for token in (
            'if gh release view "$tag"',
            'existing_sha="$(git rev-list -n 1 "$tag")"',
            'if [[ "$existing_sha" != "$RELEASE_TARGET_SHA" ]]',
            '--verify-tag',
            '--target "$RELEASE_TARGET_SHA"',
        ):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
