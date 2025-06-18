# -*- coding: utf-8 -*-
import uuid
from typing import Dict

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender, BaseServiceStruct


class PrimaryAccountInitService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/acct/pais/v1"

    def __init__(self):
        self.register_headers = self.client.server.Headers
        self.uuid = uuid.uuid4().hex
        self.__sender = BaseServiceSender(
            self.client,
            "PrimaryAccountInitService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def setPrimaryUuid(self, uuid):
        self.uuid = uuid

    def openPrimarySession(self, metaData: Dict[str, str] = {}):
        """open session for primary."""
        METHOD_NAME = "openSession"
        params = [
            [13, 1, [11, 11, metaData]],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getCountryInfo(
        self,
        authSessionId: str,
        countryCode: str = "TW",
        hni: str = "46601",
        carrierName: str = "Far EasTone Telecommunications Co Ltd",
    ):
        """get country info for primary."""
        METHOD_NAME = "getCountryInfo"
        simCard = [
            [11, 1, countryCode],
            [11, 2, hni],
            [11, 3, carrierName],
        ]
        params = [
            [11, 1, authSessionId],
            [12, 11, simCard],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getPhoneVerifMethod(
        self, authSessionId, phoneNumber, countryCode, deviceModel="SM-N950F"
    ):
        METHOD_NAME = "getPhoneVerifMethod"
        params = [
            [11, 1, authSessionId],
            [12, 2, [[11, 1, self.uuid], [11, 2, deviceModel]]],
            [12, 3, [[11, 1, phoneNumber], [11, 2, countryCode]]],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def sendPinCodeForPhone(
        self, authSessionId, phoneNumber, countryCode, deviceModel="SM-N950F"
    ):
        METHOD_NAME = "sendPinCodeForPhone"
        params = [
            [11, 1, authSessionId],
            [12, 2, [[11, 1, self.uuid], [11, 2, deviceModel]]],
            [12, 3, [[11, 1, phoneNumber], [11, 2, countryCode]]],
            [8, 4, 2],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def verifyPhone(
        self, authSessionId, phoneNumber, countryCode, pinCode, deviceModel="SM-N950F"
    ):
        METHOD_NAME = "verifyPhone"
        params = [
            [11, 1, authSessionId],
            [12, 2, [[11, 1, self.uuid], [11, 2, deviceModel]]],
            [12, 3, [[11, 1, phoneNumber], [11, 2, countryCode]]],
            [11, 4, pinCode],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def validateProfile(self, authSessionId, displayName):
        METHOD_NAME = "validateProfile"
        params = [[11, 1, authSessionId], [11, 2, displayName]]
        return self.__sender.send(METHOD_NAME, params)

    def exchangeEncryptionKey(self, authSessionId, publicKey, nonce, authKeyVersion=1):
        METHOD_NAME = "exchangeEncryptionKey"
        params = [
            [11, 1, authSessionId],
            [
                12,
                2,
                [
                    [8, 1, authKeyVersion],
                    [11, 2, publicKey],
                    [11, 3, nonce],
                ],
            ],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def setPassword(self, authSessionId, cipherText, encryptionKeyVersion=1):
        METHOD_NAME = "setPassword"
        params = [
            [11, 1, authSessionId],
            [
                12,
                2,
                [
                    [8, 1, encryptionKeyVersion],
                    [11, 2, cipherText],
                ],
            ],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def registerPrimaryUsingPhone(self, authSessionId):
        METHOD_NAME = "registerPrimaryUsingPhone"
        params = [[11, 2, authSessionId]]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getPhoneVerifMethodV2(
        self, authSessionId, phoneNumber, countryCode, deviceModel="SM-N950F"
    ):
        METHOD_NAME = "getPhoneVerifMethodV2"
        params = [
            [11, 1, authSessionId],
            [12, 2, [[11, 1, self.uuid], [11, 2, deviceModel]]],
            [12, 3, [[11, 1, phoneNumber], [11, 2, countryCode]]],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def requestToSendPhonePinCode(
        self,
        authSessionId: str,
        phoneNumber: str,
        countryCode: str = "TW",
        verifMethod: int = 1,
    ):
        """Request to send phone pin code for primary."""
        METHOD_NAME = "requestToSendPhonePinCode"
        params = [
            [11, 1, authSessionId],
            [12, 2, [[11, 1, phoneNumber], [11, 2, countryCode]]],
            [8, 3, verifMethod],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def verifyPhonePinCode(
        self, authSessionId: str, phoneNumber: str, countryCode: str, pinCode: str
    ):
        """Verify phone pin code for primary."""
        METHOD_NAME = "verifyPhonePinCode"
        params = [
            [11, 1, authSessionId],
            [12, 2, [[11, 1, phoneNumber], [11, 2, countryCode]]],
            [11, 3, pinCode],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def verifyAccountUsingPwd(self, authSessionId, identifier, countryCode, cipherText):
        METHOD_NAME = "verifyAccountUsingPwd"
        params = [
            [11, 1, authSessionId],
            [
                12,
                2,
                [[8, 1, 1], [11, 2, identifier], [11, 3, countryCode]],  # type
            ],
            [12, 3, [[8, 1, 1], [11, 2, cipherText]]],  # encryptionKeyVersion
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def registerPrimaryUsingPhoneWithTokenV3(self, authSessionId):
        METHOD_NAME = "registerPrimaryUsingPhoneWithTokenV3"
        params = [[11, 2, authSessionId]]
        return self.__sender.send(METHOD_NAME, params)

    def registerPrimaryWithTokenV3(self, authSessionId):
        METHOD_NAME = "registerPrimaryWithTokenV3"
        params = [[11, 2, authSessionId]]
        return self.__sender.send(METHOD_NAME, params)

    def lookupAvailableEap(self, authSessionId):
        """lookup available eap for primary."""
        METHOD_NAME = "lookupAvailableEap"
        params = [
            [11, 1, authSessionId],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getAllowedRegistrationMethod(self, authSessionId: str, countryCode: str):
        """
        Get allowed registration method.

        ---
        1: Phone - getPhoneVerifMethodV2
        2: Eap   - verifyEapAccountForRegistration
        """
        METHOD_NAME = "getAllowedRegistrationMethod"
        params = [
            [11, 1, authSessionId],
            [11, 2, countryCode],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def verifyEapAccountForRegistration(
        self,
        authSessionId: str,
        _type: int,
        accessToken: str,
        countryCode: str,
        deviceModel="SM-N950F",
    ):
        """
        Verify eap account for registration.

        - type:
            UNKNOWN(0),
            FACEBOOK(1),
            APPLE(2),
            GOOGLE(3);
        """
        METHOD_NAME = "verifyEapAccountForRegistration"
        params = [
            [11, 1, authSessionId, "authSessionId"],
            [
                12,
                2,
                [[11, 1, self.uuid, "udid"], [11, 2, deviceModel, "deviceModel"]],
                "device",
                "Device",
            ],
            [
                12,
                3,
                [
                    [8, 1, _type, "type"],
                    [11, 2, accessToken, "accessToken"],
                    [11, 3, countryCode, "accessToken"],
                ],
                "socialLogin",
                "SocialLogin",
            ],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def registerPrimaryUsingEapAccount(self, authSessionId):
        METHOD_NAME = "registerPrimaryUsingEapAccount"
        params = [[11, 1, authSessionId]]
        return self.__sender.send(METHOD_NAME, params)

    def getPhoneVerifMethodForRegistration(
        self,
        authSessionId: str,
        phoneNumber: str,
        countryCode: str,
        deviceModel="SM-N950F",
    ):
        """Get phone verif method for registration."""
        METHOD_NAME = "getPhoneVerifMethodForRegistration"
        params = [
            [11, 1, authSessionId],
            [12, 2, [[11, 1, self.uuid], [11, 2, deviceModel]]],
            [12, 3, [[11, 1, phoneNumber], [11, 2, countryCode]]],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getAcctVerifMethod(
        self,
        authSessionId: str,
        identifier: str,
        _type: int = 1,
        countryCode="TW",
    ):
        """Get acct verif method for registration."""
        METHOD_NAME = "getAcctVerifMethod"
        accountIdentifier = [
            [8, 1, _type],
            [11, 2, identifier],
            [11, 11, countryCode],
        ]
        params = [
            [11, 1, authSessionId],
            [12, 2, accountIdentifier],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getPasswordHashingParametersForPwdReg(self, authSessionId: str):
        """Get password hashing parameters for pwd reg."""
        METHOD_NAME = "getPasswordHashingParametersForPwdReg"
        params = [
            [11, 1, authSessionId],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def setHashedPassword(self, authSessionId: str, password: str):
        """Set hashed password for pwd reg."""
        METHOD_NAME = "setHashedPassword"
        params = [
            [11, 1, authSessionId],
            [11, 2, password],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
