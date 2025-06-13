from typing import TYPE_CHECKING

from ..base import BaseBIZApi
from .internal.Comment import Comment
from .internal.Post import Post

if TYPE_CHECKING:
    from ...client import CHRLINE


class MyHome(BaseBIZApi):

    def __init__(self, client: "CHRLINE", version: int):
        super().__init__(client, version=version, prefix="/mh")

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

    def update_home_cover(self, objId: str):
        data = {
            "coverImageId": objId,
        }
        r = self.request(
            "POST", self.url("/home/updateCover.json"), headers=self.headers, json=data
        )
        return r.json()

    def get_profile_info(self, homeId: str):
        params = {"homeId": homeId}
        r = self.request(
            "GET",
            self.url("/home/profileBridge.json"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_oa_profile_share_link(self, homeId: str):
        params = {"homeId": homeId}
        r = self.request(
            "GET",
            self.url("/web/getUrl.json"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_lights_home(
        self,
        homeId: str,
        *,
        scrollId: str,
        seedPostId: str,
        size: int,
        direction: str = "OLDER"
    ):
        params = {
            "homeId": homeId,
            "scrollId": scrollId,
            "seedPostId": seedPostId,
            "size": size,
            "direction": direction,
        }
        r = self.request(
            "GET",
            self.url("/lights/home"),
            headers=self.headers,
            params=params,
        )
        return r.json()
