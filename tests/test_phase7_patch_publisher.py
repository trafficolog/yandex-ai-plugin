from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-phase-7-topical-architecture-1.0.1.yml"


class Phase7PatchPublisherTests(unittest.TestCase):
    def test_patch_publisher_is_secure_and_targets_exact_main_ci_sha(self):
        self.assertTrue(WORKFLOW.is_file())
        text = WORKFLOW.read_text(encoding="utf-8")
        for token in [
            'workflows: ["CI"]',
            "github.event.workflow_run.conclusion == 'success'",
            "github.event.workflow_run.event == 'push'",
            "github.event.workflow_run.head_repository.full_name == github.repository",
            "github.event.workflow_run.head_branch == 'main'",
            "TARGET_SHA: ${{ github.event.workflow_run.head_sha }}",
            "Verify exact release target",
        ]:
            self.assertIn(token, text)

    def test_patch_publisher_declares_only_expected_patch_tags(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = [
            "phase-7-topical-architecture-1.0.1",
            "yandex-wordstat-v1.1.1",
            "yandex-seo-v1.1.1",
        ]
        for tag in expected:
            self.assertIn(tag, text)
        for old_tag in [
            "phase-7-topical-architecture-1.0.0",
            "yandex-wordstat-v1.1.0",
            "yandex-seo-v1.1.0",
        ]:
            self.assertNotIn(old_tag, text)

    def test_patch_publisher_is_idempotent_and_recovers_partial_sets(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for token in [
            "id: release_state",
            "already_published=true",
            "partial_release=true",
            "release_target_sha=$released_sha",
            "release_target_sha=$TARGET_SHA",
            "git merge-base --is-ancestor",
            "RELEASE_TARGET_SHA: ${{ steps.release_state.outputs.release_target_sha }}",
            'existing_sha" != "$RELEASE_TARGET_SHA',
            '--target "$RELEASE_TARGET_SHA"',
        ]:
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
