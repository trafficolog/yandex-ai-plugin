import unittest

from scripts import ywstat_top


class TestWordstatTop(unittest.TestCase):
    def test_build_top_payload_contract(self):
        payload = ywstat_top.build_top_payload(
            "зубная паста",
            num_phrases=100,
            regions=["225", "213"],
            devices=["DEVICE_DESKTOP", "DEVICE_PHONE"],
            folder_id="folder",
        )
        self.assertEqual(payload["phrase"], "зубная паста")
        self.assertEqual(payload["numPhrases"], 100)
        self.assertEqual(payload["regions"], ["225", "213"])
        self.assertEqual(payload["devices"], ["DEVICE_DESKTOP", "DEVICE_PHONE"])
        self.assertEqual(payload["folderId"], "folder")

    def test_build_top_payload_validates_limits(self):
        with self.assertRaises(ValueError):
            ywstat_top.build_top_payload("")
        with self.assertRaises(ValueError):
            ywstat_top.build_top_payload("x" * 401)
        with self.assertRaises(ValueError):
            ywstat_top.build_top_payload("x", num_phrases=0)
        with self.assertRaises(ValueError):
            ywstat_top.build_top_payload("x", num_phrases=2001)
        with self.assertRaises(ValueError):
            ywstat_top.build_top_payload("x", regions=[str(i) for i in range(101)])
        with self.assertRaises(ValueError):
            ywstat_top.build_top_payload("x", devices=["DEVICE_ALL"] * 4)
        with self.assertRaises(ValueError):
            ywstat_top.build_top_payload("x", devices=["DEVICE_TV"])

    def test_normalize_keeps_results_and_associations_distinct(self):
        response = {
            "totalCount": "1500",
            "results": [
                {"phrase": "зубная паста купить", "count": "500"},
                {"phrase": "зубная паста", "count": "1000"},
            ],
            "associations": [
                {"phrase": "ирригатор", "count": "200"},
            ],
        }
        normalized = ywstat_top.normalize_top_response(response, seed="зубная паста")
        self.assertEqual(normalized["total_count"], 1500)
        self.assertEqual(normalized["results"][0]["relation"], "nested")
        self.assertEqual(normalized["associations"][0]["relation"], "association")
        self.assertEqual(normalized["results"][0]["count"], 500)
        self.assertEqual(normalized["results"][0]["sources"], ["зубная паста"])
        self.assertEqual(len(normalized["records"]), 3)

    def test_association_coverage_marks_exact_cap_as_truncated(self):
        response = {
            "totalCount": "100",
            "results": [],
            "associations": [
                {"phrase": f"association {index}", "count": str(index + 1)}
                for index in range(20)
            ],
        }
        normalized = ywstat_top.normalize_top_response(response, seed="seed")
        self.assertEqual(ywstat_top.MAX_ASSOCIATIONS, 20)
        self.assertEqual(normalized["coverage"], {
            "associations_cap": 20,
            "associations_count": 20,
            "associations_truncated": True,
        })
        self.assertTrue(all(row["relation"] == "association" for row in normalized["associations"]))

    def test_association_coverage_below_cap_is_not_truncated(self):
        response = {
            "totalCount": "100",
            "results": [],
            "associations": [
                {"phrase": f"association {index}", "count": str(index + 1)}
                for index in range(5)
            ],
        }
        normalized = ywstat_top.normalize_top_response(response, seed="seed")
        self.assertEqual(normalized["coverage"], {
            "associations_cap": 20,
            "associations_count": 5,
            "associations_truncated": False,
        })

    def test_operator_expression_is_preserved(self):
        normalized = ywstat_top.normalize_top_response(
            {"totalCount": "2", "results": [{"phrase": "купить собаку", "count": "2"}]},
            seed="купить !собаку",
            operator_expression="купить !собаку",
        )
        self.assertEqual(normalized["results"][0]["operator_expression"], "купить !собаку")


if __name__ == "__main__":
    unittest.main()
