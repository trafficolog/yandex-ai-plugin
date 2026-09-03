import unittest

from scripts import ywstat_topic_map


class TopicMapNormalizationTests(unittest.TestCase):
    def test_nfkc_compatibility_forms_share_one_query_key(self):
        self.assertEqual(ywstat_topic_map._normalize_text("Ｋупить пасту"), "kупить пасту")
        self.assertEqual(ywstat_topic_map._normalize_text("ｐａｓｔａ"), "pasta")

    def test_nfkc_variants_merge_into_one_topic_map_query(self):
        result = ywstat_topic_map.build_topic_map(
            seeds=[{"seed": "pasta", "operators": "", "filters": {}, "coverage": {}}],
            phrase_records=[
                {"query_id": "q1", "text": "ｐａｓｔａ", "source_seed": "pasta", "relation": "nested", "demand": None},
                {"query_id": "q2", "text": "pasta", "source_seed": "pasta", "relation": "association", "demand": None},
            ],
            candidate_topics=[],
        )
        self.assertEqual(len(result["queries"]), 1)
        self.assertEqual(result["queries"][0]["normalized_query"], "pasta")


if __name__ == "__main__":
    unittest.main()
