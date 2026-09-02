import unittest

from scripts import ywstat_regions


class TestWordstatRegions(unittest.TestCase):
    def test_build_regions_payload(self):
        payload = ywstat_regions.build_regions_payload(
            "зубная паста", region="REGION_CITIES", devices=["DEVICE_PHONE"], folder_id="folder"
        )
        self.assertEqual(payload, {
            "phrase":"зубная паста", "region":"REGION_CITIES",
            "devices":["DEVICE_PHONE"], "folderId":"folder"
        })
        with self.assertRaises(ValueError):
            ywstat_regions.build_regions_payload("x", region="CITY")

    def test_normalize_regions(self):
        rows = ywstat_regions.normalize_regions({
            "results": [
                {"region":"213", "count":"80000", "share":"0.012", "affinityIndex":"92"},
                {"region":"55", "count":"10000", "share":"0.021", "affinityIndex":"165"},
            ]
        })
        self.assertEqual(rows[0]["region_id"], "213")
        self.assertEqual(rows[0]["count"], 80000)
        self.assertAlmostEqual(rows[1]["affinity_index"], 165.0)

    def test_flatten_and_search_region_tree(self):
        response = {
            "regions": [
                {"id":"225", "label":"Россия", "children":[
                    {"id":"213", "label":"Москва", "children":[]},
                    {"id":"2", "label":"Санкт-Петербург", "children":[]},
                ]},
                {"id":"149", "label":"Беларусь", "children":[]},
            ]
        }
        flat = ywstat_regions.flatten_region_tree(response)
        self.assertEqual(len(flat), 4)
        moscow = next(item for item in flat if item["id"] == "213")
        self.assertEqual(moscow["parent_id"], "225")
        self.assertEqual(moscow["path"], ["Россия", "Москва"])
        matches = ywstat_regions.search_regions(response, "моск")
        self.assertEqual([item["id"] for item in matches], ["213"])

    def test_rank_by_volume_and_affinity_are_different(self):
        records = [
            {"region_id":"213", "count":80000, "share":0.012, "affinity_index":92.0},
            {"region_id":"55", "count":10000, "share":0.021, "affinity_index":165.0},
        ]
        self.assertEqual(ywstat_regions.rank_regions(records, by="volume")[0]["region_id"], "213")
        self.assertEqual(ywstat_regions.rank_regions(records, by="affinity")[0]["region_id"], "55")
        with self.assertRaises(ValueError):
            ywstat_regions.rank_regions(records, by="unknown")


if __name__ == "__main__":
    unittest.main()
