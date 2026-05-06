# -*- coding: utf-8 -*-
import time
from typing import TYPE_CHECKING, Dict, List, Optional, cast

from ..serializers.DummyProtocol import DummyThrift
from .BaseService import BaseService, BaseServiceSender

if TYPE_CHECKING:
    from ..client import CHRLINE


CHANNEL_ID = "2007849914"


class CalendarBaseService(BaseService):
    def __init__(self, client: "CHRLINE"):
        self.client = client
        self._sender: Optional[BaseServiceSender] = None

    @property
    def channel_token(self):
        return self.client.channel_token_manager.getChannelAccessToken(CHANNEL_ID)

    @property
    def headers(self):
        base = self.client.server.Headers
        ext = {
            "x-line-channeltoken": self.channel_token,
        }
        return self.client.server.additionalHeaders(base, ext)

    def sendRequest(self, method_name: str, params: list, **kwargs):
        if self._sender is None:
            raise RuntimeError("Sender is not initialized.")
        kwargs["headers"] = self.headers
        return cast(DummyThrift, self._sender.send(method_name, params, **kwargs))


class CalendarService(CalendarBaseService):
    __REQ_TYPE = -2
    __RES_TYPE = -2
    __ENDPOINT = "/line.calendar.bff.CalendarService"

    def __init__(self, client: "CHRLINE"):
        super().__init__(client)
        self._sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

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


