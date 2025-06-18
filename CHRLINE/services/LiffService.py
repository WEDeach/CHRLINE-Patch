# -*- coding: utf-8 -*-

from typing import List

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender, BaseServiceStruct


class LiffService(ChrHelperProtocol):  # noqa: F821
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/LIFF1"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            "LiffService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def issueLiffView(
        self, chatMid, liffId="1562242036-RW04okm", lang="zh_TW", isSub=False
    ):
        """Issue liff view."""
        METHOD_NAME = "issueLiffView"
        if isSub:
            METHOD_NAME = "issueSubLiffView"
        context = [12, 1, []]
        if chatMid is not None:
            chat = [11, 1, chatMid]
            if chatMid[0] in ["u", "c", "r"]:
                chatType = 2
            else:
                chatType = 3
            context = [12, chatType, [chat]]
        params = [
            [
                12,
                1,
                [
                    [11, 1, liffId],
                    [12, 2, [context]],
                    [11, 3, lang],
                    # [12, 4, []], # deviceSetting
                    # [11, 5, None] # msit
                ],
            ]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getLiffViewWithoutUserContext(self, liffId="1562242036-RW04okm"):
        """Get liff view without user context."""
        METHOD_NAME = "getLiffViewWithoutUserContext"
        params = [
            [11, 1, liffId],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
        
    def revokeLiffTokens(self, accessTokens: List[str]):
        """Revoke liff tokens."""
        METHOD_NAME = "revokeTokens"
        if not isinstance(accessTokens, list):
            raise ValueError("accessTokens must be list, but got %s." % type(accessTokens))
        params = [
            [15, 1, [11, accessTokens]],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)