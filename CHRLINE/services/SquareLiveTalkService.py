# -*- coding: utf-8 -*-
from typing import List, Optional

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class SquareLiveTalkService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/SQLV1"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def acceptSpeakers(self, squareChatMid: str, sessionId: str, targetMids: List[str]):
        """Accept speakers."""
        METHOD_NAME = "acceptSpeakers"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [14, 3, [11, targetMids]]]
        return self.__sender.send(METHOD_NAME, params)

    def acceptToChangeRole(
        self, squareChatMid: str, sessionId: str, inviteRequestId: str
    ):
        """Accept to change role."""
        METHOD_NAME = "acceptToChangeRole"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [11, 3, inviteRequestId]]
        return self.__sender.send(METHOD_NAME, params)

    def acceptToListen(self, squareChatMid: str, sessionId: str, inviteRequestId: str):
        """Accept to listen."""
        METHOD_NAME = "acceptToListen"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [11, 3, inviteRequestId]]
        return self.__sender.send(METHOD_NAME, params)

    def acceptToSpeak(self, squareChatMid: str, sessionId: str, inviteRequestId: str):
        """Accept to speak."""
        METHOD_NAME = "acceptToSpeak"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [11, 3, inviteRequestId]]
        return self.__sender.send(METHOD_NAME, params)

    def cancelToSpeak(self, squareChatMid: str, sessionId: str):
        """Cancel to speak."""
        METHOD_NAME = "cancelToSpeak"
        params = [[11, 1, squareChatMid], [11, 2, sessionId]]
        return self.__sender.send(METHOD_NAME, params)

    def endLiveTalk(self, squareChatMid: str, sessionId: str):
        """End live talk."""
        METHOD_NAME = "endLiveTalk"
        params = [[11, 1, squareChatMid], [11, 2, sessionId]]
        return self.__sender.send(METHOD_NAME, params)

    def fetchLiveTalkEvents(
        self, squareChatMid: str, sessionId: str, syncToken: str, limit: int = 50
    ):
        """Fetch live talk events."""
        METHOD_NAME = "fetchLiveTalkEvents"
        params = [
            [11, 1, squareChatMid],
            [11, 2, sessionId],
            [11, 3, syncToken],
            [8, 4, limit],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def findLiveTalkByInvitationTicket(self, invitationTicket: str):
        """Find live talk by invitation ticket."""
        METHOD_NAME = "findLiveTalkByInvitationTicket"
        params = [[11, 1, invitationTicket]]
        return self.__sender.send(METHOD_NAME, params)

    def forceEndLiveTalk(self, squareChatMid: str, sessionId: str):
        """Force end live talk."""
        METHOD_NAME = "forceEndLiveTalk"
        params = [[11, 1, squareChatMid], [11, 2, sessionId]]
        return self.__sender.send(METHOD_NAME, params)

    def getLiveTalkInfoForNonMember(
        self, squareChatMid: str, sessionId: str, speakers: List[str]
    ):
        """Get live talk info for non-member."""
        METHOD_NAME = "getLiveTalkInfoForNonMember"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [15, 3, [11, speakers]]]
        return self.__sender.send(METHOD_NAME, params)

    def getLiveTalkInvitationUrl(self, squareChatMid: str, sessionId: str):
        """Get live talk invitation url."""
        METHOD_NAME = "getLiveTalkInvitationUrl"
        params = [[11, 1, squareChatMid], [11, 2, sessionId]]
        return self.__sender.send(METHOD_NAME, params)

    def getLiveTalkSpeakersForNonMember(
        self, squareChatMid: str, sessionId: str, speakers: List[str]
    ):
        """Get live talk speakers for non-member."""
        METHOD_NAME = "getLiveTalkSpeakersForNonMember"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [15, 3, [11, speakers]]]
        return self.__sender.send(METHOD_NAME, params)

    def getSquareInfoByChatMid(self, squareChatMid: str):
        """Get square info by chat mid."""
        METHOD_NAME = "getSquareInfoByChatMid"
        params = [[11, 1, squareChatMid]]
        return self.__sender.send(METHOD_NAME, params)

    def inviteToChangeRole(
        self, squareChatMid: str, sessionId: str, targetMid: str, targetRole: int
    ):
        """
        Invite to change role.

        - targetRole:
            HOST(1),
            CO_HOST(2),
            GUEST(3);
        """
        METHOD_NAME = "inviteToChangeRole"
        params = [
            [11, 1, squareChatMid],
            [11, 2, sessionId],
            [11, 3, targetMid],
            [8, 4, targetRole],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def inviteToListen(self, squareChatMid: str, sessionId: str, targetMid: str):
        """Invite to listen."""
        METHOD_NAME = "inviteToListen"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [11, 3, targetMid]]
        return self.__sender.send(METHOD_NAME, params)

    def inviteToLiveTalk(self, squareChatMid: str, sessionId: str, invitees: List[str]):
        """Invite to live talk."""
        METHOD_NAME = "inviteToLiveTalk"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [15, 3, [11, invitees]]]
        return self.__sender.send(METHOD_NAME, params)

    def inviteToSpeak(self, squareChatMid: str, sessionId: str, targetMid: str):
        """Invite to speak."""
        METHOD_NAME = "inviteToSpeak"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [11, 3, targetMid]]
        return self.__sender.send(METHOD_NAME, params)

    def joinLiveTalk(self, squareChatMid: str, sessionId: str, wantToSpeak: bool):
        """Join live talk."""
        METHOD_NAME = "joinLiveTalk"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [2, 3, wantToSpeak]]
        return self.__sender.send(METHOD_NAME, params)

    def kickOutLiveTalkParticipants(
        self, squareChatMid: str, sessionId: str, mid: Optional[str] = None
    ):
        """Kick out live talk participants."""
        METHOD_NAME = "kickOutLiveTalkParticipants"
        target = []
        if mid is not None:
            liveTalkParticipant = [[11, 1, mid]]
            target.append([12, 1, liveTalkParticipant])
        else:
            target.append([12, 2, []])
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [12, 3, target]]
        return self.__sender.send(METHOD_NAME, params)

    def rejectSpeakers(self, squareChatMid: str, sessionId: str, targetMids: List[str]):
        """Reject speakers."""
        METHOD_NAME = "rejectSpeakers"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [14, 3, [11, targetMids]]]
        return self.__sender.send(METHOD_NAME, params)

    def rejectToSpeak(self, squareChatMid: str, sessionId: str, inviteRequestId: str):
        """Reject to speak."""
        METHOD_NAME = "rejectToSpeak"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [11, 3, inviteRequestId]]
        return self.__sender.send(METHOD_NAME, params)

    def reportLiveTalk(self, squareChatMid: str, sessionId: str, reportType: int):
        """
        Report live talk.

        - reportType:
            ADVERTISING(1),
            GENDER_HARASSMENT(2),
            HARASSMENT(3),
            IRRELEVANT_CONTENT(4),
            OTHER(5);
        """
        METHOD_NAME = "reportLiveTalk"
        params = [[11, 1, squareChatMid], [11, 2, sessionId], [8, 3, reportType]]
        return self.__sender.send(METHOD_NAME, params)

    def reportLiveTalkSpeaker(
        self, squareChatMid: str, sessionId: str, speakerMemberMid: str, reportType: int
    ):
        """
        Report live talk speaks.

        - reportType:
            ADVERTISING(1),
            GENDER_HARASSMENT(2),
            HARASSMENT(3),
            IRRELEVANT_CONTENT(4),
            OTHER(5);
        """
        METHOD_NAME = "reportLiveTalkSpeaker"
        params = [
            [11, 1, squareChatMid],
            [11, 2, sessionId],
            [11, 3, speakerMemberMid],
            [8, 4, reportType],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def requestToListen(self, squareChatMid: str, sessionId: str):
        """Request to listen."""
        METHOD_NAME = "requestToListen"
        params = [[11, 1, squareChatMid], [11, 2, sessionId]]
        return self.__sender.send(METHOD_NAME, params)

    def requestToSpeak(self, squareChatMid: str, sessionId: str):
        """Request to speak."""
        METHOD_NAME = "requestToSpeak"
        params = [[11, 1, squareChatMid], [11, 2, sessionId]]
        return self.__sender.send(METHOD_NAME, params)

    def startLiveTalk(
        self, squareChatMid: str, title: str, _type: int = 1, speakerSetting: int = 2
    ):
        """
        Start live talk.

        - type:
            PUBLIC(1),
            PRIVATE(2);
        - speakerSetting:
            LIMITED_SPEAKERS(1),
            ALL_AS_SPEAKERS(2);
        """
        METHOD_NAME = "startLiveTalk"
        params = [
            [11, 1, squareChatMid],
            [11, 2, title],
            [8, 3, _type],
            [8, 4, speakerSetting],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def updateLiveTalkAttrs(
        self,
        squareChatMid: str,
        sessionId: str,
        updatedAttrs: List[int],
        title: Optional[str] = None,
        speakerSetting: Optional[int] = None,
        allowRequestToSpeak: Optional[bool] = None,
    ):
        """
        Update live talk attrs.

        - updatedAttrs:
            TITLE(1),
            SPEAKER_SETTING(2),
            ALLOW_REQUEST_TO_SPEAK(3);
        """
        METHOD_NAME = "updateLiveTalkAttrs"
        liveTalk = [[11, 1, squareChatMid], [11, 2, sessionId]]
        if title is not None:
            liveTalk.append([11, 3, title])
        if speakerSetting is not None:
            liveTalk.append([8, 5, speakerSetting])
        if allowRequestToSpeak is not None:
            liveTalk.append([2, 6, allowRequestToSpeak])
        params = [[14, 1, [8, updatedAttrs]], [12, 2, liveTalk]]
        return self.__sender.send(METHOD_NAME, params)

    def acquireLiveTalk(
        self,
        squareChatMid: str,
        title: str,
        _type: int = 1,
        speakerSetting: int = 2,
    ):
        """Acquire live talk."""
        METHOD_NAME = "acquireLiveTalk"
        params = [
            [11, 1, squareChatMid],
            [11, 2, title],
            [8, 3, _type],
            [8, 4, speakerSetting],
        ]
        return self.__sender.send(METHOD_NAME, params)
