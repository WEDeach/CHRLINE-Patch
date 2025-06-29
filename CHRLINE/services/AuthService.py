# -*- coding: utf-8 -*-
from typing import Dict, Optional

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class AuthService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/RS4"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def confirmIdentifier(
        self,
        authSessionId: str,
        verificationCode: str,
        metaData: Dict[str, str] = {},
        forceRegistration: Optional[bool] = None,
    ):
        METHOD_NAME = "confirmIdentifier"
        confirmationRequest = [
            [13, 1, [11, 11, metaData]],
            [2, 2, forceRegistration],
            [11, 3, verificationCode],
        ]
        request = [
            [12, 5, confirmationRequest],
        ]
        params = [[11, 2, authSessionId], [12, 3, request]]
        return self.__sender.send(METHOD_NAME, params)

    def removeIdentifier(
        self,
        authSessionId: str,
        cipherKeyId: str,
        cipherText: str,
        identityProvider: int = 1,
    ):
        METHOD_NAME = "removeIdentifier"
        request = [
            [8, 2, identityProvider],
            [11, 3, cipherKeyId],
            [11, 4, cipherText],
        ]
        params = [[11, 2, authSessionId], [12, 3, request]]
        return self.__sender.send(METHOD_NAME, params)

    def resendIdentifierConfirmation(
        self,
        authSessionId: str,
    ):
        METHOD_NAME = "resendIdentifierConfirmation"
        request = []
        params = [[11, 2, authSessionId], [12, 3, request]]
        return self.__sender.send(METHOD_NAME, params)

    def setIdentifier(
        self,
        authSessionId: str,
        cipherKeyId: str,
        cipherText: str,
        identityProvider: int = 1,
        metaData: Dict[str, str] = {},
    ):
        METHOD_NAME = "setIdentifier"
        request = [
            [13, 1, [11, 11, metaData]],
            [8, 2, identityProvider],
            [11, 3, cipherKeyId],
            [11, 4, cipherText],
        ]
        params = [[11, 2, authSessionId], [12, 3, request]]
        return self.__sender.send(METHOD_NAME, params)

    def updateIdentifier(
        self,
        authSessionId: str,
        cipherKeyId: str,
        cipherText: str,
        identityProvider: int = 1,
        metaData: Dict[str, str] = {},
    ):
        METHOD_NAME = "updateIdentifier"
        request = [
            [13, 1, [11, 11, metaData]],
            [8, 2, identityProvider],
            [11, 3, cipherKeyId],
            [11, 4, cipherText],
        ]
        params = [[11, 2, authSessionId], [12, 3, request]]
        return self.__sender.send(METHOD_NAME, params)

    def getAuthRSAKey(self, authSessionId: str, identityProvider: int = 1):
        METHOD_NAME = "getAuthRSAKey"
        params = [[11, 2, authSessionId], [8, 3, identityProvider]]
        return self.__sender.send(METHOD_NAME, params)

    def issueTokenForAccountMigrationSettings(self, enforce: bool):
        METHOD_NAME = "issueTokenForAccountMigrationSettings"
        params = [[2, 2, enforce]]
        return self.__sender.send(METHOD_NAME, params)

    def issueV3TokenForPrimary(self, udid: str, systemDisplayName: str, modelName: str):
        METHOD_NAME = "issueV3TokenForPrimary"
        params = [
            [12, 1, [[11, 1, udid], [11, 2, systemDisplayName], [11, 3, modelName]]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def openAuthSession(self, metaData: Dict[str, str] = {}):
        METHOD_NAME = "openAuthSession"
        request = [[13, 1, [11, 11, metaData]]]
        params = [[12, 2, request]]
        return self.__sender.send(METHOD_NAME, params)

    def respondE2EELoginRequest(
        self,
        verifier,
        keyId,
        keyData,
        createdTime,
        encryptedKeyChain,
        hashKeyChain,
        errorCode: int = 95,
    ):
        METHOD_NAME = "respondE2EELoginRequest"
        publicKey = [
            [8, 1, 1],  # version
            [8, 2, keyId],
            [11, 4, keyData],
            [10, 5, createdTime],
        ]
        params = [
            [11, 1, verifier],
            [12, 2, publicKey],
            [11, 3, encryptedKeyChain],
            [11, 4, hashKeyChain],
            [8, 5, errorCode],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def loginFromClova(self, authSessionId, cipherText, metaData={}):
        METHOD_NAME = "loginFromClova"
        params = [
            [11, 2, authSessionId],
            [12, 3, [[8, 1, 2], [13, 2, [11, 11, metaData]], [11, 3, cipherText]]],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def validateClovaRequest(self, authSessionId, cipherText, metaData={}):
        METHOD_NAME = "validateClovaRequest"
        params = [
            [11, 2, authSessionId],
            [12, 3, [[8, 1, 2], [13, 2, [11, 11, metaData]], [11, 3, cipherText]]],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def setClovaCredential(self, authSessionId, cipherText, metaData={}):
        METHOD_NAME = "setClovaCredential"
        params = [
            [11, 2, authSessionId],
            [
                12,
                3,
                [
                    [8, 1, 2],  # authLoginVersion
                    [13, 2, [11, 11, metaData]],
                    [11, 3, cipherText],
                ],
            ],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def validateClovaAppToken(self, authSessionId, cipherText, metaData={}):
        METHOD_NAME = "validateClovaAppToken"
        params = [
            [11, 2, authSessionId],
            [
                12,
                3,
                [
                    [8, 1, 2],  # authLoginVersion
                    [13, 2, [11, 11, metaData]],
                    [11, 3, cipherText],
                ],
            ],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def logoutZ(self):
        METHOD_NAME = "logoutZ"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def logoutV2(self):
        METHOD_NAME = "logoutV2"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def releaseLockScreen(self, authSessionId: str, cipherKeyId: str, cipherText: str):
        """
        TODO: 2022/02/25
        """
        METHOD_NAME = "releaseLockScreen"
        params = [
            [11, 2, authSessionId],
            [
                12,
                3,
                [
                    [13, 1, [11, 11, {}]],
                    [11, 2, cipherKeyId],
                    [11, 3, cipherText],
                ],
            ],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def exchangeKey(
        self, authSessionId: str, authKeyVersion: int, publicKey: str, nonce: str
    ):
        METHOD_NAME = "exchangeKey"
        params = [
            [11, 2, authSessionId],
            [
                12,
                3,
                [
                    [8, 1, authKeyVersion],
                    [11, 2, publicKey],
                    [11, 3, nonce],
                ],
            ],
        ]
        return self.__sender.send(METHOD_NAME, params)
