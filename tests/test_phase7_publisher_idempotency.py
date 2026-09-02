from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-phase-7-topical-architecture.yml"


class Phase7PublisherIdempotencyTests(unittest.TestCase):
    def test_completed_release_set_is_verified_and_becomes_noop(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for token in [
            "Detect immutable Phase 7 release state",
            "id: release_state",
            "already_published=true",
            "git merge-base --is-ancestor",
            "steps.release_state.outputs.already_published != 'true'",
            "steps.release_state.outputs.already_published == 'true'",
            "Phase 7 release set already published; no-op.",
        ]:
            self.assertIn(token, text)

    def test_complete_release_state_checks_all_three_phase7_tags(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for tag in [
            "phase-7-topical-architecture-1.0.0",
            "yandex-wordstat-v1.1.0",
            "yandex-seo-v1.1.0",
        ]:
            self.assertIn(tag, text)
        self.assertIn("release_count", text)
        self.assertIn("release_shas", text)

    def test_partial_release_set_resumes_at_existing_common_sha(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for token in [
            "partial_release=true",
            "release_target_sha=$released_sha",
            "release_target_sha=$TARGET_SHA",
            "RELEASE_TARGET_SHA: ${{ steps.release_state.outputs.release_target_sha }}",
            'existing_sha" != "$RELEASE_TARGET_SHA',
            '--target "$RELEASE_TARGET_SHA"',
        ]:
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
