from typing import TYPE_CHECKING, Union

from .define_typed.Post import TPostReportReasonCode

if TYPE_CHECKING:
    from ..MH import MyHome
    from ..NT import Note
    from ..SN import SquareNote
    from ..TL import Timeline


class Comment:

    def __init__(self, instance: Union["MyHome", "Timeline", "Note", "SquareNote"]):
        self.instance = instance

    @property
    def headers(self):
        return self.instance.client.biz.headers_with_timeline

    def url(self, path: str):
        return self.instance.url("/comment" + path)

    def report_comment(self, commentId: str, *, reason: TPostReportReasonCode):
        data = {"commentId": commentId, "reason": reason}
        r = self.instance.request(
            "POST", self.url("/report.json"), headers=self.headers, json=data
        )
        return r.json()

    def get_highlight_comment(self, commentId: str):
        params = {"commentId": commentId}
        r = self.instance.request(
            "GET", self.url("/get.json"), headers=self.headers, params=params
        )
        return r.json()

    def delete_comment(self, homeId: str, *, commentId: str, actorId: str):
        params = {"homeId": homeId, "commentId": commentId, "actorId": actorId}
        r = self.instance.request(
            "GET", self.url("/delete.json"), headers=self.headers, params=params
        )
        return r.json()

    def get_more_comments(
        self,
        homeId: str,
        *,
        contentId: str,
        actorId: str,
        scrollId: str,
        limit: int = -1
    ):
        params = {
            "homeId": homeId,
            "contentId": contentId,
            "actorId": actorId,
            "scrollId": scrollId,
            "limit": limit,
        }
        r = self.instance.request(
            "GET", self.url("/getList.json"), headers=self.headers, params=params
        )
        return r.json()
