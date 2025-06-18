# -*- coding: utf-8 -*-
from typing import Optional

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender, BaseServiceStruct


class OaChatService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/ext/oachat/api/"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            "OaCallStatusService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def getCallStatus(
        self,
        basicSearchId: str,
        otp: Optional[str] = None,
    ):
        """Get call status."""
        METHOD_NAME = "getCallStatus"
        params = [
            [11, 1, basicSearchId],
            [11, 2, otp],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
