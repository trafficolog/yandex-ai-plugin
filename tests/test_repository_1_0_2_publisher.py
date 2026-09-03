from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-repository-1.0.2.yml"


class Repository102PublisherTests(unittest.TestCase):
    def test_publisher_targets_only_repository_release_1_0_2(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"1.0.2"', text)
        for forbidden in [
            "yandex-direct-v",
            "yandex-metrika-v",
            "yandex-webmaster-v",
            "yandex-wordstat-v",
            "yandex-search-v",
            "yandex-seo-v",
            "yandex-marketing-v",
        ]:
            self.assertNotIn(forbidden, text)

    def test_publisher_is_main_ci_gated_and_exact_sha(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for token in [
            'workflows: ["CI"]',
            "github.event.workflow_run.conclusion == 'success'",
            "github.event.workflow_run.event == 'push'",
            "github.event.workflow_run.head_repository.full_name == github.repository",
            "github.event.workflow_run.head_branch == 'main'",
            "TARGET_SHA: ${{ github.event.workflow_run.head_sha }}",
            'test "$(git rev-parse HEAD)" = "$TARGET_SHA"',
        ]:
            self.assertIn(token, text)

    def test_release_contract_is_idempotent_and_version_matrix_stays_unchanged(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for token in [
            "Detect immutable repository 1.0.2 release state",
            "already_published=true",
            "Repository release 1.0.2 already published; no-op.",
            '"version": "1.0.1"',
            '"version": "1.0.2"',
            '"version": "1.0.3"',
            '"version": "1.1.1"',
            '"version": "1.1.0"',
            "## [1.0.2] — 2026-09-03",
            '--target "$TARGET_SHA"',
        ]:
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
