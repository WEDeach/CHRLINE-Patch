from typing import TYPE_CHECKING, Optional

from ..base import BaseBIZApi
from .internal.Comment import Comment
from .internal.Hashtag import Hashtag
from .internal.OtoAccount import OtoAccount

if TYPE_CHECKING:
    from ...client import CHRLINE


class Note(BaseBIZApi):

    def __init__(self, client: "CHRLINE", version: int):
        super().__init__(client, version=version, prefix="/nt")

        self.comment = Comment(self)
        self.oto_account = OtoAccount(self)
        self.hashtag = Hashtag(self)

    @property
    def token(self):
        return self.client.biz.token_with_timeline

    @property
    def headers(self):
        return self.client.biz.headers_with_timeline

    def url(self, path: str):
        return super().url(path)

    def search_post_list(
        self,
        homeId: str,
        *,
        query: str,
        queryType: str,
        postLimit: int,
        scrollId: Optional[str] = None
    ):
        data = {
            "homeId": homeId,
            "query": query,
            "queryType": queryType,
            "scrollId": scrollId,
            "postLimit": postLimit,
        }
        r = self.request(
            "POST", self.url("/search/note.json"), headers=self.headers, json=data
        )
        return r.json()

    def get_group_home_init_model(self):
        r = self.request("GET", self.url("/grouphome/init.json"), headers=self.headers)
        return r.json()

    def sync_new_flag(self, *, revision: Optional[int] = None):
        params = {"revision": revision}
        r = self.request(
            "GET",
            self.url("/grouphome/isnew.json"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_group_notification_setting(self, homeId: str):
        params = {"homeId": homeId}
        r = self.request(
            "GET",
            self.url("/grouphome/notisetting/getCmtLike.json"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def update_group_notification_setting(self, homeId: str, *, noti: bool):
        params = {"homeId": homeId}
        data = {"notiSet": [{"notiType": "NOTE_CMTLIKE", "noti": noti}]}
        r = self.request(
            "GET",
            self.url("/grouphome/notisetting/updateCmtLike.json"),
            headers=self.headers,
            params=params,
            json=data,
        )
        return r.json()
