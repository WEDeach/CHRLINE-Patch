# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class PrimaryQrCodeMigrationLongPollingService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/EXT/auth/feature-user/lp/api/primary/mig/qr"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )
        
    def checkIfEncryptedE2EEKeyReceived(self, sessionId: str, newDevicePublicKey: bytes, encryptedQrIdentifier: str):
        METHOD_NAME = "checkIfEncryptedE2EEKeyReceived"
        params = [
            [11, 1, sessionId],
            [12, 2, [
                [11, 1, newDevicePublicKey],
                [11, 2, encryptedQrIdentifier]
            ]]
        ]
        params = [
            [12, 1, params]
        ]
        return self.__sender.send(METHOD_NAME, params)