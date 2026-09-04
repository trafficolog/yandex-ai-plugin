from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-fable-review5-maintenance.yml"


class FableReview5PublisherRollbackArmTests(unittest.TestCase):
    def test_rollback_is_armed_before_draft_publication(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        publish_start = text.index("publish_one() {")
        publish_end = text.index("- name: Verify complete immutable release set", publish_start)
        function = text[publish_start:publish_end]

        trap = function.index("trap 'rc=$?; rollback_published_release \"$tag\" \"$rc\"' ERR")
        publish = function.index('gh release edit "$tag"', trap)
        verify = function.index('state="$(gh release view "$tag"', publish)
        clear_trap = function.index("trap - ERR", verify)

        self.assertLess(trap, publish)
        self.assertLess(publish, verify)
        self.assertLess(verify, clear_trap)


if __name__ == "__main__":
    unittest.main()
