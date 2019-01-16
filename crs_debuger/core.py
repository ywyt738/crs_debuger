import base64
import datetime
import functools
import hashlib
import pathlib

import requests
from requests.exceptions import InvalidSchema
from urllib3.util import parse_url


class Database:
    def __init__(
        self, host, appkey, appsecret, search_port=8080, target_port=8888, timeout=None
    ):
        self.appkey = appkey
        self.appsecret = appsecret
        self.timeout = timeout
        self._prepare_api_url(host, search_port, target_port)

    def _prepare_api_url(self, url, search_port, target_port):
        scheme, auth, host, port, path, query, fragment = parse_url(url)
        if scheme is None or scheme == "http":
            self.search_api = f"http://{host}:{search_port}"
            self.target_api = f"http://{host}:{target_port}"
        else:
            raise InvalidSchema("Invalid scheme %r: Do not supply" % scheme)

    def generate_signature(self, data=None):
        if data is None:
            data = {}
        # 追加timestamp和appKey字段
        data["timestamp"] = str(int(datetime.datetime.now().timestamp()) * 1000)
        data["appKey"] = self.appkey
        # 根据key排序
        _data = sorted(data.items(), key=lambda x: x[0])
        _tmp = "".join([str(key) + str(value) for key, value in _data]) + self.appsecret
        signature = hashlib.sha256()
        signature.update(_tmp.encode())
        data["signature"] = signature.hexdigest()
        return data

    def _pic2base64(self, pic):
        # 图片转base64编码
        with open(pic, "rb") as f:
            base64_data = base64.b64encode(f.read())
        return base64_data.decode()

    def add_target(
        self,
        image,
        active="1",
        name=None,
        size="20",
        meta="",
        custom_post=None,
        **kwargs,
    ):
        # 新增target
        endpoint = "/targets/"
        _p = pathlib.Path(image)
        if name is None:
            name = _p.name
        _data = {
            "image": self._pic2base64(image),
            "active": active,
            "name": name,
            "size": size,
            "meta": meta,
            "type": "ImageTarget",
        }
        if isinstance(custom_post, dict):
            _data = _data.update(custom_post)
        data = self.generate_signature(_data)
        kwargs.setdefault("timeout", self.timeout)
        r = requests.post(url=self.target_api + endpoint, json=data, **kwargs)
        return r

    def del_target(self, target_id, **kwargs):
        endpoint = f"/target/{target_id}"
        signature = self.generate_signature()
        kwargs.setdefault("timeout", self.timeout)
        r = requests.delete(url=self.target_api + endpoint, params=signature, **kwargs)
        return r

    def target_list(self, start=1, size=5, **kwargs):
        endpoint = "/targets/infos"
        signature = self.generate_signature({"pageSize": size, "pageNum": start})
        kwargs.setdefault("timeout", self.timeout)
        r = requests.get(url=self.target_api + endpoint, params=signature, **kwargs)
        return r

    def search(self, pic, notracking=False, **kwargs):
        endpoint = "/search/"
        pic_base64 = self._pic2base64(pic)
        if notracking:
            params = {"image": pic_base64, "notracking": "true"}
        else:
            params = {"image": pic_base64}
        signed_params = self.generate_signature(params)
        kwargs.setdefault("timeout", self.timeout)
        r = requests.post(url=self.search_api + endpoint, json=signed_params, **kwargs)
        return r
