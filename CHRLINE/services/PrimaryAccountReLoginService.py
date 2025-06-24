# -*- coding: utf-8 -*-
from typing import Any

from .BaseService import BaseService, BaseServiceSender, BaseServiceStruct


class PrimaryAccountReLoginService(BaseService):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/ext/auth/feature-guest/thrift/account/v1/relogin/primary"

    def __init__(self, client: Any):
        self.__sender = BaseServiceSender(
            client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def createSession(self, mid: str, modelName: str, deviceUid: str):
        """Create relogin session."""
        METHOD_NAME = "createSession"
        request = [
            [11, 1, mid],
            [11, 2, modelName],
            [11, 3, deviceUid],
        ]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def getCountryInfo(
        self,
        authSessionId: str,
        countryCode: str = "TW",
        hni: str = "46601",
        carrierName: str = "Far EasTone Telecommunications Co Ltd",
    ):
        """get country info."""
        METHOD_NAME = "getCountryInfo"
        simCard = [
            [11, 1, countryCode],
            [11, 2, hni],
            [11, 3, carrierName],
        ]
        request = [
            [11, 1, authSessionId],
            [12, 2, simCard],
        ]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def getPasswordHashingParameters(self, authSessionId: str):
        """Get password hashing parameters."""
        METHOD_NAME = "getPasswordHashingParameters"
        request = [[11, 1, authSessionId]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def getPhoneVerifMethodV2(
        self, authSessionId: str, phoneNumber: str, countryCode: str
    ):
        """Get phone verif method v2."""
        METHOD_NAME = "getPhoneVerifMethodV2"
        userPhoneNumber = [[11, 1, phoneNumber], [11, 2, countryCode]]
        request = [[11, 1, authSessionId], [12, 2, userPhoneNumber]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def reloginPrimaryUsingEapAccount(self, authSessionId: str):
        """Relogin primary using eap account."""
        METHOD_NAME = "reloginPrimaryUsingEapAccount"
        request = [[11, 1, authSessionId]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def reloginPrimaryUsingPhone(self, authSessionId: str):
        """Relogin primary using phone."""
        METHOD_NAME = "reloginPrimaryUsingPhone"
        request = [[11, 1, authSessionId]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def requestToSendPhonePinCode(self, authSessionId: str, verifMethod: int):
        """Request to send phone pin code."""
        METHOD_NAME = "requestToSendPhonePinCode"
        request = [[11, 1, authSessionId], [8, 2, verifMethod]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def verifyAccountUsingPwd(
        self, authSessionId: str, v1HashedPassword: str, clientHashedPassword: str
    ):
        """Verify account using pwd."""
        METHOD_NAME = "verifyAccountUsingPwd"
        _v1HashedPassword = [[11, 1, v1HashedPassword]]
        _clientHashedPassword = [[11, 1, clientHashedPassword]]
        request = [
            [11, 1, authSessionId],
            [12, 2, _v1HashedPassword],
            [12, 3, _clientHashedPassword],
        ]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def verifyEapLogin(
        self, authSessionId: str, eapType: int, accessToken: str, countryCode: str
    ):
        """Verify eap login."""
        METHOD_NAME = "verifyEapLogin"
        eapLogin = [
            [8, 1, eapType],
            [11, 2, accessToken],
            [11, 3, countryCode],
        ]
        request = [[11, 1, authSessionId], [12, 2, eapLogin]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def verifyEmail(self, authSessionId: str, email: str):
        """Verify email."""
        METHOD_NAME = "verifyEmail"
        _email = [[11, 1, email]]
        request = [[11, 1, authSessionId], [12, 2, _email]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def verifyPhonePinCode(self, authSessionId: str, pinCode: str):
        """Verify phone pin code."""
        METHOD_NAME = "verifyPhonePinCode"
        request = [[11, 1, authSessionId], [11, 2, pinCode]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)
