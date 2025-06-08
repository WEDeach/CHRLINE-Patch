# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class BotExternalService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/BOTE"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def notifyOATalkroomEvents(
        self, eventId: list, type: list, context: list, content: list
    ):
        METHOD_NAME = "notifyOATalkroomEvents"
        OATalkroomEvent = []
        for eId in eventId:
            OATalkroomEvent.append(
                [
                    [11, 1, eId],
                    [8, 2, type],
                    # [12, 3, context],
                    # [12, 4, content],
                ]
            )
        params = [[12, 1, [[15, 1, [12, OATalkroomEvent]]]]]
        return self.__sender.send(METHOD_NAME, params)

    def notifyChatAdEntry(self, chatMid: str, scenarioId: str, sdata: str):
        METHOD_NAME = "notifyChatAdEntry"
        params = [[12, 1, [[11, 1, chatMid], [11, 2, scenarioId], [11, 3, sdata]]]]
        return self.__sender.send(METHOD_NAME, params)
