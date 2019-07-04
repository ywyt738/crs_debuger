import pytest
import requests

from crs_debuger.core import Database


class Test_Api:
    @pytest.fixture
    def db(self):
        return Database(
            "www.faker_crs_server",
            appkey="test_key",
            appsecret="test_secret",
            targeter_host="www.faker_crs_targeter",
        )

    @pytest.mark.parametrize(
        "searcher_url, targeter_url, result", (
            ("api.com", "api.com", True),
            ("searcher.com", "targeter.com", False)),
    )
    def test_searchurl_diff_with_target(self, searcher_url, targeter_url, result):
        """searcher和targeter地址是否相同"""
        _db = Database(
            searcher_host=searcher_url,
            targeter_host=targeter_url,
            appkey="appkey",
            appsecret="secret",
        )
        assert _db.search_api == f"http://{searcher_url}:8080"
        assert _db.target_api == f"http://{targeter_url}:8888"

    def test_add_target(self, monkeypatch, db):
        """新增target"""
        class MockAddTargetResponse:
            status_code = 200

            @staticmethod
            def json():
                return {"statusCode": 0}

        def mock_get(*args, **kwargs):
            return MockAddTargetResponse()

        monkeypatch.setattr(requests, "post", mock_get)

        result = db.add_target("tests/sightplogo.png")
        assert result.status_code == 200
        assert result.json()["statusCode"] == 0

    # TODO: 删除target用例
    @pytest.mark.skip(reason="未完成")
    def test_del_target(self):
        pass

    # TODO: target列表用咧
    @pytest.mark.skip(reason="未完成")
    def test_get_target_list(self):
        pass
