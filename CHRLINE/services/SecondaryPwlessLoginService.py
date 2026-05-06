# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class SecondaryPwlessLoginService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/acct/lgn/secpwless/v1"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def createPwlessSession(self, phone, region="TW"):
        METHOD_NAME = "createSession"
        request = [[11, 1, phone], [11, 2, region]]
        params = [[12, 1, request]]
        return self.__sender.send(METHOD_NAME, params)

    def verifyLoginCertificate(self, session, cert=None):
        METHOD_NAME = "verifyLoginCertificate"
        request = [[11, 1, session], [11, 2, cert]]
        params = [[12, 1, request]]
        return self.__sender.send(METHOD_NAME, params)

    def requestPinCodeVerif(self, session):
        METHOD_NAME = "requestPinCodeVerif"
        request = [[11, 1, session]]
        params = [[12, 1, request]]
        return self.__sender.send(METHOD_NAME, params)

    def putExchangeKey(self, session, temporalPublicKey, e2eeVersion=1):
        METHOD_NAME = "putExchangeKey"
        e2eeInfo = {
            "e2eeVersion": str(e2eeVersion),
            "temporalPublicKey": temporalPublicKey,
        }
        request = [
            [11, 1, session],
            [13, 2, [11, 11, e2eeInfo]],
        ]
        params = [[12, 1, request]]
        return self.__sender.send(METHOD_NAME, params)

    def requestPaakAuth(self, session):
        METHOD_NAME = "requestPaakAuth"
        request = [[11, 1, session]]
        params = [[12, 1, request]]
        return self.__sender.send(METHOD_NAME, params)

    def getE2eeKey(self, session):
        METHOD_NAME = "getE2eeKey"
        request = [[11, 1, session]]
        params = [[12, 1, request]]
        return self.__sender.send(METHOD_NAME, params)

    def pwlessLogin(self, session):
        METHOD_NAME = "login"
        request = [
            [11, 1, session],
            [11, 2, "DeachSword-CHRLINE"],
            [11, 3, "CHANNELGW"],
        ]
        params = [[12, 1, request]]
        return self.__sender.send(METHOD_NAME, params)

    def pwlessLoginV2(self, session, autoLoginIsRequired=True):
        METHOD_NAME = "loginV2"
        request = [
            [11, 1, session],
            [2, 2, autoLoginIsRequired],
            [11, 3, "DeachSword-CHRLINE"],
            [11, 4, "CHANNELGW"],
        ]
        params = [[12, 1, request]]
        return self.__sender.send(METHOD_NAME, params)
