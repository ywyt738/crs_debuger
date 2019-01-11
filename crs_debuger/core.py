import base64
import datetime
import hashlib
import pathlib
from collections import ChainMap

import requests


class Database:
    def __init__(self, host, appkey, appsecret, search_port=8080, target_port=8888):
        self.appkey = appkey
        self.appsecret = appsecret
        self.search_api = f"{host}:{search_port}"
        self.target_api = f"{host}:{target_port}"

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

    def add_target(self, image, active="1", name=None, size="20", meta="", **kwargs):
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
        data = dict(ChainMap(_data, kwargs))
        data = self.generate_signature(data)
        r = requests.post(url=self.target_api + endpoint, json=data)
        return r.json()

    def del_target(self, target_id):
        endpoint = f"/target/{target_id}"
        signature = self.generate_signature()
        r = requests.delete(url=self.target_api + endpoint, params=signature)
        return r.json()

    def target_list(self, start=1, size=5):
        endpoint = "/targets/infos"
        signature = self.generate_signature({"pageSize": size, "pageNum": start})
        r = requests.get(url=self.target_api + endpoint, params=signature)
        return r.json()

    def search(self, pic, notracking=False):
        endpoint = "/search/"
        pic_base64 = self._pic2base64(pic)
        if notracking:
            params = {"image": pic_base64, "notracking": "true"}
        else:
            params = {"image": pic_base64}
        signed_params = self.generate_signature(params)
        r = requests.post(url=self.search_api + endpoint, json=signed_params)
        return r.json()
