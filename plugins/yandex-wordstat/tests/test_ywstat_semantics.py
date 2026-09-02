import unittest

from scripts import ywstat_semantics


class TestWordstatSemantics(unittest.TestCase):
    def test_merge_preserves_all_provenance_and_relations(self):
        records = [
            {"phrase":"ирригатор", "count":100, "relation":"association", "sources":["щетка"], "operator_expression":None},
            {"phrase":"ирригатор", "count":120, "relation":"nested", "sources":["ирригатор купить"], "operator_expression":None},
            {"phrase":"ирригатор", "count":110, "relation":"association", "sources":["уход за зубами"], "operator_expression":"ирригатор"},
        ]
        merged = ywstat_semantics.merge_records(records)
        self.assertEqual(len(merged), 1)
        item = merged[0]
        self.assertEqual(item["count"], 120)
        self.assertEqual(item["relations"], ["association", "nested"])
        self.assertEqual(item["sources"], ["ирригатор купить", "уход за зубами", "щетка"])
        self.assertEqual(item["operator_expressions"], ["ирригатор"])

    def test_dataset_keeps_total_counts_per_seed_without_sum(self):
        seed_results = [
            {
                "seed":"a", "total_count":1000,
                "records":[{"phrase":"x","count":100,"relation":"nested","sources":["a"],"operator_expression":None}],
            },
            {
                "seed":"b", "total_count":900,
                "records":[{"phrase":"x","count":120,"relation":"association","sources":["b"],"operator_expression":None}],
            },
        ]
        dataset = ywstat_semantics.build_dataset(seed_results)
        self.assertEqual(dataset["total_counts"], {"a": 1000, "b": 900})
        self.assertEqual(dataset["meta"]["unique_phrases"], 1)
        self.assertNotIn("total_demand", dataset)
        self.assertNotIn("sum_counts", dataset)
        self.assertEqual(dataset["phrases"][0]["sources"], ["a", "b"])

    def test_fake_total_demand_labels_are_rejected(self):
        for label in ["total demand", "market size", "unique searches", "суммарный спрос", "размер рынка", "уникальные запросы"]:
            with self.assertRaises(ValueError, msg=label):
                ywstat_semantics.assert_no_fake_total_demand(label)
        ywstat_semantics.assert_no_fake_total_demand("sum of returned row counts for debugging")


if __name__ == "__main__":
    unittest.main()
