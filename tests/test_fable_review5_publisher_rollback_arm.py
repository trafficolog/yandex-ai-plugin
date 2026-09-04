from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-fable-review5-maintenance.yml"


class FableReview5PublisherRollbackArmTests(unittest.TestCase):
    def test_rollback_is_armed_before_draft_publication(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        publish_start = text.index("publish_one() {")
        publish_end = text.index("direct_notes=", publish_start)
        function = text[publish_start:publish_end]

        cleanup = function.index("cleanup_publish_failure() {")
        armed = function.index("rollback_armed=true", cleanup)
        trap = function.index("trap cleanup_publish_failure ERR", armed)
        publish = function.index('gh release edit "$tag"', trap)
        verify = function.index('verify_published_release "$tag"', publish)
        disarm = function.index("rollback_armed=false", verify)
        clear_trap = function.index("trap - ERR", disarm)

        self.assertLess(cleanup, armed)
        self.assertLess(armed, trap)
        self.assertLess(trap, publish)
        self.assertLess(publish, verify)
        self.assertLess(verify, disarm)
        self.assertLess(disarm, clear_trap)
        self.assertIn('rollback_published_release "$tag"', function[cleanup:publish])


if __name__ == "__main__":
    unittest.main()
