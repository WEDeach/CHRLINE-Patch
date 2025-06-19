from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

from .define_typed.Post import TPost, TPostReportReasonCode

if TYPE_CHECKING:
    from ..MH import MyHome
    from ..NT import Note
    from ..SN import SquareNote
    from ..TL import Timeline


MediaStyleType = Dict[str, Literal["GRID_1_A", "GRID_2_B", "OTHER"]]  # Example
TPostInfo = Dict[Literal["postId", "readPermission", "OTHER"], dict]  # Example


class Post:

    def __init__(self, instance: Union["MyHome", "Timeline", "Note", "SquareNote"]):
        self.instance = instance

    @property
    def headers(self):
        return self.instance.client.biz.headers_with_timeline

    @property
    def prefix(self):
        return "/post"

    def url(self, path: str):
        return self.instance.url(self.prefix + path)

    def url_with_type(self, path: str, _type: str):
        if isinstance(self.instance, "Timeline"):
            return self.instance.url(self.prefix + path, api_type=_type)
        raise NotImplementedError("url_with_type only work for Timeline.")

    def get_post(
        self,
        homeId: str,
        *,
        postId: str,
        likeLimit: int = -1,
        commentLimit: int = -1,
        sourceType: Optional[str] = None,
    ):
        data = {
            "homeId": homeId,
            "postId": postId,
            "likeLimit": likeLimit,
            "commentLimit": commentLimit,
            "sourceType": sourceType,
        }
        r = self.instance.request(
            "POST", self.url("/get.json"), headers=self.headers, json=data
        )
        return r.json()

    def fetch_post(
        self,
        homeId: Optional[str],
        *,
        postId: Optional[str] = None,
        likeLimit: int = 0,
        commentLimit: int = 0,
        sourceType: Optional[str] = None,
        updatedTime: Optional[int] = None,
    ):
        params = {
            "homeId": homeId,
            "postLimit": postId,
            "likeLimit": likeLimit,
            "commentLimit": commentLimit,
            "sourceType": sourceType,
        }
        if postId is not None and updatedTime is not None:
            params["postId"] = postId
            if homeId is None or len(homeId) == 0:
                params["createdTime"] = updatedTime
            else:
                params["updatedTime"] = updatedTime
        r = self.instance.request(
            "GET", self.url("/list.json"), headers=self.headers, params=params
        )
        return r.json()

    def send_post_to_talk(
        self,
        postId: str,
        *,
        receiveMids: Optional[List[str]],
        homeId: Optional[str] = None,
    ):
        params = {}
        data = {"postId": postId, "receiveMids": receiveMids}
        url = self.url("/sendPostToTalk.json")
        if self.instance.__class__.__name__ == "Timeline":
            data = {"postId": postId, "receiveMids": receiveMids}
        else:
            url = self.url("/share.json")
            params = {"homeId": homeId}
            data = {"postId": postId}
        r = self.instance.request(
            "POST",
            url,
            headers=self.headers,
            params=params,
            json=data,
        )
        return r.json()

    def report_post(self, homeId: str, *, postId: str, reason: TPostReportReasonCode):
        data = {"homeId": homeId, "postId": postId, "reason": reason}
        r = self.instance.request(
            "POST", self.url("/report.json"), headers=self.headers, json=data
        )
        return r.json()

    def hide_contents(self, contentId: str, serviceCode: str):
        params = {"contentId": contentId, "serviceCode": serviceCode}
        r = self.instance.request(
            "GET", self.url("/contents/hide"), headers=self.headers, params=params
        )
        return r.json()

    def delete_post(self, homeId: str, *, postId: str):
        params = {"homeId": homeId, "postId": postId}
        r = self.instance.request(
            "GET", self.url("/delete.json"), headers=self.headers, params=params
        )
        return r.json()

    def update_post(
        self,
        homeId: str,
        *,
        postBody: TPost,
        sourceType: Optional[str] = None,
    ):
        params = {"homeId": homeId, "sourceType": sourceType}
        data = postBody
        r = self.instance.request(
            "POST",
            self.url("/update.json"),
            headers=self.headers,
            params=params,
            json=data,
            required_time=True,
        )
        return r.json()

    def create_post(
        self,
        homeId: str,
        *,
        ruid: str,
        postBody: TPost,
        sourceType: Optional[str] = None,
    ):
        params = {"homeId": homeId, "sourceType": sourceType, "ruid": ruid}
        data = postBody
        r = self.instance.request(
            "POST",
            self.url("/create.json"),
            headers=self.headers,
            params=params,
            json=data,
            required_time=True,
        )
        return r.json()

    def request_lights_post_id(self):
        r = self.instance.request("GET", self.url("/id"), headers=self.headers)
        return r.json()

    def get_share_link(self, postId: str):
        params = {"postId": postId}
        r = self.instance.request(
            "GET", self.url("/getShareLink.json"), headers=self.headers, params=params
        )
        return r.json()
