# -*- coding: utf-8 -*-

from typing import Optional

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class ChatAppService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/CAPP1"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def getChatapp(self, chatappId: str, language: str = "zh_TW"):
        METHOD_NAME = "getChatapp"
        params = [[12, 1, [[11, 1, chatappId], [11, 2, language]]]]
        return self.__sender.send(METHOD_NAME, params)

    def getMyChatapps(
        self, language: str = "zh_TW", continuationToken: Optional[str] = None
    ):
        METHOD_NAME = "getMyChatapps"
        params = [[12, 1, [[11, 1, language], [11, 2, continuationToken]]]]
        return self.__sender.send(METHOD_NAME, params)
