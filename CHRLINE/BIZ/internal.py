from typing import TYPE_CHECKING

from .base import BaseBIZ

if TYPE_CHECKING:
    from ..client import CHRLINE


class InternalBiz(BaseBIZ):
    def __init__(self, client: "CHRLINE"):
        super().__init__(client)

    @property
    def domain(self):
        return self.client.LINE_API_DOMAIN

    def get_certs_with_token(self, token: str):
        res = self.request_get("/oauth2/v2.1/certs", headers={"authorization": f"Bearer {token}"})
        return res.json()
