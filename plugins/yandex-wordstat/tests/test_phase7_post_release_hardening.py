import unittest

from scripts import ywstat_topic_map


class TestPhase7PostReleaseHardening(unittest.TestCase):
    def test_candidate_topic_relation_rejects_self_edge(self):
        with self.assertRaises(ValueError):
            ywstat_topic_map.build_topic_map(
                seeds=[{"seed": "seo"}],
                phrase_records=[],
                candidate_topics=[{
                    "topic_id": "t1",
                    "label": "SEO",
                    "query_ids": [],
                    "confidence": "LOW",
                }],
                candidate_relations=[{
                    "from_topic_id": "t1",
                    "to_topic_id": "t1",
                    "relation": "NARROWER",
                    "evidence": [],
                }],
            )

    def test_candidate_topic_relation_allows_distinct_topics(self):
        result = ywstat_topic_map.build_topic_map(
            seeds=[{"seed": "seo"}],
            phrase_records=[],
            candidate_topics=[
                {"topic_id": "t1", "label": "SEO", "query_ids": [], "confidence": "LOW"},
                {"topic_id": "t2", "label": "Technical SEO", "query_ids": [], "confidence": "LOW"},
            ],
            candidate_relations=[{
                "from_topic_id": "t1",
                "to_topic_id": "t2",
                "relation": "RELATED",
                "evidence": [],
            }],
        )
        self.assertEqual(result["candidate_relations"][0]["from_topic_id"], "t1")
        self.assertEqual(result["candidate_relations"][0]["to_topic_id"], "t2")

    def test_duplicate_seed_identifiers_are_rejected(self):
        with self.assertRaises(ValueError):
            ywstat_topic_map.build_topic_map(
                seeds=[
                    {"seed": "seo", "operators": ["exact"]},
                    {"seed": "seo", "operators": ["broad"]},
                ],
                phrase_records=[],
                candidate_topics=[],
            )


if __name__ == "__main__":
    unittest.main()
