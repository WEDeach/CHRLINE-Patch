# -*- coding: utf-8 -*-


from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class HomeSafetyCheckService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/EXT/home/safety-check/safety-check"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def deleteSafetyStatus(self, disasterId: str):
        METHOD_NAME = "deleteSafetyStatus"
        params = [[12, 1, [[11, 1, disasterId]]]]
        return self.__sender.send(METHOD_NAME, params)

    def getDisasterCases(self):
        METHOD_NAME = "getDisasterCases"
        params = [[12, 1, []]]
        return self.__sender.send(METHOD_NAME, params)

    def updateSafetyStatus(self, disasterId: str, message: str, safetyStatus: int = 1):
        """
        - safetyStatus:
            SAFE(1),
            NOT_SAFE(2);
        """
        METHOD_NAME = "updateSafetyStatus"
        params = [
            [
                12,
                1,
                [
                    [11, 1, disasterId],
                    [8, 2, safetyStatus],
                    [11, 3, message],
                ],
            ]
        ]
        return self.__sender.send(METHOD_NAME, params)
