from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
USES = re.compile(r"^\s*-\s+uses:\s*([^\s#]+)")


class GitHubActionsSupplyChainTests(unittest.TestCase):
    def test_external_actions_are_pinned_to_full_commit_sha(self):
        violations: list[str] = []
        for workflow in sorted(WORKFLOWS.glob("*.yml")):
            for line_no, line in enumerate(workflow.read_text(encoding="utf-8").splitlines(), 1):
                match = USES.match(line)
                if not match:
                    continue
                target = match.group(1)
                if target.startswith("./"):
                    continue
                if "@" not in target:
                    violations.append(f"{workflow.relative_to(ROOT)}:{line_no}: {target}")
                    continue
                _, ref = target.rsplit("@", 1)
                if not FULL_SHA.fullmatch(ref):
                    violations.append(f"{workflow.relative_to(ROOT)}:{line_no}: {target}")
        self.assertEqual([], violations, "mutable or non-SHA action refs:\n" + "\n".join(violations))

    def test_dependabot_updates_github_actions(self):
        config = ROOT / ".github" / "dependabot.yml"
        self.assertTrue(config.is_file(), ".github/dependabot.yml is required")
        text = config.read_text(encoding="utf-8")
        self.assertIn('package-ecosystem: "github-actions"', text)
        self.assertIn('directory: "/"', text)
        self.assertIn('interval: "weekly"', text)


if __name__ == "__main__":
    unittest.main()
