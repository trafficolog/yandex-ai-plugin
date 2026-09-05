from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github/workflows"


class PublisherMigrationContractTests(unittest.TestCase):
    def test_exactly_one_active_publish_workflow_exists(self):
        publishers = sorted(path.name for path in WORKFLOWS.glob("publish-*.yml"))
        self.assertEqual(publishers, ["publish-current-release.yml"])

    def test_historical_publish_names_are_absent_from_current_tip(self):
        names = "\n".join(path.name.lower() for path in WORKFLOWS.glob("publish-*.yml"))
        for token in ("opus", "fable", "phase", "docs", "1.0.2", "1.0.5"):
            self.assertNotIn(token, names)


if __name__ == "__main__":
    unittest.main()
