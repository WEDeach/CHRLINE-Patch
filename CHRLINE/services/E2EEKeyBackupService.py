# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class E2EEKeyBackupService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/EKBS4"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def createE2EEKeyBackup(self, blobHeader: str, blobPayload: str, reason: int):
        """
        - reason
            UNKNOWN(0),
            BACKGROUND_NEW_KEY_CREATED(1),
            BACKGROUND_PERIODICAL_VERIFICATION(2),
            FOREGROUND_NEW_PIN_REGISTERED(3),
            FOREGROUND_VERIFICATION(4);
        """
        METHOD_NAME = "createE2EEKeyBackup"
        params = [[12, 2, [[11, 1, blobHeader], [11, 2, blobPayload], [8, 3, reason]]]]
        return self.__sender.send(METHOD_NAME, params)

    def getE2EEKeyBackupCertificates(self):
        METHOD_NAME = "getE2EEKeyBackupCertificates"
        params = [[12, 2, []]]
        return self.__sender.send(METHOD_NAME, params)

    def getE2EEKeyBackupInfo(self):
        METHOD_NAME = "getE2EEKeyBackupInfo"
        params = [[12, 2, []]]
        return self.__sender.send(METHOD_NAME, params)
