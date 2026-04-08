# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

from .BaseService import BaseService, BaseServiceSender

if TYPE_CHECKING:
    from ..client import CHRLINE


CHANNEL_ID = "2007849914"


class CalendarService(BaseService):
    __REQ_TYPE = -2
    __RES_TYPE = -2
    __ENDPOINT = "/line.calendar.bff.CalendarService"

    def __init__(self, client: "CHRLINE"):
        self.client = client
        self.__token = None
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    @property
    def channel_token(self):
        # TODO: renew token when expired
        if self.__token is None:
            self.__token = self.client.checkAndGetValue(
                self.client.approveChannelAndIssueChannelToken(CHANNEL_ID),
                "channelAccessToken",
                5,
            )
        return self.__token

    @property
    def headers(self):
        base = self.client.server.Headers
        ext = {
            "x-line-channeltoken": self.channel_token,
        }
        return self.client.server.additionalHeaders(base, ext)

    def sendRequest(self, method_name: str, params: list, **kwargs):
        kwargs["headers"] = self.headers
        return self.__sender.send(method_name, params, **kwargs)

    def listAllCalendars(self):
        METHOD_NAME = "ListAllCalendars"
        params = []
        return self.sendRequest(METHOD_NAME, params)

    def getChatCalendar(self, chatroomId: str):
        METHOD_NAME = "GetChatCalendar"
        params = [[11, 1, chatroomId]]
        return self.sendRequest(METHOD_NAME, params)

    def updateCalendars(self, calendars: list):
        METHOD_NAME = "UpdateCalendars"
        updates = []
        for calendar in calendars:
            update = [
                [11, 1, calendar[2]],  # id
                [11, 2, calendar[7]],  # chatroomId
                [11, 3, calendar[1]],  # name
                [8, 4, calendar[6]],  # colorId
                [2, 5, calendar[3]],  # isVisible
                [2, 6, calendar[4]],  # isFavorite
                [10, 7, calendar[11]],  # clientUpdatedAt
                [2, 8, calendar[13]],  # isReminderEnabled
                [2, 9, calendar[15]],  # isShownInCalendarList
            ]
            updates.append(update)
        params = [[15, 1, [12, updates]]]
        return self.sendRequest(METHOD_NAME, params)

    def createChatCalendar(self, chatroomId: str):
        METHOD_NAME = "CreateChatCalendar"
        params = [[11, 1, chatroomId]]
        return self.sendRequest(METHOD_NAME, params)

    def createPersonalCalendar(self, _id: str, name: str, colorId: int):
        METHOD_NAME = "CreatePersonalCalendar"
        params = [
            [11, 1, _id],
            [11, 2, name],
            [8, 3, colorId],
        ]
        return self.sendRequest(METHOD_NAME, params)

    def deletePersonalCalendar(self, _id: str, clientUpdatedAt: int):
        METHOD_NAME = "DeletePersonalCalendar"
        params = [
            [11, 1, _id],
            [10, 2, clientUpdatedAt],
        ]
        return self.sendRequest(METHOD_NAME, params)
