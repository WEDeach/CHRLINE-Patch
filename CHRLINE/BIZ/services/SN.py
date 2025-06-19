from typing import TYPE_CHECKING, Optional

from ..base import BaseBIZApi
from .internal.Comment import Comment
from .internal.Post import Post

if TYPE_CHECKING:
    from ...client import CHRLINE


class SquareNote(BaseBIZApi):

    def __init__(self, client: "CHRLINE", version: int):
        super().__init__(client, version=version, prefix="/sn")

        self.post = Post(self)
        self.comment = Comment(self)

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
        postLimit: int = 10,
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
            "GET", self.url("/search/note"), headers=self.headers, json=data
        )
        return r.json()

    def create_announce(self, homeId: str, *, postId: str):
        params = {"homeId": homeId}
        data = {"postId": postId}
        r = self.request(
            "POST",
            self.url("/announce/create.json"),
            headers=self.headers,
            params=params,
            json=data,
        )
        return r.json()

    def delete_announce(self, homeId: str, *, postId: str):
        params = {"homeId": homeId, "postId": postId}
        r = self.request(
            "GET",
            self.url("/announce/delete.json"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def fetch_announce(self, homeId: str):
        params = {"homeId": homeId}
        r = self.request(
            "GET",
            self.url("/announce/list.json"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def fetch_announce_post(self, homeId: str, *, scrollId: str):
        params = {"homeId": homeId, "scrollId": scrollId}
        r = self.request(
            "GET",
            self.url("/announce/postlist.json"),
            headers=self.headers,
            params=params,
        )
        return r.json()
