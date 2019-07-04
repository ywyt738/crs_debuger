import datetime
from json.decoder import JSONDecodeError

import pytest
import requests

from crs_debuger.response import SearchResponse, TargetListResponse


class Test_Response_Class:
    def test_base_response_json(self):
        class MockResponse:
            status_code = 200

            def json(self):
                return {"msg": "OK"}

            @property
            def elapsed(self):
                return datetime.timedelta(microseconds=12345)

        _r = MockResponse()
        r = SearchResponse(_r)
        assert r.json() == {"msg": "OK"}
        assert r.elapsed == datetime.timedelta(microseconds=12345)

    def test_search_success_response(self, requests_mock):
        requests_mock.post(
            "http://fake-api.com",
            json={
                "statusCode": 0,
                "result": {"target": {"targetId": "11111-11111-11111-11111"}},
            },
        )
        response = SearchResponse(requests.post("http://fake-api.com"))
        assert response.ok is True
        assert response.target_id == "11111-11111-11111-11111"

    def test_search_fail_response(self, requests_mock):
        requests_mock.post("http://fake-api.com", status_code=500, json=None)
        response = SearchResponse(requests.post("http://fake-api.com"))
        with pytest.raises(JSONDecodeError):
            assert response.ok is False
            assert response.target_id == "Not Recognized"

    def test_target_list_response(self, requests_mock):
        requests_mock.post(
            "http://fake-api.com",
            json={
                "result": {
                    "targets": [
                        {
                            "active": 1,
                            "created": 1562144001530,
                            "modified": 1562144001530,
                            "name": "pic1",
                            "size": 10,
                            "systemMeta": None,
                            "targetId": "12345-12345-12345",
                            "trackingImage": "http://pic.com/pic1",
                        },
                        {
                            "active": 1,
                            "created": 1562144001530,
                            "modified": 1562144001530,
                            "name": "pic2",
                            "size": 15,
                            "systemMeta": "meta msg",
                            "targetId": "22345-22345-22345",
                            "trackingImage": "http://pic.com/pic2",
                        },
                        {
                            "active": 1,
                            "created": 1562144001530,
                            "modified": 1562144001530,
                            "name": "pic3",
                            "size": 20,
                            "systemMeta": None,
                            "targetId": "32345-32345-32345",
                            "trackingImage": "http://pic.com/pic3",
                        },
                    ]
                }
            },
        )
        response = TargetListResponse(requests.post("http://fake-api.com"))
        assert len(response) == 3
        for target in response:
            assert target.name in ["pic1", "pic2", "pic3"]
