# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class RegistrationAuthService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/api/v4p/rs"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def confirmE2EELogin(self, verifier, deviceSecret):
        METHOD_NAME = "confirmE2EELogin"
        params = [
            [11, 1, verifier],
            [11, 2, deviceSecret],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def issueTokenForAccountMigration(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("issueTokenForAccountMigration is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "issueTokenForAccountMigration", params, self.AuthService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.AuthService_API_PATH, sqrd, self.AuthService_RES_TYPE
        )

    def normalizePhoneNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("normalizePhoneNumber is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "normalizePhoneNumber", params, self.AuthService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.AuthService_API_PATH, sqrd, self.AuthService_RES_TYPE
        )
