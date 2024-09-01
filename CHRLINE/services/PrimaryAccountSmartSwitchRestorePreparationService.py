# -*- coding: utf-8 -*-
from typing import Any

from .BaseService import BaseService, BaseServiceSender, BaseServiceStruct


class PrimaryAccountSmartSwitchRestorePreparationService(BaseService):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/EXT/auth/feature-user/thrift/account/v1/restore/smart-switch/prepare"

    def __init__(self, client: Any):
        self.__sender = BaseServiceSender(
            client,
            "PrimaryAccountSmartSwitchRestorePreparationService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def createSession(
        self,
    ):
        """Create smart-switch session."""
        METHOD_NAME = "createSession"
        request = []
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)

    def registerSSEncryptionKey(
        self,
        authSessionId: str,
        keyMaterial: str,
    ):
        """Register SSEncryption key."""
        METHOD_NAME = "registerSSEncryptionKey"
        encryptionKey = [
            [11, 1, keyMaterial],
        ]
        request = [
            [11, 1, authSessionId],
            [12, 2, encryptionKey],
        ]
        params = BaseServiceStruct.BaseRequest(request)
        return self.__sender.send(METHOD_NAME, params)
