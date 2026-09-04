import unittest
from unittest.mock import patch

from scripts._approval import preview_id
from scripts.yd_api import YandexDirectClient, YandexDirectError


class DummyOpener:
    pass


class YandexDirectHTTPIntegrationTests(unittest.TestCase):
    def test_client_uses_service_local_adapter_with_timeout_and_opener(self):
        opener = DummyOpener()
        client = YandexDirectClient("token", timeout=17, opener=opener)
        payload = {"result": {"Campaigns": [{"Id": 1}]}}
        transport = {"request_id": "req-1", "units": "1/9/10"}

        with patch("scripts.yd_api._http.request_json", return_value=(payload, transport)) as request_json:
            result = client.request("campaigns", "get", {})

        request_json.assert_called_once_with(
            "https://api.direct.yandex.com/json/v501/campaigns",
            client.headers(),
            {"method": "get", "params": {}},
            timeout=17,
            opener=opener,
        )
        self.assertEqual(result, {"result": payload, "transport": transport})

    def test_api_error_uses_transport_request_id_context(self):
        client = YandexDirectClient("token", opener=DummyOpener())
        payload = {"error": {"error_code": 53, "error_string": "Authorization error"}}
        transport = {"request_id": "req-err"}

        with patch("scripts.yd_api._http.request_json", return_value=(payload, transport)):
            with self.assertRaises(YandexDirectError) as caught:
                client.request("campaigns", "get", {})

        message = str(caught.exception)
        self.assertIn("request_id=req-err", message)
        self.assertNotIn("transport", message)

    def test_exact_approved_write_calls_adapter_once(self):
        opener = DummyOpener()
        client = YandexDirectClient("token", client_login="client", opener=opener)
        params = {"Campaigns": [{"Id": 123}]}
        approve = preview_id(client.approval_envelope("campaigns", "update", params))

        with patch(
            "scripts.yd_api._http.request_json",
            return_value=({"result": {"UpdateResults": []}}, {"request_id": "req-write"}),
        ) as request_json:
            result = client.request("campaigns", "update", params, approve=approve)

        request_json.assert_called_once()
        self.assertEqual(result["transport"]["request_id"], "req-write")


if __name__ == "__main__":
    unittest.main()
