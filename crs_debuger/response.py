import requests
from .exceptions import ClassInitError


class Response:
    def __init__(self, r: requests.Response):
        self.raw = r
        self.status_code = r.status_code

    def __repr__(self):
        return f"<{self.__class__} [%s]>" % (self.status_code)

    def json(self):
        return self.raw.json()

    @property
    def elapsed(self):
        return self.raw.elapsed


class SearchResponse(Response):
    @property
    def ok(self):
        data = self.json()
        code = data.get("statusCode", None)
        if code == 0:
            return True
        else:
            return False

    @property
    def target_id(self):
        try:
            return self.json()["result"]["target"]["targetId"]
        except KeyError:
            return "Not Recognized"


class TargetListResponse(Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = 0
        try:
            self.targets = self.json()["result"]["targets"]
        except KeyError:
            raise ClassInitError(f"target_list接口返回错误, HttpCode:{self.status_code}")

    def __iter__(self):
        return self

    def __next__(self):
        try:
            target = self.targets[self._index]
            result = Target(**target)
            self._index += 1
            return result
        except IndexError:
            raise StopIteration()

    def __len__(self):
        return len(self.targets)


class Target:
    def __init__(self, name, size, systemMeta, targetId, trackingImage, **kwargs):
        self.name = name
        self.size = size
        self.meta = systemMeta
        self.target_id = targetId
        self.tracking_image = trackingImage

    def download(self, filename=None):
        if not filename:
            filename = f"{self.target_id}.jpg"
        res = requests.get(self.tracking_image, stream=True)
        with open(filename, 'wb') as fd:
            for chunk in res.iter_content(chunk_size=128):
                fd.write(chunk)
