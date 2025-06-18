from typing import TYPE_CHECKING

from ..base import BaseBIZApi

if TYPE_CHECKING:
    from ...client import CHRLINE


class HomeApi(BaseBIZApi):

    def __init__(self, client: "CHRLINE", version: int):
        super().__init__(client, version=version, prefix="/ma")

    @property
    def token(self):
        return self.client.biz.token_with_timeline

    @property
    def headers(self):
        return self.client.biz.headers_with_timeline

    def url(self, path: str):
        return super().url(path)

    def get_chat_room_status(self, userMid: str):
        params = {"userMid": userMid}
        r = self.request(
            "GET", self.url("/talkroom/get.json"), headers=self.headers, params=params
        )
        return r.json()
