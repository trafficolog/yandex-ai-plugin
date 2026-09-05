from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-current-release.yml"
CANONICAL_REPOSITORY = "trafficolog/yandex-ai-plugins-skills"


class PublisherRepositoryIdentityTests(unittest.TestCase):
    def test_current_publisher_uses_canonical_repository_identity(self):
        self.assertTrue(WORKFLOW.is_file(), "generic release publisher is missing")
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            f"github.repository == '{CANONICAL_REPOSITORY}'",
            text,
        )
        self.assertIn(f"GH_REPO: {CANONICAL_REPOSITORY}", text)
        self.assertIn("github.event.workflow_run.head_repository.full_name == github.repository", text)


if __name__ == "__main__":
    unittest.main()
