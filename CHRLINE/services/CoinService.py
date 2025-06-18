# -*- coding: utf-8 -*-
from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class CoinService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/COIN4"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def getTotalCoinBalance(self, appStoreCode: int):
        """Get total coin balance."""
        METHOD_NAME = "getTotalCoinBalance"
        params = [[12, 1, [[8, 1, appStoreCode]]]]
        return self.__sender.send(METHOD_NAME, params)

    def getCoinPurchaseHistory(self):
        METHOD_NAME = "getCoinPurchaseHistory"
        raise NotImplementedError
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getCoinProducts(self):
        METHOD_NAME = "getCoinProducts"
        raise NotImplementedError
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def reserveCoinPurchase(self):
        METHOD_NAME = "reserveCoinPurchase"
        raise NotImplementedError
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getCoinUseAndRefundHistory(self):
        METHOD_NAME = "getCoinUseAndRefundHistory"
        raise NotImplementedError
        params = []
        return self.__sender.send(METHOD_NAME, params)
