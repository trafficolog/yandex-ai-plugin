from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-fable-review5-maintenance.yml"


class FableReview5PublisherErrtraceTests(unittest.TestCase):
    def test_publish_step_enables_errtrace_for_nested_verification_failures(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        publish_step = text.index("- name: Publish immutable maintenance releases")
        verify_step = text.index("- name: Verify complete immutable release set", publish_step)
        segment = text[publish_step:verify_step]

        self.assertIn("set -Eeuo pipefail", segment)
        trap = segment.index("trap 'rc=$?; rollback_published_release \"$tag\" \"$rc\"' ERR")
        publish = segment.index('gh release edit "$tag"', trap)
        verify = segment.index('state="$(gh release view "$tag"', publish)
        self.assertLess(trap, publish)
        self.assertLess(publish, verify)


if __name__ == "__main__":
    unittest.main()
