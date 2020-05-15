import asyncio
import base64
import datetime
import hashlib
import json
import pathlib

import requests
import umsgpack
import websockets
from requests.exceptions import InvalidSchema
from urllib3.util import parse_url

from crs_debuger.exceptions import GetTunnelIDError
from crs_debuger.response import SearchResponse, TargetListResponse


class Database:
    def __init__(
        self,
        searcher_host,
        appkey,
        appsecret,
        targeter_host=None,
        search_port=8080,
        target_port=8888,
        timeout=None,
    ):
        self.appkey = appkey
        self.appsecret = appsecret
        self.timeout = timeout
        self.searcher_host = searcher_host
        self.targeter_host = targeter_host or searcher_host
        self.search_api = self._prepare_api_url(self.searcher_host, search_port)
        self.target_api = self._prepare_api_url(self.targeter_host, target_port)

    def _prepare_api_url(self, url, p):
        scheme, auth, host, port, path, query, fragment = parse_url(url)
        if scheme is None or scheme == "http":
            return f"http://{host}:{p}"
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
        allow_similar=False,
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
            "allowSimilar": "0" if not allow_similar else "1",
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
        return TargetListResponse(r)

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
        return SearchResponse(r)

    def similar(self, pic, **kwargs):
        endpoint = "/similar/"
        pic_base64 = self._pic2base64(pic)
        kwargs.setdefault("timeout", self.timeout)
        signed_params = self.generate_signature({"image": pic_base64})
        r = requests.post(url=self.target_api + endpoint, json=signed_params, **kwargs)
        return r

    def grade(self, pic, **kwargs):
        endpoint = "/grade/detection/"
        pic_base64 = self._pic2base64(pic)
        kwargs.setdefault("timeout", self.timeout)
        signed_params = self.generate_signature({"image": pic_base64})
        r = requests.post(url=self.target_api + endpoint, json=signed_params, **kwargs)
        return r

    async def _search_with_websocket(self, images: list) -> list:
        get_tunnel_endpoint = "/tunnels/"
        signed_params = self.generate_signature()
        r = requests.post(url=self.search_api + get_tunnel_endpoint, json=signed_params)
        try:
            tunnel_id = r.json().get("result").get("tunnel")
        except Exception:
            raise GetTunnelIDError(r.content.decode())
        ws_uri = (
            f"{self.search_api.replace('http', 'ws', 1)}/services/recognize/{tunnel_id}"
        )
        res = []
        async with websockets.connect(ws_uri) as websocket:
            for img in images:
                with open(img, "rb") as fp:
                    data = umsgpack.packb({"image": fp.read()})
                await websocket.send(data)
                recv = await websocket.recv()
                res.append(json.loads(recv))
        return res

    def search_with_websocket(self, images):
        res = asyncio.get_event_loop().run_until_complete(self._search_with_websocket(images))
        return res
