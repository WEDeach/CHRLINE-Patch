# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

from .BaseService import BaseService, BaseServiceSender, BaseServiceStruct

if TYPE_CHECKING:
    from ..client import CHRLINE


class PremiumStatusService(BaseService):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/EXT/line-premium/common/thrift/status"

    def __init__(self, client: "CHRLINE"):
        self.client = client
        self.__sender = BaseServiceSender(
            self.client,
            "PremiumStatusService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def getPremiumStatus(
        self,
    ):
        """Get premium status."""
        METHOD_NAME = "getPremiumStatus"
        params = []
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getPremiumStatusForUpgrade(
        self,
    ):
        """Get premium status for upgrade."""
        METHOD_NAME = "getPremiumStatusForUpgrade"
        params = []
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getDataRetention(
        self,
    ):
        """Get data retention."""
        METHOD_NAME = "getDataRetention"
        params = []
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getIncentiveStatus(
        self,
    ):
        """Get incentive status."""
        METHOD_NAME = "getIncentiveStatus"
        params = []
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
