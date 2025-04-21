# -*- coding: utf-8 -*-


from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender, BaseServiceStruct


class AccessTokenRefreshService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/EXT/auth/tokenrefresh/v1"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            "AccessTokenRefreshService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def refreshAccessToken(self, refreshToken: str):
        METHOD_NAME = "refresh"
        params = [
            [11, 1, refreshToken],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def reportRefreshedAccessToken(self, refreshToken: str):
        METHOD_NAME = "reportRefreshedAccessToken"
        params = [
            [11, 1, refreshToken],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
