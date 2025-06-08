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

    def createPwlessSession(self, phone, region='TW'):
        METHOD_NAME = "createSession"
        params = [
            [12, 1, [
                [11, 1, phone],
                [11, 2, region]
            ]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def verifyLoginCertificate(self, session, cert=None):
        METHOD_NAME = "verifyLoginCertificate"
        params = [
            [12, 1, [
                [11, 1, session],
                [11, 2, cert]
            ]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def requestPinCodeVerif(self, session):
        METHOD_NAME = "requestPinCodeVerif"
        params = [
            [12, 1, [
                [11, 1, session]
            ]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def putExchangeKey(self, session, temporalPublicKey, e2eeVersion=1):
        METHOD_NAME = "putExchangeKey"
        params = [
            [12, 1, [
                [11, 1, session],
                [13, 2, [11, 11, {
                    'e2eeVersion': str(e2eeVersion),
                    'temporalPublicKey': temporalPublicKey
                }]]
            ]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def requestPaakAuth(self, session):
        METHOD_NAME = "requestPaakAuth"
        params = [
            [12, 1, [
                [11, 1, session]
            ]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getE2eeKey(self, session):
        METHOD_NAME = "getE2eeKey"
        params = [
            [12, 1, [
                [11, 1, session]
            ]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def pwlessLogin(self, session):
        METHOD_NAME = "login"
        params = [
            [12, 1, [
                [11, 1, session],
                [11, 2, "DeachSword-CHRLINE"],
                [11, 3, "CHANNELGW"]
            ]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def pwlessLoginV2(self, session):
        METHOD_NAME = "loginV2"
        params = [
            [12, 1, [
                [11, 1, session],
                [2, 2, True],
                [11, 3, "DeachSword-CHRLINE"],
                [11, 4, "CHANNELGW"]
            ]]
        ]
        return self.__sender.send(METHOD_NAME, params)