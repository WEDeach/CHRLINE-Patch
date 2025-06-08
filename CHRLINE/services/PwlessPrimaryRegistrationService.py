# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class PwlessPrimaryRegistrationService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/ACCT/authfactor/pwless/v1"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def createSession(self):
        METHOD_NAME = "createSession"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getChallengeForPrimaryReg(self, session):
        METHOD_NAME = "getChallengeForPrimaryReg"
        params = [[12, 1, [[11, 1, session]]]]
        return self.__sender.send(METHOD_NAME, params)

    def registerPrimaryCredential(self, session: str, cId: str, cType: str):
        raise NotImplementedError("RegisterPrimaryCredential id not implemented.")
        params = [
            [
                12,
                1,
                [
                    [11, 1, session],
                    [
                        12,
                        2,
                        [
                            [11, 1, cId],
                            [11, 2, cType],
                            # [12, 3, response],
                            # [12, 4, extensionResults]
                        ],
                    ],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol("registerPrimaryCredential", params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_PWLESS_PRIMARY_REGISTRATION_ENDPOINT,
            sqrd,
            4,
            access_token=session,
        )
