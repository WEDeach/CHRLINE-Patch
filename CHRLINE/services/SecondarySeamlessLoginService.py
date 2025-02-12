# -*- coding: utf-8 -*-
# THIS SCRIPT IS REFS TO
#   https://canary.discord.com/channels/466066749440393216/827711705899204699/1261308927530897419
#       2024/07/12 - Wear OS

from typing import TYPE_CHECKING

from .BaseService import BaseService, BaseServiceSender, BaseServiceStruct

if TYPE_CHECKING:
    from ..client import CHRLINE


class SecondarySeamlessLoginService(BaseService):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/ext/auth/feature-guest/api/secondary/login/seamless"

    def __init__(self, client: "CHRLINE"):
        self.client = client
        self.__sender = BaseServiceSender(
            self.client,
            "SeamlessLoginService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def createSession(self):
        """Create session."""
        METHOD_NAME = "createSession"
        params = []
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def login(
        self, sessionId: str, systemDisplayName: str, modelName: str, oneTimeToken: str
    ):
        """login."""
        METHOD_NAME = "login"
        params = [
            [11, 1, sessionId],
            [11, 2, systemDisplayName],
            [11, 3, modelName],
            [11, 4, oneTimeToken],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
