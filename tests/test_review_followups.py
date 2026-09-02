import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReviewFollowupTraceabilityTests(unittest.TestCase):
    def test_review_blocker_contracts_are_traceable(self):
        matrix = json.loads((ROOT / "docs/CONTRACT_MATRIX.json").read_text(encoding="utf-8"))
        ids = {contract["id"] for contract in matrix["contracts"]}
        required = {
            "direct.preview-before-write",
            "metrika.direct-expense-duplication-guard",
            "webmaster.feed-batch-safety",
            "webmaster.indexing-archive-lifecycle",
            "seo.evidence-period-geo-semantics",
            "seo.webmaster-impressions-unknown",
            "marketing.quality-metadata-shape",
        }
        self.assertEqual(required - ids, set())


if __name__ == "__main__":
    unittest.main()
