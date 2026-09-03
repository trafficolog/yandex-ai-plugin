from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-repository-1.0.2.yml"


class Repository102PublisherTests(unittest.TestCase):
    def test_publisher_targets_only_repository_release_1_0_2(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('gh release create "1.0.2"', text)
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

    def test_existing_release_is_verified_and_suppresses_publication(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for token in [
            "Detect immutable repository 1.0.2 release state",
            "id: release_state",
            'git show-ref --verify --quiet "refs/tags/$tag"',
            'released_sha="$(git rev-list -n 1 "$tag")"',
            'git merge-base --is-ancestor "$released_sha" "$TARGET_SHA"',
            "already_published=true",
            "steps.release_state.outputs.already_published == 'true'",
            "steps.release_state.outputs.already_published != 'true'",
            "Repository release 1.0.2 already published; no-op.",
            "Publish repository release",
        ]:
            self.assertIn(token, text)

    def test_release_contract_checks_every_plugin_manifest_and_expected_version(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "plugins/yandex-direct/.codex-plugin/plugin.json": "1.0.1",
            "plugins/yandex-metrika/.codex-plugin/plugin.json": "1.0.2",
            "plugins/yandex-webmaster/.codex-plugin/plugin.json": "1.0.3",
            "plugins/yandex-wordstat/.codex-plugin/plugin.json": "1.1.1",
            "plugins/yandex-search/.codex-plugin/plugin.json": "1.0.2",
            "plugins/yandex-seo/.codex-plugin/plugin.json": "1.1.1",
            "plugins/yandex-marketing/.codex-plugin/plugin.json": "1.1.0",
        }
        for path, version in expected.items():
            self.assertIn(
                f"grep -F '\"version\": \"{version}\"' {path}",
                text,
            )
        self.assertIn("## [1.0.2] — 2026-09-03", text)
        self.assertIn('--target "$TARGET_SHA"', text)


if __name__ == "__main__":
    unittest.main()
