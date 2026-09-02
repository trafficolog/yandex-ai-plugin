import unittest

from scripts import ywstat_topic_map


class TestWordstatTopicMap(unittest.TestCase):
    def test_preserves_provenance_without_summing_overlapping_demand(self):
        result = ywstat_topic_map.build_topic_map(
            seeds=[
                {"seed": "seo", "operators": "", "filters": {}, "coverage": {"associations_truncated": True}},
                {"seed": "аудит сайта", "operators": "", "filters": {}, "coverage": {}},
            ],
            phrase_records=[
                {
                    "query_id": "q1",
                    "text": "SEO аудит",
                    "source_seed": "seo",
                    "relation": "nested",
                    "demand": {"count": 100, "period": "2026-08"},
                },
                {
                    "query_id": "q2",
                    "text": " seo   аудит ",
                    "source_seed": "аудит сайта",
                    "relation": "association",
                    "demand": {"count": 80, "period": "2026-08"},
                },
            ],
            candidate_topics=[
                {
                    "topic_id": "audit",
                    "label": "SEO-аудит",
                    "query_ids": ["q1", "q2"],
                    "candidate_intents": ["informational"],
                    "reasons": ["WORDSTAT_NESTED_RELATION"],
                    "confidence": "MEDIUM",
                }
            ],
        )

        self.assertEqual(result["schema"], "wordstat-topic-map/v1")
        self.assertEqual(len(result["queries"]), 1)
        query = result["queries"][0]
        self.assertEqual(query["query_ids"], ["q1", "q2"])
        self.assertEqual(set(query["source_seeds"]), {"seo", "аудит сайта"})
        self.assertEqual(set(query["relations"]), {"nested", "association"})
        self.assertEqual(len(query["demand_observations"]), 2)
        self.assertNotIn("total_demand", query)
        self.assertNotIn("sum_counts", query)
        self.assertIn("WORDSTAT_ASSOCIATIONS_CAPPED", result["limitations"])
        self.assertEqual(result["candidate_topics"][0]["status"], "CANDIDATE")
        self.assertNotIn("page", result["candidate_topics"][0])
        self.assertNotIn("canonical_parent", result["candidate_topics"][0])
        self.assertNotIn("internal_link", result["candidate_topics"][0])

    def test_duplicate_query_id_must_resolve_to_same_normalized_query(self):
        seeds = [{"seed": "seo", "operators": "", "filters": {}, "coverage": {}}]
        with self.assertRaises(ValueError):
            ywstat_topic_map.build_topic_map(
                seeds=seeds,
                phrase_records=[
                    {"query_id": "q1", "text": "seo", "source_seed": "seo", "relation": "nested", "demand": None},
                    {"query_id": "q1", "text": "seo аудит", "source_seed": "seo", "relation": "association", "demand": None},
                ],
                candidate_topics=[],
            )

        result = ywstat_topic_map.build_topic_map(
            seeds=seeds,
            phrase_records=[
                {"query_id": "q1", "text": "SEO аудит", "source_seed": "seo", "relation": "nested", "demand": None},
                {"query_id": "q1", "text": " seo   аудит ", "source_seed": "seo", "relation": "association", "demand": None},
            ],
            candidate_topics=[],
        )
        self.assertEqual(len(result["queries"]), 1)
        self.assertEqual(result["queries"][0]["query_id"], "q1")

    def test_unknown_query_reference_is_rejected(self):
        with self.assertRaises(ValueError):
            ywstat_topic_map.build_topic_map(
                seeds=[{"seed": "seo", "operators": "", "filters": {}, "coverage": {}}],
                phrase_records=[
                    {"query_id": "q1", "text": "seo", "source_seed": "seo", "relation": "nested", "demand": None}
                ],
                candidate_topics=[
                    {
                        "topic_id": "bad",
                        "label": "Bad",
                        "query_ids": ["missing"],
                        "candidate_intents": [],
                        "reasons": [],
                        "confidence": "LOW",
                    }
                ],
            )

    def test_candidate_relation_requires_known_topics_and_is_hypothesis(self):
        result = ywstat_topic_map.build_topic_map(
            seeds=[{"seed": "seo", "operators": "", "filters": {}, "coverage": {}}],
            phrase_records=[
                {"query_id": "q1", "text": "seo", "source_seed": "seo", "relation": "nested", "demand": None},
                {"query_id": "q2", "text": "seo аудит", "source_seed": "seo", "relation": "association", "demand": None},
            ],
            candidate_topics=[
                {"topic_id": "root", "label": "SEO", "query_ids": ["q1"], "candidate_intents": [], "reasons": [], "confidence": "MEDIUM"},
                {"topic_id": "audit", "label": "SEO-аудит", "query_ids": ["q2"], "candidate_intents": [], "reasons": [], "confidence": "MEDIUM"},
            ],
            candidate_relations=[
                {"from_topic_id": "root", "to_topic_id": "audit", "relation": "NARROWER", "evidence": ["WORDSTAT_ASSOCIATION"]}
            ],
        )
        self.assertEqual(result["candidate_relations"][0]["status"], "HYPOTHESIS")

        with self.assertRaises(ValueError):
            ywstat_topic_map.build_topic_map(
                seeds=[{"seed": "seo", "operators": "", "filters": {}, "coverage": {}}],
                phrase_records=[
                    {"query_id": "q1", "text": "seo", "source_seed": "seo", "relation": "nested", "demand": None}
                ],
                candidate_topics=[
                    {"topic_id": "root", "label": "SEO", "query_ids": ["q1"], "candidate_intents": [], "reasons": [], "confidence": "LOW"}
                ],
                candidate_relations=[
                    {"from_topic_id": "root", "to_topic_id": "missing", "relation": "RELATED", "evidence": []}
                ],
            )

    def test_invalid_confidence_or_relation_is_rejected(self):
        base = {
            "seeds": [{"seed": "seo", "operators": "", "filters": {}, "coverage": {}}],
            "phrase_records": [
                {"query_id": "q1", "text": "seo", "source_seed": "seo", "relation": "nested", "demand": None}
            ],
        }
        with self.assertRaises(ValueError):
            ywstat_topic_map.build_topic_map(
                **base,
                candidate_topics=[
                    {"topic_id": "root", "label": "SEO", "query_ids": ["q1"], "candidate_intents": [], "reasons": [], "confidence": "0.91"}
                ],
            )
        with self.assertRaises(ValueError):
            ywstat_topic_map.build_topic_map(
                **base,
                candidate_topics=[
                    {"topic_id": "root", "label": "SEO", "query_ids": ["q1"], "candidate_intents": [], "reasons": [], "confidence": "LOW"}
                ],
                candidate_relations=[
                    {"from_topic_id": "root", "to_topic_id": "root", "relation": "PAGE_CHILD", "evidence": []}
                ],
            )


if __name__ == "__main__":
    unittest.main()
