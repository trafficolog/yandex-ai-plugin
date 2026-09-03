from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-opus-1.1.3.yml"


class Opus113PublisherResidueTests(unittest.TestCase):
    def test_rollback_distinguishes_confirmed_absence_from_probe_failure(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        start = text.index("cleanup_published_release() {")
        end = text.index("            if release_state=", start)
        cleanup = text[start:end]

        for token in (
            'release_probe_status=0',
            'release_probe_output="$(gh api --include "repos/$GITHUB_REPOSITORY/releases/tags/$tag" 2>&1)" || release_probe_status=$?',
            'release_http_status=',
            'if [[ "$release_http_status" == "404" ]]',
            'Rollback verification failed: unable to verify release $tag absence.',
            'tag_probe_status=0',
            'git ls-remote --exit-code origin "refs/tags/$tag" >/dev/null 2>&1 || tag_probe_status=$?',
            'elif [[ "$tag_probe_status" -eq 2 ]]',
            'Rollback verification failed: unable to verify tag $tag absence.',
        ):
            self.assertIn(token, cleanup)

        self.assertNotIn(
            'if gh release view "$tag" --repo "$GITHUB_REPOSITORY" >/dev/null 2>&1; then',
            cleanup,
        )
        self.assertNotIn(
            'if git ls-remote --exit-code origin "refs/tags/$tag" >/dev/null 2>&1; then',
            cleanup,
        )


if __name__ == "__main__":
    unittest.main()
