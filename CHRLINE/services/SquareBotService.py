# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class SquareBotService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/BP1"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )
        
    def getSquareBot(self, botMid):
        METHOD_NAME = "getSquareBot"
        params = [
            [12, 1, [
                [11, 1, botMid]
            ]]
        ]
        return self.__sender.send(METHOD_NAME, params)