from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-fable-review5-maintenance.yml"


class FableReview5PublisherProbeSafetyTests(unittest.TestCase):
    def test_tag_absence_requires_ls_remote_status_2(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("remote_tag_exists() {", text)
        self.assertIn('git ls-remote --exit-code origin "refs/tags/$tag"', text)
        self.assertIn('case "$rc" in', text)
        self.assertIn('0) return 0', text)
        self.assertIn('2) return 1', text)
        self.assertIn('Unable to determine remote tag state for $tag', text)

    def test_publisher_does_not_use_boolean_ls_remote_as_absence_proof(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn('if ! git ls-remote --exit-code origin "refs/tags/$tag"', text)
        self.assertNotIn('if git ls-remote --exit-code origin "refs/tags/$tag" >/dev/null 2>&1; then\n              printf \'present\\n\'', text)


if __name__ == "__main__":
    unittest.main()
