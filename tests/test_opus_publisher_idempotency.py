from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-opus-1.1.1.yml"


class OpusPublisherIdempotencyTests(unittest.TestCase):
    def test_completed_release_set_is_verified_and_becomes_noop(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for token in [
            "Detect immutable OPUS 1.1.1 release state",
            "id: release_state",
            "already_published=true",
            "git merge-base --is-ancestor",
            "steps.release_state.outputs.already_published != 'true'",
            "steps.release_state.outputs.already_published == 'true'",
            "OPUS 1.1.1 release set already published; no-op.",
        ]:
            self.assertIn(token, text)

    def test_complete_release_state_checks_all_three_opus_tags(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for tag in [
            "opus-1.1.1",
            "yandex-metrika-v1.0.2",
            "yandex-webmaster-v1.0.3",
        ]:
            self.assertIn(tag, text)
        self.assertIn("release_count", text)
        self.assertIn("release_shas", text)
        self.assertIn("Existing OPUS 1.1.1 releases point to multiple commits", text)

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
