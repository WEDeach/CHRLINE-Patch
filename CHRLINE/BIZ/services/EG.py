from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..base import BaseBIZApi

if TYPE_CHECKING:
    from ...client import CHRLINE


class SocialNotification(BaseBIZApi):

    def __init__(self, client: "CHRLINE", version: int):
        super().__init__(client, version=version, prefix="/eg")

    @property
    def token(self):
        return self.client.biz.token_with_timeline

    @property
    def headers(self):
        headers = {}
        headers.update(self.client.biz.headers_with_timeline)
        headers.update(
            {
                "x-line-signup-region": self.client.LINE_SERVICE_REGION,
                "x-line-tl-upstream-id": "1583881852",
            }
        )
        return headers

    def url(self, path: str):
        return super().url("/notification" + path)

    def get_notifications(
        self,
        noticenter: str = "SOCIAL_OPERATION_NOTICENTER",
        *,
        withTotalUnread: Optional[bool] = None,
        isMarkedAsRead: Optional[bool] = None,
        limit: Optional[int] = None,
        lastReadCreatedTime: Optional[int] = None,
        append_noticenters: Optional[List[Dict[str, Any]]] = None
    ):
        data = {
            "noticenter": noticenter,
            "isMarkedAsRead": isMarkedAsRead,
            "withTotalUnread": withTotalUnread,
            "limit": limit,
        }
        if isMarkedAsRead is not None:
            data["isMarkedAsRead"] = isMarkedAsRead
        if withTotalUnread is not None:
            data["withTotalUnread"] = withTotalUnread
        if limit is not None:
            data["limit"] = limit
        if lastReadCreatedTime is not None:
            data["lastReadCreatedTime"] = lastReadCreatedTime
        data = {"noticenters": [data]}
        if append_noticenters is not None:
            data["noticenters"].extend(append_noticenters)
        r = self.request("POST", self.url("/fetch"), headers=self.headers, json=data)
        return r.json()

    def get_all_notifications(self):
        return self.get_notifications(
            "SOCIAL_OPERATION_NOTICENTER",
            withTotalUnread=True,
            isMarkedAsRead=False,
            limit=1,
            append_noticenters=[{"noticenter": "SOCIAL_NOTICENTER"}],
        )

    def get_notifications_by_id(self, noticenter: str, *, lastReadCreatedTime: int):
        return self.get_notifications(
            noticenter, lastReadCreatedTime=lastReadCreatedTime
        )

    def delete_notifications(self, noticenter: str, *, revisions: List[int]):
        data = {"noticenter": noticenter, "revisions": revisions}
        r = self.request("POST", self.url("/delete"), headers=self.headers, json=data)
        return r.json()
