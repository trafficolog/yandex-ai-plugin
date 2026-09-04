import unittest

from scripts.yd_api import SUPPORTED_SERVICES, YandexDirectClient


OFFICIAL_V5_SERVICES = {
    "adextensions",
    "adgroups",
    "adimages",
    "ads",
    "advideos",
    "agencyclients",
    "audiencetargets",
    "bids",
    "businesses",
    "bidmodifiers",
    "campaigns",
    "changes",
    "clients",
    "creatives",
    "dictionaries",
    "dynamictextadtargets",
    "feeds",
    "keywordbids",
    "keywords",
    "keywordsresearch",
    "leads",
    "negativekeywordsharedsets",
    "retargetinglists",
    "sitelinks",
    "smartadtargets",
    "strategies",
    "turbopages",
    "vcards",
}


class DirectServiceAllowlistTests(unittest.TestCase):
    def test_supported_services_match_verified_v5_inventory(self):
        self.assertEqual(SUPPORTED_SERVICES, OFFICIAL_V5_SERVICES)

    def test_known_services_build_endpoints(self):
        client = YandexDirectClient("token")
        for service in [
            "campaigns",
            "strategies",
            "businesses",
            "keywordsresearch",
            "dynamictextadtargets",
            "smartadtargets",
            "vcards",
        ]:
            with self.subTest(service=service):
                self.assertTrue(client.endpoint(service).endswith(f"/{service}"))

    def test_unknown_or_deceptive_service_names_are_rejected(self):
        client = YandexDirectClient("token")
        for service in [
            "campaigns?x=1",
            "campaigns/../ads",
            "unknown",
            " campaigns ",
            "campaigns%2Fads",
            "",
        ]:
            with self.subTest(service=service):
                with self.assertRaises(ValueError):
                    client.endpoint(service)


if __name__ == "__main__":
    unittest.main()
