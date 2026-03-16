# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class OaMembershipService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    # __ENDPOINT = "/EXT/bot/oafan"
    __ENDPOINT = "/EXT/oafan/api"  # 2026/03/16

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def activateSubscription(self, uniqueKey: str, activeStatus: int = 1):
        """
        - activeStatus:
            INACTIVE(0),
            ACTIVE(1);
        """
        METHOD_NAME = "activateSubscription"
        params = [[12, 1, [[11, 1, uniqueKey], [8, 2, activeStatus]]]]
        return self.__sender.send(METHOD_NAME, params)

    def activateMembership(self, uniqueKey: str, activeStatus: int = 1):
        """
        - activeStatus:
            INACTIVE(0),
            ACTIVE(1);
        """
        METHOD_NAME = "activateMembership"
        params = [[12, 1, [[11, 1, uniqueKey], [8, 2, activeStatus]]]]
        return self.__sender.send(METHOD_NAME, params)

    def getJoinedMembership(self, uniqueKey: str):
        METHOD_NAME = "getJoinedMembership"
        params = [
            [
                12,
                1,
                [
                    [11, 1, uniqueKey],
                ],
            ]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getJoinedMemberships(self):
        METHOD_NAME = "getJoinedMemberships"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getOrderInfo(self, uniqueKey: str):
        METHOD_NAME = "getOrderInfo"
        params = [
            [
                12,
                1,
                [
                    [11, 1, uniqueKey],
                ],
            ]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def reserve(self, uniqueKey: str):
        METHOD_NAME = "reserve"
        params = [[11, 1, uniqueKey]]
        request = [[12, 1, params]]
        return self.__sender.send(METHOD_NAME, request)

    def getJoinedMembershipByBotMid(self, botMid: str):
        METHOD_NAME = "getJoinedMembershipByBotMid"
        params = [[11, 1, botMid]]
        request = [[12, 1, params]]
        return self.__sender.send(METHOD_NAME, request)

    def getSCC(self, basicSearchId: str):
        METHOD_NAME = "getSCC"
        params = [[11, 1, basicSearchId]]
        request = [[12, 1, params]]
        return self.__sender.send(METHOD_NAME, request)

    def getPublishedMemberships(self, basicSearchId: str):
        METHOD_NAME = "getPublishedMemberships"
        params = [[11, 1, basicSearchId]]
        request = [[12, 1, params]]
        return self.__sender.send(METHOD_NAME, request)

    def getPurchaseEnabledStatus(self, uniqueKey: str):
        METHOD_NAME = "getPurchaseEnabledStatus"
        params = [[11, 1, uniqueKey]]
        request = [[12, 1, params]]
        return self.__sender.send(METHOD_NAME, request)
