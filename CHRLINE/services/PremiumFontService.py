# -*- coding: utf-8 -*-
from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender, BaseServiceStruct


class PremiumFontService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/EXT/talk/asset-meta-server/thrift/fontService"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            "PremiumFontService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def getAccessToken(
        self,
        fontId: str,
    ):
        """Get access token."""
        METHOD_NAME = "getAccessToken"
        params = [
            [11, 1, fontId],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getFontMetas(
        self,
        requestCause: int = 1,
    ):
        """Get font metas."""
        METHOD_NAME = "getFontMetas"
        params = [
            [8, 1, requestCause],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
