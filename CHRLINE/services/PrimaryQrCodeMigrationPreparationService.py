# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class PrimaryQrCodeMigrationPreparationService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/EXT/auth/feature-user/api/primary/mig/qr/prepare"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def createQRMigrationSession(self):
        METHOD_NAME = "createSession"
        params = [[12, 1, []]]
        return self.__sender.send(METHOD_NAME, params)

    def sendEncryptedE2EEKey(
        self, sessionId: str, recoveryKey: bytes, backupBlobPayload: bytes
    ):
        METHOD_NAME = "sendEncryptedE2EEKey"
        params = [
            [
                12,
                1,
                [
                    [11, 1, sessionId],
                    [12, 2, [[11, 1, recoveryKey], [11, 2, backupBlobPayload]]],
                ],
            ]
        ]
        return self.__sender.send(METHOD_NAME, params)
