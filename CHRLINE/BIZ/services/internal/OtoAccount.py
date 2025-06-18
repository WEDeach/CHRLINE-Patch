from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from ..NT import Note


class OtoAccount:

    def __init__(self, instance: "Note"):
        self.instance = instance

    @property
    def headers(self):
        return self.instance.client.biz.headers_with_timeline

    def url(self, path: str):
        return self.instance.url("/otoaccount" + path)

    def create_single_group(self, userMid: str, *, friendMid: str):
        data = {"userMid": userMid, "friendMid": friendMid}

        r = self.instance.request(
            "POST", self.url("/create.json"), headers=self.headers, json=data
        )
        return r.json()

    def sync_single_group(self, userMid: str, *, revision: Optional[int] = None):
        params: Dict[str, Any] = {"userMid": userMid}
        if revision is not None:
            params["revision"] = revision
        r = self.instance.request(
            "POST", self.url("/create.json"), headers=self.headers, params=params
        )
        return r.json()