class CalendarEventService(CalendarBaseService):
    __REQ_TYPE = -2
    __RES_TYPE = -2
    __ENDPOINT = "/line.calendar.bff.EventService"

    def __init__(self, client: "CHRLINE"):
        super().__init__(client)
        self._sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def listEvents(self, calendarId: str, chatroomId: str, clientLastGetTime: int = 0):
        METHOD_NAME = "ListEvents"
        params = [
            [11, 1, calendarId],
            [11, 2, chatroomId],
            [10, 3, clientLastGetTime],
        ]
        return self.sendRequest(METHOD_NAME, params)

    def updateEvents(
        self,
        calendarId: str,
        chatroomId: str,
        events: list,
        addInviteeMids: Optional[List[str]] = None,
        removeInviteeMids: Optional[List[str]] = None,
        notifyToChatroom: bool = False,
    ):
        METHOD_NAME = "UpdateEvents"
        updates = []
        for event in events:
            update = [
                [11, 1, event[1]],  # id
                [10, 2, event[3]],  # startTime
                [10, 3, event[4]],  # endTime
                [11, 4, event[5]],  # timezone
                [11, 5, event[6]],  # title
                [2, 6, event[7]],  # isAllDay
                [11, 7, event[8]],  # location
                [11, 8, event[9]],  # url
                [11, 9, event[10]],  # description
                [11, 14, event[15]],  # messageId
                [10, 16, int(time.time())],  # clientUpdatedAt
                [2, 17, notifyToChatroom],
                [8, 18, event[20]],  # colorId
                [11, 20, event[22]],  # stampId
            ]
            if event[11] is not None:  # recurrence
                update.append([12, 10, event[11]])
            if addInviteeMids is not None:
                invitees = []
                for mid in addInviteeMids:
                    invitees.append([[11, 1, mid]])
                update.append([15, 11, [12, invitees]])
            if removeInviteeMids is not None:
                invitees = []
                for mid in removeInviteeMids:
                    invitees.append([[11, 1, mid]])
                update.append([15, 12, [12, invitees]])
            if event[13] is not None:  # reminder
                update.append([15, 13, [8, event[13]]])
            if event[16] is not None:  # recurrenceChildEvents
                update.append([15, 15, [12, event[16]]])
            if event[21] is not None:  # appReminders
                update.append([12, 19, event[21]])
            updates.append(update)
        params = [
            [11, 1, calendarId],
            [11, 2, chatroomId],
            [15, 3, [12, updates]],
        ]
        return self.sendRequest(METHOD_NAME, params)

    def createEventV1(
        self,
        calendarId: str,
        chatroomId: str,
        startTime: int,
        endTime: int,
        title: str,
        timezone: str = "Asia/Tokyo",
        isAllDay: bool = False,
        location: Optional[str] = None,
        url: Optional[str] = None,
        description: Optional[str] = None,
        recurrenceFrequency: Optional[int] = None,
        recurrenceInterval: Optional[int] = None,
        recurrenceUntil: Optional[int] = None,
        recurrenceByDay: Optional[List[str]] = None,
        recurrenceExceptIds: Optional[List[int]] = None,
        inviteeMids: Optional[Dict[str, int]] = None,
        reminder: Optional[List[int]] = None,
        messageId: Optional[str] = None,
        recurrenceChildEvents: Optional[list] = None,
        notifyToChatroom: bool = True,
        colorId: Optional[int] = None,
        appReminders=None,
        stampId: Optional[str] = None,
        _id: Optional[str] = None,
    ):
        METHOD_NAME = "CreateEvents"
        if _id is None:
            # id for error callback, because you can create multiple events at once
            _id = "fukubao"
        new_event = [
            [11, 1, _id],
            [10, 2, startTime],
            [10, 3, endTime],
            [11, 4, timezone],
            [11, 5, title],
            [2, 6, isAllDay],
            [10, 15, int(time.time())],  # clientUpdatedAt
            [2, 16, notifyToChatroom],
        ]
        if location is not None:
            new_event.append([11, 7, location])
        if url is not None:
            new_event.append([11, 8, url])
        if description is not None:
            new_event.append([11, 9, description])
        if (
            recurrenceFrequency is not None
            or recurrenceInterval is not None
            or recurrenceUntil is not None
            or recurrenceByDay is not None
            or recurrenceExceptIds is not None
        ):
            recurrence = [
                [8, 1, recurrenceFrequency],
                [8, 2, recurrenceInterval],
                [10, 3, recurrenceUntil],
                [15, 4, [11, recurrenceByDay]],
                [15, 5, [8, recurrenceExceptIds]],
            ]
            new_event.append([12, 10, recurrence])
        if inviteeMids is not None:
            invitees = [
                [[11, 1, mid], [8, 3, status]] for mid, status in inviteeMids.items()
            ]
            new_event.append([15, 11, [12, invitees]])
        if reminder is not None:
            new_event.append([15, 12, [8, reminder]])
        if messageId is not None:
            new_event.append([11, 13, messageId])
        if recurrenceChildEvents is not None:
            new_event.append([15, 14, [12, recurrenceChildEvents]])
        if colorId is not None:
            new_event.append([8, 17, colorId])
        if appReminders is not None:
            new_event.append([12, 18, appReminders])
        if stampId is not None:
            new_event.append([11, 19, stampId])
        params = [
            [11, 1, calendarId],
            [11, 2, chatroomId],
            [15, 3, [12, [new_event]]],
        ]
        return self.sendRequest(METHOD_NAME, params)

    def deleteEvents(
        self,
        calendarId: str,
        chatroomId: str,
        eventIds: Dict[str, int],
        notifyToChatroom: bool = True,
    ):
        METHOD_NAME = "DeleteEvents"
        events = []
        for eventId, clientUpdatedAt in eventIds.items():
            event = [
                [11, 1, eventId],
                [10, 2, clientUpdatedAt],
                [2, 3, notifyToChatroom],
            ]
            events.append(event)
        params = [
            [11, 1, calendarId],
            [11, 2, chatroomId],
            [15, 3, [12, events]],
        ]
        return self.sendRequest(METHOD_NAME, params)


class CalendarInvitationService(CalendarBaseService):
    __REQ_TYPE = -2
    __RES_TYPE = -2
    __ENDPOINT = "/line.calendar.bff.InvitationService"

    def __init__(self, client: "CHRLINE"):
        super().__init__(client)
        self._sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def respondToInvitation(
        self,
        chatroomId: str,
        eventId: str,
        recurId: Optional[int] = None,
        status: int = 2,
        clientUpdatedAt: Optional[int] = None,
    ):
        METHOD_NAME = "RespondToInvitation"
        if clientUpdatedAt is None:
            clientUpdatedAt = int(time.time())
        params = [
            [11, 1, chatroomId],
            [11, 2, eventId],
            [10, 3, recurId],
            [8, 4, status],
            [10, 5, clientUpdatedAt],
        ]
        return self.sendRequest(METHOD_NAME, params)
