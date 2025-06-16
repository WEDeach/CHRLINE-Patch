# -*- coding: utf-8 -*-
from typing import Any

from .BaseService import BaseService, BaseServiceSender, BaseServiceStruct


class PrimaryAccountSmartSwitchRestoreService(BaseService):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/ext/auth/feature-guest/thrift/account/v1/restore/smart-switch"

    def __init__(self, client: Any):
        self.__sender = BaseServiceSender(
            client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def restorePrimaryViaSmartSwitchUsingEapAccount(self, authSessionId: str):
        """Restore primary via smart switch using eap account."""
        METHOD_NAME = "restorePrimaryViaSmartSwitchUsingEapAccount"
        request = [[11, 1, authSessionId]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def restorePrimaryViaSmartSwitchUsingPhone(self, authSessionId: str):
        """Restore primary via smart switch using phone."""
        METHOD_NAME = "restorePrimaryViaSmartSwitchUsingPhone"
        request = [[11, 1, authSessionId]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def checkEmailAssigned(self, authSessionId: str):
        """Check email assigned."""
        METHOD_NAME = "checkEmailAssigned"
        request = [[11, 1, authSessionId]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def checkIfPasswordSetVerificationEmailVerified(self, authSessionId: str):
        """Check if password set verification email verified."""
        METHOD_NAME = "checkIfPasswordSetVerificationEmailVerified"
        request = [[11, 1, authSessionId]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def getAcctVerifMethod(self, authSessionId: str):
        """Get acct verif method."""
        METHOD_NAME = "getAcctVerifMethod"
        request = [[11, 1, authSessionId]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def getCountryInfo(
        self,
        authSessionId: str,
        countryCode: str = "TW",
        hni: str = "46601",
        carrierName: str = "Far EasTone Telecommunications Co Ltd",
    ):
        """Get country info."""
        METHOD_NAME = "getCountryInfo"
        simCard = [
            [11, 1, countryCode],
            [11, 2, hni],
            [11, 3, carrierName],
        ]
        request = [[11, 1, authSessionId], [12, 2, simCard]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def getMaskedEmail(self, authSessionId: str):
        """Get masked email."""
        METHOD_NAME = "getMaskedEmail"
        request = [[11, 1, authSessionId]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def getPasswordHashingParametersForPwdReg(self, authSessionId: str):
        """Get password hashing parameters for pwd reg."""
        METHOD_NAME = "getPasswordHashingParametersForPwdReg"
        request = [[11, 1, authSessionId]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def getPasswordHashingParametersForPwdVerif(self, authSessionId: str):
        """Get password hashing parameters for pwd verif."""
        METHOD_NAME = "getPasswordHashingParametersForPwdVerif"
        request = [[11, 1, authSessionId]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def getPhoneVerifMethodV2(
        self,
        authSessionId: str,
        phoneNumber: str,
        countryCode: str,
    ):
        """Get phone verif method v2."""
        METHOD_NAME = "getPhoneVerifMethodV2"
        userPhoneNumber = [[11, 1, phoneNumber], [11, 2, countryCode]]
        params = [
            [11, 1, authSessionId],
            [12, 2, userPhoneNumber],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getSSEncryptionKey(self, authSessionId: str):
        """Get SSEncryption key."""
        METHOD_NAME = "getSSEncryptionKey"
        request = [[11, 1, authSessionId]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def requestToSendPasswordSetVerificationEmail(self, authSessionId: str, email: str):
        """Request to send password set verification email."""
        METHOD_NAME = "requestToSendPasswordSetVerificationEmail"
        request = [[11, 1, authSessionId], [11, 2, email]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def requestToSendPhonePinCode(
        self, authSessionId: str, phoneNumber: str, countryCode: str, verifMethod: int
    ):
        """Request to send phone pin code."""
        METHOD_NAME = "requestToSendPhonePinCode"
        userPhoneNumber = [[11, 1, phoneNumber], [11, 2, countryCode]]
        request = [
            [11, 1, authSessionId],
            [12, 2, userPhoneNumber],
            [8, 3, verifMethod],
        ]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def setHashedPassword(self, authSessionId: str, password: str):
        """Set hashed password."""
        METHOD_NAME = "setHashedPassword"
        request = [[11, 1, authSessionId], [11, 2, password]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def startRestoration(self, authSessionId: str, modelName: str, deviceUid: str):
        """Start restoration."""
        METHOD_NAME = "startRestoration"
        request = [[11, 1, authSessionId], [11, 2, modelName], [11, 3, deviceUid]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def verifyAccountUsingHashedPwd(
        self, authSessionId: str, v1HashedPassword: str, clientHashedPassword: str
    ):
        """Verify account using hashed pwd."""
        METHOD_NAME = "verifyAccountUsingHashedPwd"
        request = [
            [11, 1, authSessionId],
            [11, 2, v1HashedPassword],
            [11, 3, clientHashedPassword],
        ]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def verifyEapLogin(
        self, authSessionId: str, _type: int, accessToken: str, countryCode: str
    ):
        """Verify eap login."""
        METHOD_NAME = "verifyEapLogin"
        eapLogin = [[8, 1, _type], [11, 2, accessToken], [11, 3, countryCode]]
        request = [[11, 1, authSessionId], [12, 2, eapLogin]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def verifyPhonePinCode(
        self, authSessionId: str, phoneNumber: str, countryCode: str, pinCode: str
    ):
        """Verify phone pin code."""
        METHOD_NAME = "verifyPhonePinCode"
        userPhoneNumber = [[11, 1, phoneNumber], [11, 2, countryCode]]
        request = [[11, 1, authSessionId], [12, 2, userPhoneNumber], [11, 3, pinCode]]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)
