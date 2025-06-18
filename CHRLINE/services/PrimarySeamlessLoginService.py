# -*- coding: utf-8 -*-
# THIS SCRIPT IS REFS TO
#   https://canary.discord.com/channels/466066749440393216/827711705899204699/1261308927530897419
#       2024/07/12 - Wear OS

from typing import TYPE_CHECKING, Dict

from .BaseService import BaseService, BaseServiceSender, BaseServiceStruct

if TYPE_CHECKING:
    from ..client import CHRLINE


class PrimarySeamlessLoginService(BaseService):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/EXT/auth/feature-user/api/secondary/login/seamless"

    def __init__(self, client: "CHRLINE"):
        self.client = client
        self.__sender = BaseServiceSender(
            self.client,
            "SeamlessLoginService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def permitLogin(self, sessionId: str, metaData: Dict[str, str]):
        """Permit login."""
        METHOD_NAME = "permitLogin"
        params = [
            [11, 1, sessionId],
            [13, 2, [11, 11, metaData]],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
