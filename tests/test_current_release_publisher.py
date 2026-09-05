from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-current-release.yml"


class CurrentReleasePublisherTests(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""

    def test_trigger_is_successful_canonical_main_ci_only(self):
        for token in (
            'workflows: ["CI"]',
            "github.event.workflow_run.conclusion == 'success'",
            "github.event.workflow_run.event == 'push'",
            "github.event.workflow_run.head_repository.full_name == github.repository",
            "github.event.workflow_run.head_branch == 'main'",
            "github.repository == 'trafficolog/yandex-ai-plugins-skills'",
        ):
            self.assertIn(token, self.text)

    def test_checkout_is_exact_upstream_ci_sha(self):
        self.assertIn("TARGET_SHA: ${{ github.event.workflow_run.head_sha }}", self.text)
        self.assertIn("ref: ${{ env.TARGET_SHA }}", self.text)
        self.assertIn("fetch-depth: 0", self.text)

    def test_manifest_is_validated_before_remote_release_mutation(self):
        validate_i = self.text.find("python scripts/release_manifest.py validate")
        create_i = self.text.find("gh release create")
        self.assertGreaterEqual(validate_i, 0)
        self.assertGreaterEqual(create_i, 0)
        self.assertLess(validate_i, create_i)
        self.assertIn("python scripts/release_manifest.py items --format tsv", self.text)

    def test_initial_stale_main_run_is_verified_noop(self):
        self.assertIn('if [[ "$live_main" != "$TARGET_SHA" ]]', self.text)
        self.assertIn("stale=true", self.text)
        self.assertIn("Stale successful main CI run; no publication required.", self.text)
        self.assertIn("steps.state.outputs.stale != 'true'", self.text)

    def test_recovery_requires_one_common_ancestor_target(self):
        self.assertIn("Existing declared release state spans multiple commits", self.text)
        self.assertIn('git merge-base --is-ancestor "$release_target" "$live_main"', self.text)
        self.assertIn("is not an ancestor of live main", self.text)

    def test_remote_tag_probe_distinguishes_absence_from_probe_failure(self):
        self.assertIn("git ls-remote --exit-code origin", self.text)
        self.assertIn("0) return 0", self.text)
        self.assertIn("2) return 1", self.text)
        self.assertIn("Unable to determine remote tag state", self.text)

    def test_published_mutable_release_is_rejected(self):
        self.assertIn("Published release $tag is not immutable.", self.text)

    def test_standalone_tag_without_release_is_rejected(self):
        self.assertIn("Standalone remote tag $tag exists without a GitHub Release.", self.text)

    def test_draft_reservation_precedes_publication(self):
        draft_i = self.text.find('gh release create "$tag"')
        publish_i = self.text.find('gh release edit "$tag"')
        self.assertGreaterEqual(draft_i, 0)
        self.assertGreaterEqual(publish_i, 0)
        self.assertLess(draft_i, publish_i)
        self.assertIn('--draft --target "$RELEASE_TARGET"', self.text)
        self.assertIn("Draft reservation $tag unexpectedly materialized a tag.", self.text)

    def test_publish_step_enables_errtrace(self):
        self.assertIn("set -Eeuo pipefail", self.text)

    def test_rollback_is_armed_only_before_mutable_publication(self):
        arm_i = self.text.find("rollback_armed=true")
        trap_i = self.text.find("trap 'rc=$?; rollback_published_release")
        publish_i = self.text.find('gh release edit "$tag"')
        self.assertGreaterEqual(arm_i, 0)
        self.assertGreaterEqual(trap_i, 0)
        self.assertGreaterEqual(publish_i, 0)
        self.assertLess(arm_i, trap_i)
        self.assertLess(trap_i, publish_i)

    def test_rollback_rechecks_immutability_before_delete(self):
        probe_i = self.text.find('cleanup_release_immutable="$(gh release view')
        delete_i = self.text.find('gh release delete "$tag"')
        self.assertGreaterEqual(probe_i, 0)
        self.assertGreaterEqual(delete_i, 0)
        self.assertLess(probe_i, delete_i)
        self.assertIn("already immutable; rollback is neither required nor safe", self.text)

    def test_rollback_checks_release_and_tag_residue(self):
        self.assertIn("Rollback residue: release $tag remains.", self.text)
        self.assertIn("Rollback residue: tag $tag remains.", self.text)
        self.assertIn("Rollback verification could not determine tag state", self.text)

    def test_rollback_is_disarmed_before_post_immutability_tag_probe(self):
        immutable_i = self.text.find('[[ "$published_is_immutable" == "true" ]]')
        self.assertGreaterEqual(immutable_i, 0)
        disarm_i = self.text.find("rollback_armed=false", immutable_i)
        trap_i = self.text.find("trap - ERR", disarm_i)
        fetch_i = self.text.find('git fetch origin "refs/tags/$tag:refs/tags/$tag"', trap_i)
        self.assertGreaterEqual(disarm_i, 0)
        self.assertGreaterEqual(trap_i, 0)
        self.assertGreaterEqual(fetch_i, 0)
        self.assertLess(immutable_i, disarm_i)
        self.assertLess(disarm_i, trap_i)
        self.assertLess(trap_i, fetch_i)

    def test_final_verification_checks_every_declared_item(self):
        self.assertIn("Verify complete immutable release set", self.text)
        self.assertIn("while IFS=$'\\t' read -r kind name version tag title notes_file", self.text)
        self.assertIn("Final verification: release $tag is not immutable.", self.text)
        self.assertIn("Final verification: tag $tag points to", self.text)

    def test_repository_only_manifest_cannot_hardcode_plugin_publication(self):
        self.assertNotRegex(self.text, re.compile(r'publish_one\s+"yandex-[^"]+"'))
        self.assertIn("release_manifest.py items --format tsv", self.text)

    def test_concurrency_serializes_without_cancellation(self):
        self.assertIn("group: current-release-publisher", self.text)
        self.assertIn("cancel-in-progress: false", self.text)


if __name__ == "__main__":
    unittest.main()
