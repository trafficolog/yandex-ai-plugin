import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
CANONICAL_REPOSITORY = "trafficolog/yandex-ai-plugins-skills"
REPOSITORY_GUARD = re.compile(r"github\.repository\s*==\s*['\"]([^'\"]+)['\"]")


class PublisherRepositoryIdentityTests(unittest.TestCase):
    def test_all_literal_publish_repository_guards_use_canonical_repository(self):
        mismatches = []
        guards = []
        for path in sorted(WORKFLOWS.glob("publish-*.yml")):
            text = path.read_text(encoding="utf-8")
            for match in REPOSITORY_GUARD.finditer(text):
                repository = match.group(1)
                guards.append((path.name, repository))
                if repository != CANONICAL_REPOSITORY:
                    mismatches.append((path.name, repository))
        self.assertTrue(guards, "expected at least one explicit publisher repository guard")
        self.assertEqual(mismatches, [])


if __name__ == "__main__":
    unittest.main()
