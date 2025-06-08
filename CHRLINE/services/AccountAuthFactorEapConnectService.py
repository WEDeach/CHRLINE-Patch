# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender, BaseServiceStruct


class AccountAuthFactorEapConnectService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/ACCT/authfactor/eap/v1"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def connectEapAccount(self, authSessionId: str):
        METHOD_NAME = "connectEapAccount"
        params = [
            [11, 1, authSessionId],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def disconnectEapAccount(self, eapType: int = 3):
        METHOD_NAME = "disconnectEapAccount"
        params = [
            [8, 1, eapType],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getHashedPpidForYahoojapan(self):
        METHOD_NAME = "getHashedPpidForYahoojapan"
        params = []
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def openAAFECSession(self, udid: str, deviceModel: str = "Pixel 2"):
        METHOD_NAME = "openSession"
        params = [12, 1, [[11, 1, udid], [11, 1, deviceModel]]]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def verifyEapLogin(self, authSessionId: str, type: int, accessToken: str):
        """
        - type:
            UNKNOWN(0),
            FACEBOOK(1),
            APPLE(2),
            YAHOOJAPAN(3);
        """
        METHOD_NAME = "verifyEapLogin"
        eapLogin = [
            [8, 1, type],
            [11, 2, accessToken],
        ]
        params = [
            [11, 1, authSessionId],
            [12, 2, eapLogin],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
