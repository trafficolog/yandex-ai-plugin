from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-opus-1.1.2.yml"


class Opus112PublisherTests(unittest.TestCase):
    def _text(self) -> str:
        return WORKFLOW.read_text(encoding="utf-8")

    def test_publisher_declares_exact_release_set(self):
        text = self._text()
        for tag in (
            '"opus-1.1.2"',
            '"yandex-metrika-v1.0.3"',
        ):
            self.assertIn(tag, text)
        for forbidden in (
            "yandex-direct-v",
            "yandex-webmaster-v",
            "yandex-wordstat-v",
            "yandex-search-v",
            "yandex-seo-v",
            "yandex-marketing-v",
        ):
            self.assertNotIn(forbidden, text)
        self.assertEqual(text.count('publish_release "opus-1.1.2"'), 1)
        self.assertEqual(text.count('publish_release "yandex-metrika-v1.0.3"'), 1)

    def test_publisher_is_securely_gated_to_exact_successful_main_ci_sha(self):
        text = self._text()
        for token in (
            'workflows: ["CI"]',
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
            "Detect immutable OPUS 1.1.2 release state",
            "id: release_state",
            "release_count=0",
            "release_shas=()",
            "already_published=true",
            "partial_release=true",
            "Existing OPUS 1.1.2 releases point to multiple commits",
            'git merge-base --is-ancestor "$released_sha" "$TARGET_SHA"',
            "release_target_sha=$released_sha",
            "steps.release_state.outputs.already_published == 'true'",
            "steps.release_state.outputs.partial_release == 'true'",
            "steps.release_state.outputs.already_published != 'true'",
            "RELEASE_TARGET_SHA: ${{ steps.release_state.outputs.release_target_sha }}",
        ):
            self.assertIn(token, text)

    def test_release_target_contract_pins_metrika_and_repository_versions(self):
        text = self._text()
        for token in (
            'git show "$RELEASE_TARGET_SHA:plugins/yandex-metrika/.codex-plugin/plugin.json" | grep -F \'"version": "1.0.3"\'',
            'git show "$RELEASE_TARGET_SHA:CHANGELOG.md" | grep -F \'## [OPUS 1.1.2] — 2026-09-03\'',
            'git show "$RELEASE_TARGET_SHA:docs/superpowers/specs/2026-09-03-opus-1.1.2-residual-audit-hardening-amendment.md"',
            '"version": "1.0.1"',
            '"version": "1.0.3"',
            '"version": "1.1.1"',
            '"version": "1.0.2"',
            '"version": "1.1.0"',
        ):
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
