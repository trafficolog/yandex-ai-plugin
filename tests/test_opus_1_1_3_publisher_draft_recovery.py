from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-opus-1.1.3.yml"


class Opus113PublisherDraftRecoveryTests(unittest.TestCase):
    def test_draft_targets_participate_in_recovery_consensus(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        detect = text[text.index('id: release_state'):text.index('- name: Report already-published release set')]

        for token in (
            'draft_target_shas=()',
            'draft_target_shas+=("$release_target_commitish")',
            'recovery_shas=("${immutable_shas[@]}" "${draft_target_shas[@]}")',
            'if [[ "${#recovery_shas[@]}" -eq 0 ]]',
            'immutable_sha="${recovery_shas[0]}"',
            'for sha in "${recovery_shas[@]}"',
            'release_target_sha=$immutable_sha',
        ):
            self.assertIn(token, detect)

        self.assertIn('git merge-base --is-ancestor "$immutable_sha" "$live_main_sha"', detect)


if __name__ == "__main__":
    unittest.main()
