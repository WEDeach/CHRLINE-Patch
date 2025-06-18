from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..base import BaseBIZApi
from .internal.Discover import Discover
from .internal.Post import Post

if TYPE_CHECKING:
    from ...client import CHRLINE


class Timeline(BaseBIZApi):

    def __init__(self, client: "CHRLINE", version: int):
        super().__init__(client, version=version, prefix="/tl")

        self.post = Post(self)
        self.discover = Discover(self)

    @property
    def token(self):
        return self.client.biz.token_with_timeline

    @property
    def headers(self):
        return self.client.biz.headers_with_timeline

    def url(self, path: str, *, api_type: str = "api"):
        return f"{self.prefix}/{api_type}/v{self.version}" + path

    def url_raw(self, path: str):
        return self.prefix + path

    def hide_contents(self, _id: str, scrollId: str, *, userCountLimit: int = 20):
        data = {"id": _id, "userCountLimit": userCountLimit, "scrollId": scrollId}
        r = self.request(
            "POST",
            self.url("/contacts/hide/profile", api_type="mapi"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def del_hide_contents(self, _id: str, *, contactIds: List[str]):
        data = {"id": _id, "contactIds": contactIds}
        r = self.request(
            "POST",
            self.url("/contacts/hide/del", api_type="mapi"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def add_hide_contents(self, _id: str, *, contactIds: List[str]):
        data = {"id": _id, "contactIds": contactIds}
        r = self.request(
            "POST",
            self.url("/contacts/hide/add", api_type="mapi"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def hide_activity(self, postId: str, mergeId: str):
        params = {"postId": postId, "mergeId": mergeId}
        r = self.request(
            "GET",
            self.url("/hideActivity", api_type="mapi"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def merge_activities(
        self,
        mergeId: str,
        postLimit: int,
        *,
        appSn: Optional[int] = None,
        postId: Optional[int] = None,
        createdTime: Optional[int] = None,
        direction: str = "next",
    ):
        params = {"mergeId": mergeId, "postLimit": postLimit}
        if appSn is not None and postId is not None and createdTime is not None:
            params["appSn"] = appSn
            params["postId"] = postId
            params["createdTime"] = createdTime
            params["direction"] = direction
        r = self.request(
            "GET",
            self.url("/mergeActivities", api_type="mapi"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_timeline(
        self,
        *,
        feed_version: str,
        story_version: str,
        postLimit: int,
        requestTime: int,
        userAction: str = "TAP-NEW_POST",
        query_order: Optional[str] = None,
        contents: list = ["CP", "PI", "PV", "PL", "LS"],
    ):

        queryParams = {
            "postLimit": postLimit,
            "requestTime": requestTime,
            "userAction": userAction,
        }
        if query_order is not None:
            queryParams["order"] = query_order
        feedRequests = {
            "FEED_LIST": {
                "version": feed_version,
                "queryParams": queryParams,
                "requestBody": {"discover": {"contents": contents}},
            },
            "STORY": {"version": story_version},
        }
        data = {"feedRequests": feedRequests}
        r = self.request(
            "POST",
            self.url("/timeline/tab/contents.json"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_feed(self, feedInfos: list):
        data = {"feedInfos": feedInfos}
        r = self.request(
            "POST", self.url("/feed/get.json"), headers=self.headers, json=data
        )
        return r.json()

    def update_feed_status(self, *, requestTime: Optional[int] = None):
        params = {}
        if requestTime is not None:
            params["requestTime"] = requestTime
        r = self.request(
            "GET", self.url("/feed/newfeed.json"), headers=self.headers, params=params
        )
        return r.json()

    def get_timeline_tab_status(self):
        r = self.request(
            "GET", self.url("/timeline/tab/status.json"), headers=self.headers
        )
        return r.json()

    def fetch_neta_contents_with_module_id(self, moduleId: str, _type: str):
        params = {"moduleId": moduleId, "type": _type}
        r = self.request(
            "GET",
            self.url_raw("/netacard/api/v2/list.json"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def fetch_neta_contents(self, cardId: str):
        params = {"cardId": cardId}
        r = self.request(
            "GET",
            self.url_raw("/netacard/api/v2/get.json"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def cancel_celebration(self, boardId: str, _from: str):
        data = {"boardId": boardId, "from": _from}
        r = self.request(
            "POST",
            self.url_raw("/api/v1/bdb/celebrate/cancel"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def create_like_card(self, boardId: str, cardId: str):
        data = {"boardId": boardId, "cardId": cardId}
        r = self.request(
            "POST",
            self.url_raw("/api/v1/bdb/card/like/create"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def cancel_like_card(self, boardId: str, cardId: str):
        data = {"boardId": boardId, "cardId": cardId}
        r = self.request(
            "POST",
            self.url_raw("/api/v1/bdb/card/like/cancel"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def delete_card(self, boardId: str, cardId: str):
        data = {"boardId": boardId, "cardId": cardId}
        r = self.request(
            "POST",
            self.url_raw("/api/v1/bdb/card/delete"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def report_card(self, boardId: str, cardId: str):
        data = {"boardId": boardId, "cardId": cardId}
        r = self.request(
            "GET",
            self.url_raw("/api/v1/bdb/card/report"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def delete_board(self, boardId: str, _from: str):
        data = {"boardId": boardId, "from": _from}
        r = self.request(
            "POST",
            self.url_raw("/api/v1/bdb/board/delete"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_card_template_list(self):
        r = self.request(
            "GET", self.url_raw("/api/v1/bdb/template/card/list"), headers=self.headers
        )
        return r.json()

    def create_card(
        self,
        boardId: str,
        celebratorMid: str,
        cardStatus: str,
        text: str,
        _from: str,
        *,
        templateId: Optional[str] = None,
    ):
        data = {
            "boardId": boardId,
            "celebratorMid": celebratorMid,
            "cardStatus": cardStatus,
            "text": text,
            "from": _from,
        }
        if templateId is not None:
            data["templateId"] = templateId
        r = self.request(
            "POST",
            self.url_raw("/api/v1/bdb/card/create"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def update_board_read_permission(
        self,
        boardId: str,
        *,
        _from: str,
        gids: List[int],
        count: int,
        _type: str = "ALL",
    ):
        data = {
            "type": _type,
            "boardId": boardId,
            "gids": gids,
            "count": count,
        }
        data = {
            "readPermission": data,
            "from": _from,
        }
        r = self.request(
            "POST",
            self.url_raw("/api/v1/bdb/board/update/readPermission"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def update_card(
        self,
        boardId: str,
        cardId: str,
        cardStatus: str,
        text: str,
        *,
        templateId: Optional[str] = None,
    ):
        data = {
            "boardId": boardId,
            "cardId": cardId,
            "cardStatus": cardStatus,
            "text": text,
        }
        if templateId is not None:
            data["templateId"] = templateId
        r = self.request(
            "POST",
            self.url_raw("/api/v1/bdb/card/update"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_card_list(
        self,
        boardId: str,
        *,
        limit: Optional[int] = None,
        scrollId: Optional[str] = None,
    ):
        data: Dict[str, Any] = {"boardId": boardId}
        if limit is not None:
            data["limit"] = limit
        if scrollId is not None:
            data["scrollId"] = scrollId
        r = self.request(
            "POST",
            self.url_raw("/api/v1/bdb/card/list"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_celebration_list(self, boardId: str, *, scrollId: Optional[str] = None):
        data = {"boardId": boardId}
        if scrollId is not None:
            data["scrollId"] = scrollId
        r = self.request(
            "POST",
            self.url_raw("/api/v1/bdb/celebrate/list"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_board(self, boardId: str, *, cardId: Optional[str] = None):
        data = {"boardId": boardId}
        if cardId is not None:
            data["cardId"] = cardId
        r = self.request(
            "POST",
            self.url_raw("/api/v1/bdb/board/get"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_birthday_card_like_list(
        self, boardId: str, *, cardId: str, scrollId: Optional[str] = None
    ):
        data = {"boardId": boardId, "cardId": cardId}
        if scrollId is not None:
            data["scrollId"] = scrollId
        r = self.request(
            "POST",
            self.url_raw("/api/v1/bdb/card/like/list"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_follow_list(self, *, nextScrollId: Optional[str] = None):
        params = {}
        if nextScrollId is not None:
            params["nextScrollId"] = nextScrollId
        r = self.request(
            "POST",
            self.url_raw("/feed/api/v1/follow/friends/youCanFollow"),
            headers=self.headers,
            params=params,
        )
        return r.json()
