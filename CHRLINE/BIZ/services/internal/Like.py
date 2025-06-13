from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from ..MH import MyHome
    from ..NT import Note
    from ..SN import SquareNote
    from ..TL import Timeline


class Like:

    def __init__(self, instance: Union["MyHome", "Timeline", "Note", "SquareNote"]):
        self.instance = instance

    @property
    def headers(self):
        return self.instance.client.biz.headers_with_timeline

    def url(self, path: str):
        return self.instance.url("/like" + path)

    def get(self, contentId: str, *, homeId: Optional[str] = None):
        params = {"contentId": contentId}
        if homeId is not None:
            params["homeId"] = homeId
        r = self.instance.request(
            "GET", self.url("/get.json"), headers=self.headers, params=params
        )
        return r.json()

    def create(
        self,
        contentId: str,
        *,
        homeId: Optional[str] = None,
        likeType: int,
        sourceType: Optional[str] = None,
        ruid: Optional[str] = None,
        actorId: Optional[str] = None,
        sharable: bool = False
    ):
        params = {"ruid": ruid, "sourceType": sourceType}
        data = {
            "contentId": contentId,
            "actorId": actorId,
            "likeType": likeType,
            "sharable": sharable,
        }
        if homeId is not None:
            params["homeId"] = homeId
        r = self.instance.request(
            "POST",
            self.url("/create.json"),
            headers=self.headers,
            params=params,
            json=data,
        )
        return r.json()

    def cancel(
        self,
        contentId: str,
        *,
        homeId: Optional[str] = None,
        sourceType: Optional[str] = None
    ):
        params = {"contentId": contentId, "sourceType": sourceType}
        if homeId is not None:
            params["homeId"] = homeId
        r = self.instance.request(
            "GET", self.url("/cancel.json"), headers=self.headers, params=params
        )
        return r.json()

    def get_list(
        self,
        contentId: str,
        *,
        homeId: Optional[str] = None,
        scrollId: Optional[str] = None,
        includes: str = "ALL,GROUPED,STATS",
        filterType: Optional[int] = None
    ):
        params = {"contentId": contentId, "includes": includes}
        if homeId is not None:
            params["homeId"] = homeId
        if scrollId is not None:
            params["scrollId"] = scrollId
        if filterType is not None:
            params["filterType"] = str(filterType)  # eg. 1003 for GROUPED
        r = self.instance.request(
            "POST", self.url("/getList.json"), headers=self.headers, params=params
        )
        return r.json()
