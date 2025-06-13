from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from ..base import BaseBIZApi

if TYPE_CHECKING:
    from ...client import CHRLINE


class Translation(BaseBIZApi):

    def __init__(self, client: "CHRLINE", version: int):
        super().__init__(client, version=version, prefix="/ds")

    @property
    def token(self):
        return self.client.biz.token_with_timeline

    @property
    def headers(self):
        return self.client.biz.headers_with_timeline

    def url(self, path: str):
        return f"{self.prefix}/translate" + path

    def get_translated_text(
        self,
        originalText: str,
        *,
        tLang: str,
        sLang: str,
        tFrom: Optional[str] = "line_timeline",
    ):
        data = {
            "id": str(uuid4()),
            "originalText": originalText,
            "tLang": tLang,
            "sLang": sLang,
        }
        hr = self.client.server.additionalHeaders(
            self.headers, {"X-Line-Translate-From": tFrom}
        )
        r = self.request("POST", self.url("/legyTransAPI.nhn"), headers=hr, json=data)
        return r.json()
