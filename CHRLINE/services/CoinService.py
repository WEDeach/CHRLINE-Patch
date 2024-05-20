# -*- coding: utf-8 -*-
from .BaseService import BaseService


class CoinService(BaseService):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/COIN4"

    def __init__(self):
        pass

    def getTotalCoinBalance(self, appStoreCode: int):
        """Get total coin balance."""
        METHOD_NAME = "getTotalCoinBalance"
        params = [[12, 1, [[8, 1, appStoreCode]]]]
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.__REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.__ENDPOINT, sqrd, self.__RES_TYPE
        )

    def getCoinPurchaseHistory(self):
        METHOD_NAME = "getCoinPurchaseHistory"
        raise NotImplementedError
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.__REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.__ENDPOINT, sqrd, self.__RES_TYPE
        )

    def getCoinProducts(self):
        METHOD_NAME = "getCoinProducts"
        raise NotImplementedError
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.__REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.__ENDPOINT, sqrd, self.__RES_TYPE
        )

    def reserveCoinPurchase(self):
        METHOD_NAME = "reserveCoinPurchase"
        raise NotImplementedError
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.__REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.__ENDPOINT, sqrd, self.__RES_TYPE
        )

    def getCoinUseAndRefundHistory(self):
        METHOD_NAME = "getCoinUseAndRefundHistory"
        raise NotImplementedError
        params = []
        sqrd = self.generateDummyProtocol(METHOD_NAME, params, self.__REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            self.__ENDPOINT, sqrd, self.__RES_TYPE
        )
