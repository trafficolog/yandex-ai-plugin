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


if __name__ == "__main__":
    unittest.main()
