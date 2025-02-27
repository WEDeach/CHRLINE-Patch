# -*- coding: utf-8 -*-
from random import randint
from typing import TYPE_CHECKING, Any, ByteString, List, Optional, Union

import httpx

from ..helper import ChrHelperProtocol
from ..helpers.bulders.message import Message as WrappedMessage
from ..serializers.DummyProtocol import DummyThrift
from .BaseService import (
    BaseServiceHandler,
    BaseServiceSender,
    BaseServiceStruct,
)

try:
    from ..exceptions import LineServiceException
    from .thrift.ttypes import TalkException
except:
    pass
if TYPE_CHECKING:
    from ..client import CHRLINE


class TalkService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/S4"

    def __init__(self):

        self.sync_conn = httpx.Client(http2=True)
        self.talk_handler = TalkServiceHandler(self.client)

        self._logger = self.client.get_logger("SERVICE").overload("TALK")
        self.__sender = BaseServiceSender(
            self.client,
            "TalkService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )
        self._logger.info("INIT!")

    def sendMessage(
        self,
        to: str,
        text: Optional[str],
        contentType: int = 0,
        contentMetadata: Optional[dict] = None,
        relatedMessageId: Optional[str] = None,
        location: Optional[dict] = None,
        chunk: Optional[list] = None,
        squareChatMid: Optional[str] = None,
        autoE2EE: bool = True,
    ):
        if contentMetadata is None:
            contentMetadata = {}

        METHOD_NAME = "sendMessage"
        SERVICE_NAME = "TalkService"
        RES_TYPE = self.__RES_TYPE
        ENDPOINT = self.__ENDPOINT
        relatedMessageServiceCode = 1
        TO_TYPE = self.client.getToType(to)

        if TO_TYPE == 4:
            SERVICE_NAME = "SquareService"
            RES_TYPE = 4
            ENDPOINT = "/SQ1"
            relatedMessageServiceCode = 2
        elif TO_TYPE == 7:
            SERVICE_NAME = "SquareService"
            METHOD_NAME = "sendSquareThreadMessage"
            RES_TYPE = 4
            ENDPOINT = "/SQ1"
            relatedMessageServiceCode = 2

        message = [
            [11, 2, to],
            [10, 5, 0],  # createdTime
            [10, 6, 0],  # deliveredTime
            [2, 14, False],  # hasContent
            [8, 15, contentType],
            [13, 18, [11, 11, contentMetadata]],
            [3, 19, 0],  # sessionId
        ]
        if text is not None:
            message.append([11, 10, text])
        if location is not None:
            locationObj = [
                [11, 1, location.get(1, "CHRLINE API")],
                [11, 2, location.get(2, "https://github.com/DeachSword/CHRLINE")],
                [4, 3, location.get(3, 0)],
                [4, 4, location.get(4, 0)],
                [11, 6, location.get(6, "PC0")],
                [8, 7, location.get(7, 2)],
            ]
            message.append([12, 11, locationObj])
        if chunk is not None:
            message.append([15, 20, [11, chunk]])
        if relatedMessageId is not None:
            message.append([11, 21, relatedMessageId])
            message.append(
                # messageRelationType; FORWARD(0), AUTO_REPLY(1), SUBORDINATE(2), REPLY(3);
                [8, 22, 3]
            )
            message.append([8, 24, relatedMessageServiceCode])
        params = [
            [8, 1, self.client.getCurrReqId()],
            [12, 2, message],
        ]
        if TO_TYPE == 4:
            params = [
                [8, 1, self.client.getCurrReqId("sq")],
                [11, 2, to],
                [12, 3, [[12, 1, message]]],
            ]
            params = [[12, 1, params]]
        elif TO_TYPE == 7:
            assert squareChatMid
            threadMessage = [
                [12, 1, message],
                [8, 3, 5],
            ]
            params = [
                [8, 1, self.client.getCurrReqId("sq")],
                [11, 2, squareChatMid],
                [11, 3, to],
                [12, 4, threadMessage],
            ]
            params = [[12, 1, params]]
        else:
            params = [
                [8, 1, self.client.getCurrReqId()],
                [12, 2, message],
            ]
        try:
            return self.__sender.send(
                METHOD_NAME,
                params,
                **{
                    "path": ENDPOINT,
                    "ttype": RES_TYPE,
                    "readWith": f"{SERVICE_NAME}.{METHOD_NAME}",
                },
            )
        except (LineServiceException, TalkException) as e:
            if getattr(e, "code") in [82, 99]:
                if autoE2EE:
                    self._logger.warn("auto encrypt msg for E2EE...")
                    return self.sendMessageWithE2EE(
                        to, text, contentType, contentMetadata, relatedMessageId
                    )
            raise e
        except Exception as e:
            raise e

    def replyMessage(
        self,
        msgData: Union[dict, WrappedMessage],
        text: Any,
        contentType: int = 0,
        contentMetadata: Optional[dict] = None,
        location: Optional[dict] = None,
        relatedMessageId: Optional[str] = None,
        squareChatMid: Optional[str] = None,
    ):
        to = self.client.checkAndGetValue(msgData, "to", 2)
        toType = self.client.checkAndGetValue(msgData, "toType", 3)
        if contentMetadata is None:
            contentMetadata = {}
        if relatedMessageId is None:
            relatedMessageId = self.client.checkAndGetValue(msgData, "id", 4)
        opType = self.client.checkAndGetValue(msgData, "opType")
        if toType == 0 and opType in [26, None]:  # opType for hooks
            to = self.client.checkAndGetValue(msgData, "_from", 1)
            if isinstance(msgData, WrappedMessage):
                to = msgData.sender.mid
        elif toType == 7:
            if squareChatMid is None:
                squareChatMid = self.client.checkAndGetValue(msgData, "squareChatMid")
            assert squareChatMid
        if to is None:
            raise ValueError("`to` is required.")
        if self.client.checkAndGetValue(msgData, "isE2EE") is True:
            if contentType == 15:
                text = location  # difference
            return self.sendMessageWithE2EE(
                to, text, contentType, contentMetadata, relatedMessageId
            )
        return self.sendMessage(
            to,
            text,
            contentType,
            contentMetadata,
            relatedMessageId,
            squareChatMid=squareChatMid,
        )

    def sendContact(self, to, mid, displayName=None):
        if displayName is None:
            contentMetadata = {"mid": mid}
        else:
            contentMetadata = {"mid": mid, "displayName": displayName}
        return self.sendMessage(
            to, None, contentType=13, contentMetadata=contentMetadata
        )

    def sendLocation(self, to, title, la=0.0, lb=0.0, subTile="CHRLINE API"):
        data = {1: title, 2: subTile, 3: la, 4: lb}
        return self.sendMessage(to, None, contentType=15, location=data)

    def sendLocationMessage(self, to, title, la=0.0, lb=0.0, subTile="CHRLINE API"):
        data = {1: title, 2: subTile, 3: la, 4: lb}
        return self.sendMessage(to, "test", location=data)

    def sendGift(self, to, productId, productType):
        if productType not in ["theme", "sticker"]:
            raise Exception("Invalid productType value")
        contentMetadata = {
            "MSGTPL": str(randint(0, 12)),
            "PRDTYPE": productType.upper(),
            "STKPKGID" if productType == "sticker" else "PRDID": productId,
        }
        return self.sendMessage(
            to=to, text="", contentMetadata=contentMetadata, contentType=9
        )

    def sendMessageWithE2EE(
        self,
        to,
        text,
        contentType=0,
        contentMetadata=None,
        relatedMessageId=None,
        renewKey=False,
    ):
        if contentMetadata is None:
            contentMetadata = {}
        chunk = self.client.encryptE2EEMessage(
            to, text, contentType=contentType, renewKey=renewKey
        )
        contentMetadata.update(
            {
                "e2eeVersion": "2",
                "contentType": str(contentType),
                "e2eeMark": "2",
            }
        )
        try:
            return self.sendMessageWithChunks(
                to, chunk, contentType, contentMetadata, relatedMessageId
            )
        except (LineServiceException, TalkException) as e:
            e_code = getattr(e, "code")
            if e_code == 84 and not renewKey:
                self._logger.warn(f"renew E2EE key for '{to}'...")
                return self.sendMessageWithE2EE(
                    to,
                    text,
                    contentType,
                    contentMetadata,
                    relatedMessageId,
                    renewKey=True,
                )
            raise e

    def sendMessageWithChunks(
        self, to, chunk, contentType=0, contentMetadata=None, relatedMessageId=None
    ):
        if contentMetadata is None:
            contentMetadata = {}
        return self.sendMessage(
            to,
            None,
            contentType,
            contentMetadata,
            relatedMessageId,
            chunk=chunk,
            autoE2EE=False,
        )

    def sendCompactMessage(
        self, to: str, text: Optional[str], chunks: Optional[list] = None
    ):
        cType = -1  # 2 = TEXT, 4 = STICKER, 5 = E2EE_TEXT, 6 = E2EE_LOCATION
        ep = self.client.LINE_COMPACT_PLAIN_MESSAGE_ENDPOINT
        if chunks is None:
            chunks = []
        if text is not None:
            cType = 2
        elif chunks:
            cType = 5
            ep = self.client.LINE_COMPACT_E2EE_MESSAGE_ENDPOINT
        midType = self.client.getToType(to)
        sqrd = [cType, midType]
        _reqId = self.client.getCurrReqId()
        self._logger.debug(
            f"[sendCompactMessage] REQ_ID: {_reqId}",
        )
        sqrd += self.client.getIntBytes(_reqId, isCompact=True)
        sqrd += self.client.getMagicStringBytes(to[1:])
        if cType == 2:
            sqrd += self.client.getStringBytes(text, isCompact=True)
            sqrd.append(2)
        elif cType == 5:
            sqrd += [2]
            for _ck in chunks[:3]:
                sqrd += self.client.getStringBytes(_ck, isCompact=True)
            for _ck in chunks[3:5]:
                sqrd += list(_ck)
        hr = self.client.server.additionalHeaders(
            self.client.server.Headers, {"x-lai": str(_reqId)}
        )
        try:
            return self.client.postPackDataAndGetUnpackRespData(
                ep, sqrd, -7, headers=hr
            )
        except (LineServiceException, TalkException) as e:
            if getattr(e, "code") in [82, 99]:
                return self.sendCompactE2EEMessage(to, text)
            raise e
        except Exception as e:
            raise e

    def sendCompactE2EEMessage(self, to, text):
        chunks = self.client.encryptE2EEMessage(to, text, isCompact=True)
        return self.sendCompactMessage(to, None, chunks)

    def sendSuperEzTagAll(self, to: str, text: str, **kwargs):
        """2022/08/25"""
        a = [["contentType", 0], ["contentMetadata", {}], ["relatedMessageId", None]]
        k = kwargs
        L = 0
        m = {}
        r = text
        S = 0
        T = 0
        for ck, cv in a:
            if ck not in k:
                k[ck] = cv
        if "@" not in r:
            r = f"@CHRLINE-v2.5.0-RC-Will-NOT-Be-Released {r}"
        S = r.index("@")
        T = r[S:].index(" ")
        L = S + (T if T != -1 else 1)
        m = self.client.genMentionData([{"S": S, "L": L, "A": True}])
        k["contentMetadata"].update(m)
        k["to"] = to
        k["text"] = r
        return self.sendMessage(**k)

    def getEncryptedIdentity(self):
        """
        Get encrypted identity.

        DEPRECATED: Use 'getEncryptedIdentityV3' instead.
        """
        METHOD_NAME = "getEncryptedIdentity"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getProfile(self):
        METHOD_NAME = "getProfile"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getSettings(self):
        METHOD_NAME = "getSettings"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def sendChatChecked(
        self, chatMid: str, lastMessageId: str, sessionId: Optional[int] = None
    ):
        METHOD_NAME = "sendChatChecked"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, chatMid],
            [11, 3, lastMessageId],
            [3, 4, sessionId],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def unsendMessage(self, messageId: str):
        METHOD_NAME = "unsendMessage"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, messageId],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getContact(self, mid: str):
        """
        Get contact.
        """
        METHOD_NAME = "getContact"
        params = [[11, 2, mid]]
        return self.__sender.send(METHOD_NAME, params)

    def getContacts(self, mids: List[str]):
        """
        Get contacts.

        DEPRECATED: Use 'getContactsV3' instead.
        """
        METHOD_NAME = "getContacts"
        params = [[15, 2, [11, mids]]]
        return self.__sender.send(METHOD_NAME, params)

    def getContactsV2(self, mids):
        """
        Get contacts V2.

        DEPRECATED: Use 'getContactsV3' instead.
        """
        METHOD_NAME = "getContactsV2"
        params = [[15, 1, [11, mids]]]
        params = [[12, 1, params]]
        return self.__sender.send(METHOD_NAME, params)

    def findAndAddContactsByMid(
        self, mid, reference='{"screen":"groupMemberList","spec":"native"}'
    ):
        """
        Find and add contacts by mid.

        DEPRECATED: Use 'addFriendByMid' instead.
        """
        METHOD_NAME = "findAndAddContactsByMid"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, mid],
            [8, 3, 0],
            [11, 4, reference],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getGroup(self, mid: str):
        """
        Get group.

        DEPRECATED: Use 'getChats' instead.
        """
        METHOD_NAME = "getGroup"
        params = [
            [11, 2, mid],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getGroups(self, mids: List[str]):
        """
        Get groups.

        DEPRECATED: Use 'getChats' instead.
        """
        METHOD_NAME = "getGroups"
        params = [
            [15, 2, [11, mids]],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getGroupsV2(self, mids: List[str]):
        """
        Get groups v2.

        DEPRECATED: Use 'getChats' instead.
        """
        METHOD_NAME = "getGroupsV2"
        params = [
            [15, 2, [11, mids]],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getChats(self, mids: List[str], withMembers=True, withInvitees=True):
        """Get chats."""
        METHOD_NAME = "getChats"
        if not isinstance(mids, list):
            raise Exception("[getChats] mids must be a list")
        params = [
            [12, 1, [[15, 1, [11, mids]], [2, 2, withMembers], [2, 3, withInvitees]]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getAllChatMids(self, withMembers=True, withInvitees=True):
        """Get all chat mids."""
        METHOD_NAME = "getAllChatMids"
        params = [[12, 1, [[2, 1, withMembers], [2, 2, withInvitees]]], [8, 2, 7]]
        return self.__sender.send(METHOD_NAME, params)

    def getCompactGroup(self, mid: str):
        """
        Get compact group.

        DEPRECATED: Use 'getChats' instead.
        """
        METHOD_NAME = "getCompactGroup"
        params = [
            [11, 2, mid],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def deleteOtherFromChat(self, to: str, mid: str):
        """Delete other from chat."""
        METHOD_NAME = "deleteOtherFromChat"
        if isinstance(mid, list):
            _lastReq = None
            for _mid in mid:
                print("[deleteOtherFromChat] The parameter 'mid' should be str")
                _lastReq = self.deleteOtherFromChat(to, _mid)
            return _lastReq
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, to],
            [14, 3, [11, [mid]]],
        ]
        params = [
            [12, 1, params],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def inviteIntoChat(self, to: str, mids: List[str]):
        """Invite into chat."""
        METHOD_NAME = "inviteIntoChat"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, to],
            [14, 3, [11, mids]],
        ]
        params = [
            [12, 1, params],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def cancelChatInvitation(self, to: str, mid: str):
        """Cancel chat invitation."""
        METHOD_NAME = "cancelChatInvitation"
        if isinstance(mid, list):
            _lastReq = None
            for _mid in mid:
                print("[deleteOtherFromChat] The parameter 'mid' should be str")
                _lastReq = self.deleteOtherFromChat(to, _mid)
            return _lastReq
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, to],
            [14, 3, [11, [mid]]],
        ]
        params = [
            [12, 1, params],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def deleteSelfFromChat(self, to: str):
        """Delete self from chat."""
        METHOD_NAME = "deleteSelfFromChat"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, to],
        ]
        params = [
            [12, 1, params],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def acceptChatInvitation(self, to: str):
        """Accept chat invitation."""
        METHOD_NAME = "acceptChatInvitation"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, to],
        ]
        params = [
            [12, 1, params],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def reissueChatTicket(self, groupMid: str):
        """Reissue chat ticket."""
        METHOD_NAME = "reissueChatTicket"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, groupMid],
        ]
        params = [
            [12, 1, params],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def findChatByTicket(self, ticketId: str):
        """Find chat by ticket."""
        METHOD_NAME = "findChatByTicket"
        params = [
            [11, 1, ticketId],
        ]
        params = [
            [12, 1, params],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def acceptChatInvitationByTicket(self, to: str, ticket: str):
        """Accept chat invitation by ticket."""
        METHOD_NAME = "acceptChatInvitationByTicket"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, to],
            [11, 3, ticket],
        ]
        params = [
            [12, 1, params],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def updateChat(
        self, chatMid: str, chatSet: Union[dict, DummyThrift], updatedAttribute=1
    ):
        """
        Update chat.

        updatedAttribute:
            NAME(1),
            PICTURE_STATUS(2),
            PREVENTED_JOIN_BY_TICKET(4),
            NOTIFICATION_SETTING(8),
            INVITATION_TICKET(16),
            FAVORITE_TIMESTAMP(32),
            CHAT_TYPE(64);
        """
        METHOD_NAME = "updateChat"
        chat_type = {
            1: 8,
            3: 10,
            4: 2,
            5: 10,
            6: 11,
            7: 11,
        }
        extra_group_type = {
            1: 11,
            2: 2,
            3: 11,
            4: (13, (11, 10)),
            5: (13, (11, 10)),
            6: 2,
            7: 2,
            8: 2,
        }
        chat = [
            [11, 2, chatMid],
        ]
        if isinstance(chatSet, DummyThrift):
            chat = chatSet
        else:
            # if chatSet use dict only
            for k, v in chat_type.items():
                v2 = chatSet.get(k)
                if v2 is not None:
                    chat.append([v, k, v2])
            extra = chatSet.get(8)
            if extra is not None:
                groupExtra = extra.get(1)
                peerExtra = extra.get(2)
                chat_extra = []
                if groupExtra is not None:
                    for k, v in extra_group_type.items():
                        v2 = groupExtra.get(k)
                        if v2 is not None:
                            if isinstance(v, int):
                                chat_extra.append([v, k, v2])
                            else:
                                v3, v4 = v
                                v5 = [_v for _v in v4] + [v2]
                                chat_extra.append([v3, k, v5])
                    chat_extra = [[12, 1, chat_extra]]
                else:
                    raise NotImplementedError
                chat.append([12, 8, chat_extra])
        params = [
            [8, 1, self.client.getCurrReqId()],
            [12, 2, chat],
            [8, 3, updatedAttribute],
        ]
        params = [
            [12, 1, params],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def updateChatName(self, chatMid: str, name: str):
        """Update chat name."""
        return self.updateChat(chatMid, {6: name}, 1)

    def updateChatPreventedUrl(self, chatMid: str, bT: bool):
        """Update chat prevented url."""
        return self.updateChat(chatMid, {8: {1: {2: bT}}}, 4)

    def getGroupIdsJoined(self):
        """
        Get group ids joined.

        DEPRECATED: Use 'getAllChatMids' instead.
        """
        METHOD_NAME = "getGroupIdsJoined"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getGroupIdsInvited(self):
        """
        Get group ids invited.

        DEPRECATED: Use 'getAllChatMids' instead.
        """
        METHOD_NAME = "getGroupIdsInvited"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getAllContactIds(self):
        """Get all contact ids."""
        METHOD_NAME = "getAllContactIds"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getBlockedContactIds(self):
        """Get blocked contact ids."""
        METHOD_NAME = "getBlockedContactIds"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getBlockedRecommendationIds(self):
        """Get blocked recommendation ids."""
        METHOD_NAME = "getBlockedRecommendationIds"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getAllReadMessageOps(self):
        """
        Get all read message ops.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "getAllReadMessageOps"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def sendPostback(self, messageId: str, url: str, chatMID: str, originMID: str):
        """
        Send postback.

        The url need start with `linepostback://postback?_data=`
        """
        METHOD_NAME = "sendPostback"
        params = [
            [11, 1, messageId],
            [11, 2, url],
            [11, 3, chatMID],
            [11, 4, originMID],
        ]
        params = [[12, 2, params]]
        return self.__sender.send(METHOD_NAME, params)

    def getPreviousMessagesV2WithRequest(
        self,
        messageBoxId: str,
        deliveredTime: int,
        messageId: int,
        messagesCount=100,
        withReadCount=False,
        receivedOnly=False,
    ):
        """Get previous messages v2 with request.

        for secondary devices to sync previous messages.
        """
        METHOD_NAME = "getPreviousMessagesV2WithRequest"
        params = [
            [
                12,
                2,
                [
                    [11, 1, messageBoxId],
                    [
                        12,
                        2,
                        [
                            [10, 1, deliveredTime],
                            [10, 2, messageId],
                        ],
                    ],
                    [8, 3, messagesCount],
                    [2, 4, withReadCount],
                    [2, 5, receivedOnly],
                ],
            ],
            [8, 3, 4],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getMessageBoxes(
        self,
        minChatId: str,
        maxChatId: str,
        activeOnly: bool,
        messageBoxCountLimit: int,
        withUnreadCount: bool,
        lastMessagesPerMessageBoxCount: int,
        unreadOnly: bool,
        syncReason: int,
    ):
        """Get message boxes"""
        METHOD_NAME = "getMessageBoxes"
        messageBoxListRequest = [
            [11, 1, minChatId],
            [11, 2, maxChatId],
            [2, 3, activeOnly],
            [8, 4, messageBoxCountLimit],
            [2, 5, withUnreadCount],
            [8, 6, lastMessagesPerMessageBoxCount],
            [2, 7, unreadOnly],
        ]
        params = [
            [12, 2, messageBoxListRequest],
            [8, 3, syncReason],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getChatRoomAnnouncementsBulk(self, chatRoomMids: List[str], syncReason: int):
        """Get announcements for multiple groups at once."""
        METHOD_NAME = "getChatRoomAnnouncementsBulk"
        params = [[15, 2, [11, chatRoomMids]], [8, 3, syncReason]]
        return self.__sender.send(METHOD_NAME, params)

    def getChatRoomAnnouncements(self, chatRoomMid: str):
        """Get chat room announcements."""
        METHOD_NAME = "getChatRoomAnnouncements"
        params = [[11, 2, chatRoomMid]]
        return self.__sender.send(METHOD_NAME, params)

    def removeChatRoomAnnouncement(self, chatRoomMid: str, announcementSeq: int):
        """Remove chat room announcement."""
        METHOD_NAME = "removeChatRoomAnnouncement"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, chatRoomMid],
            [10, 3, announcementSeq],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def createChatRoomAnnouncement(
        self,
        chatRoomMid: str,
        text: str,
        link: str,
        thumbnail: Optional[str] = None,
        _type: int = 0,
        displayFields: int = 5,
        replace: Optional[str] = None,
        sticonOwnership: Optional[str] = None,
        postNotificationMetadata: Optional[str] = None,
    ):
        """Create chat room announcement."""
        METHOD_NAME = "createChatRoomAnnouncement"
        contentMetadata = [
            [11, 1, replace],
            [11, 2, sticonOwnership],
            [11, 3, postNotificationMetadata],
        ]
        contents = [
            [8, 1, displayFields],
            [11, 2, text],
            [11, 3, link],
            [11, 4, thumbnail],
            [12, 5, contentMetadata],
        ]
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, chatRoomMid],
            [8, 3, _type],
            [12, 4, contents],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def leaveRoom(self, roomId: str):
        """Leave room."""
        METHOD_NAME = "leaveRoom"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, roomId],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getRoomsV2(self, roomIds: List[str]):
        """Get room v2."""
        METHOD_NAME = "getRoomsV2"
        params = [
            [15, 2, [11, roomIds]],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def createRoomV2(self, contactIds: List[str]):
        """Create room v2."""
        METHOD_NAME = "createRoomV2"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [15, 2, [11, contactIds]],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getCountries(self, countryGroup=1):
        """Get countries."""
        METHOD_NAME = "getCountries"
        params = [
            [8, 2, countryGroup],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def acquireEncryptedAccessToken(self, featureType=2):
        """Acquire encrypted access token."""
        METHOD_NAME = "acquireEncryptedAccessToken"
        params = [
            [8, 2, featureType],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def blockContact(self, mid: str):
        """Block contact."""
        METHOD_NAME = "blockContact"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, mid],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def unblockContact(self, mid, reference: Optional[str] = None):
        """Unblock contact."""
        METHOD_NAME = "unblockContact"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, mid],
            [11, 3, reference],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getLastOpRevision(self):
        """Get last op revision."""
        METHOD_NAME = "getLastOpRevision"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getServerTime(self):
        """Get server time."""
        METHOD_NAME = "getServerTime"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getConfigurations(
        self,
        revision: Optional[int] = None,
        regionOfUsim: Optional[str] = None,
        regionOfTelephone: Optional[str] = None,
        regionOfLocale: Optional[str] = None,
        carrier: Optional[str] = None,
        syncReason: Optional[int] = None,
    ):
        """Get configurations."""
        METHOD_NAME = "getConfigurations"
        params = [
            [10, 2, revision],
            [11, 3, regionOfUsim],
            [11, 4, regionOfTelephone],
            [11, 5, regionOfLocale],
            [11, 6, carrier],
            [8, 7, syncReason],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def fetchOps(self, revision: int, count=100):
        """
        Fetch ops.

        DEPRECATED: Use 'sync' instead.
        """
        METHOD_NAME = "fetchOps"
        params = [
            [10, 2, revision],
            [8, 3, count],
            [10, 4, self.globalRev],
            [10, 5, self.individualRev],
        ]
        sqrd = self.client.generateDummyProtocol("fetchOps", params, 4)
        hr = self.client.server.additionalHeaders(
            self.client.server.Headers,
            {
                # "x-lst": "110000",
                "x-las": "F",  # or "B" if background
                "x-lam": "w",  # or "m"
                "x-lac": "46692",  # carrier
            },
        )
        try:
            data = self.client.postPackDataAndGetUnpackRespData(
                "/P5",
                sqrd,
                5,
                encType=0,
                headers=hr,
                readWith=f"TalkService.{METHOD_NAME}",
                timeout=110,
            )
            if data is None:
                return []
            if not (isinstance(data, dict) and "error" in data):
                if isinstance(data, list):
                    for op in data:
                        if self.client.checkAndGetValue(op, "type", "val_3", 3) == 0:
                            param1 = self.client.checkAndGetValue(
                                op, "param1", "val_10", 10
                            )
                            param2 = self.client.checkAndGetValue(
                                op, "param2", "val_11", 11
                            )
                            if param1 is not None:
                                a = param1.split("\x1e")
                                self.individualRev = a[0]
                                self.client.log(
                                    f"individualRev: {self.individualRev}", True
                                )
                            if param2 is not None:
                                b = param2.split("\x1e")
                                self.globalRev = b[0]
                                self.client.log(f"globalRev: {self.globalRev}", True)
                return data
            else:
                raise Exception(data["error"])
        except httpx.ReadTimeout:
            pass
        return []

    def fetchOperations(self, localRev: int, count=100):
        """
        Fetch operations.

        DEPRECATED: Use 'fetchOps' instead.
        """
        METHOD_NAME = "fetchOperations"
        params = [
            [10, 2, localRev],
            [8, 3, count],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def sendEchoPush(self, text: str):
        """
        Send echo push.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "sendEchoPush"
        # for long poll? check conn is alive
        # text: 1614384862517 = time
        params = [
            [11, 2, text],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getRepairElements(
        self, profile: bool = True, settings: bool = False, syncReason: int = 5
    ):
        """Get repair elements."""
        METHOD_NAME = "getRepairElements"
        params = [
            [2, 1, profile],
            [2, 2, settings],
            [8, 11, syncReason],
        ]
        params = [[12, 1, params]]
        return self.__sender.send(METHOD_NAME, params)

    def getSettingsAttributes2(self, attributesToRetrieve: list):
        """
        Get settings attributes2

            NOTIFICATION_ENABLE(0),
            NOTIFICATION_MUTE_EXPIRATION(1),
            NOTIFICATION_NEW_MESSAGE(2),
            NOTIFICATION_GROUP_INVITATION(3),
            NOTIFICATION_SHOW_MESSAGE(4),
            NOTIFICATION_INCOMING_CALL(5),
            NOTIFICATION_SOUND_MESSAGE(8),
            NOTIFICATION_SOUND_GROUP(9),
            NOTIFICATION_DISABLED_WITH_SUB(16),
            NOTIFICATION_PAYMENT(17),
            NOTIFICATION_MENTION(40),
            NOTIFICATION_THUMBNAIL(45),
            NOTIFICATION_BADGE_TALK_ONLY(65),
            NOTIFICATION_REACTION(67),
            PRIVACY_SYNC_CONTACTS(6),
            PRIVACY_SEARCH_BY_PHONE_NUMBER(7),
            PRIVACY_SEARCH_BY_USERID(13),
            PRIVACY_SEARCH_BY_EMAIL(14),
            PRIVACY_SHARE_PERSONAL_INFO_TO_FRIENDS(51),
            PRIVACY_ALLOW_SECONDARY_DEVICE_LOGIN(21),
            PRIVACY_PROFILE_IMAGE_POST_TO_MYHOME(23),
            PRIVACY_PROFILE_MUSIC_POST_TO_MYHOME(35),
            PRIVACY_PROFILE_HISTORY(57),
            PRIVACY_STATUS_MESSAGE_HISTORY(54),
            PRIVACY_ALLOW_FRIEND_REQUEST(30),
            PRIVACY_RECV_MESSAGES_FROM_NOT_FRIEND(25),
            PRIVACY_AGREE_USE_LINECOIN_TO_PAIDCALL(26),
            PRIVACY_AGREE_USE_PAIDCALL(27),
            PRIVACY_AGE_RESULT(60),
            PRIVACY_AGE_RESULT_RECEIVED(61),
            PRIVACY_ALLOW_FOLLOW(63),
            PRIVACY_SHOW_FOLLOW_LIST(64),
            CONTACT_MY_TICKET(10),
            IDENTITY_PROVIDER(11),
            IDENTITY_IDENTIFIER(12),
            SNS_ACCOUNT(19),
            PHONE_REGISTRATION(20),
            PWLESS_PRIMARY_CREDENTIAL_REGISTRATION(31),
            ALLOWED_TO_CONNECT_EAP_ACCOUNT(32),
            PREFERENCE_LOCALE(15),
            CUSTOM_MODE(22),
            EMAIL_CONFIRMATION_STATUS(24),
            ACCOUNT_MIGRATION_PINCODE(28),
            ENFORCED_INPUT_ACCOUNT_MIGRATION_PINCODE(29),
            SECURITY_CENTER_SETTINGS(18),
            E2EE_ENABLE(33),
            HITOKOTO_BACKUP_REQUESTED(34),
            CONTACT_ALLOW_FOLLOWING(36),
            PRIVACY_ALLOW_NEARBY(37),
            AGREEMENT_NEARBY(38),
            AGREEMENT_SQUARE(39),
            ALLOW_UNREGISTRATION_SECONDARY_DEVICE(41),
            AGREEMENT_BOT_USE(42),
            AGREEMENT_SHAKE_FUNCTION(43),
            AGREEMENT_MOBILE_CONTACT_NAME(44),
            AGREEMENT_SOUND_TO_TEXT(46),
            AGREEMENT_PRIVACY_POLICY_VERSION(47),
            AGREEMENT_AD_BY_WEB_ACCESS(48),
            AGREEMENT_PHONE_NUMBER_MATCHING(49),
            AGREEMENT_COMMUNICATION_INFO(50),
            AGREEMENT_THINGS_WIRELESS_COMMUNICATION(52),
            AGREEMENT_GDPR(53),
            AGREEMENT_PROVIDE_LOCATION(55),
            AGREEMENT_BEACON(56),
            AGREEMENT_CONTENTS_SUGGEST(58),
            AGREEMENT_CONTENTS_SUGGEST_DATA_COLLECTION(59),
            AGREEMENT_OCR_IMAGE_COLLECTION(62),
            AGREEMENT_ICNA(66),
            AGREEMENT_MID(68),
            HOME_NOTIFICATION_NEW_FRIEND(69),
            HOME_NOTIFICATION_FAVORITE_FRIEND_UPDATE(70),
            HOME_NOTIFICATION_GROUP_MEMBER_UPDATE(71),
            HOME_NOTIFICATION_BIRTHDAY(72),
            AGREEMENT_LINE_OUT_USE(73),
            AGREEMENT_LINE_OUT_PROVIDE_INFO(74);
            NOTIFICATION_ENABLE(0),
            NOTIFICATION_MUTE_EXPIRATION(1),
            NOTIFICATION_NEW_MESSAGE(2),
            NOTIFICATION_GROUP_INVITATION(3),
            NOTIFICATION_SHOW_MESSAGE(4),
            NOTIFICATION_INCOMING_CALL(5),
            NOTIFICATION_SOUND_MESSAGE(8),
            NOTIFICATION_SOUND_GROUP(9),
            NOTIFICATION_DISABLED_WITH_SUB(16),
            NOTIFICATION_PAYMENT(17),
            NOTIFICATION_MENTION(40),
            NOTIFICATION_THUMBNAIL(45),
            NOTIFICATION_BADGE_TALK_ONLY(65),
            NOTIFICATION_REACTION(67),
            PRIVACY_SYNC_CONTACTS(6),
            PRIVACY_SEARCH_BY_PHONE_NUMBER(7),
            PRIVACY_SEARCH_BY_USERID(13),
            PRIVACY_SEARCH_BY_EMAIL(14),
            PRIVACY_SHARE_PERSONAL_INFO_TO_FRIENDS(51),
            PRIVACY_ALLOW_SECONDARY_DEVICE_LOGIN(21),
            PRIVACY_PROFILE_IMAGE_POST_TO_MYHOME(23),
            PRIVACY_PROFILE_MUSIC_POST_TO_MYHOME(35),
            PRIVACY_PROFILE_HISTORY(57),
            PRIVACY_STATUS_MESSAGE_HISTORY(54),
            PRIVACY_ALLOW_FRIEND_REQUEST(30),
            PRIVACY_RECV_MESSAGES_FROM_NOT_FRIEND(25),
            PRIVACY_AGREE_USE_LINECOIN_TO_PAIDCALL(26),
            PRIVACY_AGREE_USE_PAIDCALL(27),
            PRIVACY_AGE_RESULT(60),
            PRIVACY_AGE_RESULT_RECEIVED(61),
            PRIVACY_ALLOW_FOLLOW(63),
            PRIVACY_SHOW_FOLLOW_LIST(64),
            CONTACT_MY_TICKET(10),
            IDENTITY_PROVIDER(11),
            IDENTITY_IDENTIFIER(12),
            SNS_ACCOUNT(19),
            PHONE_REGISTRATION(20),
            PWLESS_PRIMARY_CREDENTIAL_REGISTRATION(31),
            ALLOWED_TO_CONNECT_EAP_ACCOUNT(32),
            PREFERENCE_LOCALE(15),
            CUSTOM_MODE(22),
            EMAIL_CONFIRMATION_STATUS(24),
            ACCOUNT_MIGRATION_PINCODE(28),
            ENFORCED_INPUT_ACCOUNT_MIGRATION_PINCODE(29),
            SECURITY_CENTER_SETTINGS(18),
            E2EE_ENABLE(33),
            HITOKOTO_BACKUP_REQUESTED(34),
            CONTACT_ALLOW_FOLLOWING(36),
            PRIVACY_ALLOW_NEARBY(37),
            AGREEMENT_NEARBY(38),
            AGREEMENT_SQUARE(39),
            ALLOW_UNREGISTRATION_SECONDARY_DEVICE(41),
            AGREEMENT_BOT_USE(42),
            AGREEMENT_SHAKE_FUNCTION(43),
            AGREEMENT_MOBILE_CONTACT_NAME(44),
            AGREEMENT_SOUND_TO_TEXT(46),
            AGREEMENT_PRIVACY_POLICY_VERSION(47),
            AGREEMENT_AD_BY_WEB_ACCESS(48),
            AGREEMENT_PHONE_NUMBER_MATCHING(49),
            AGREEMENT_COMMUNICATION_INFO(50),
            AGREEMENT_THINGS_WIRELESS_COMMUNICATION(52),
            AGREEMENT_GDPR(53),
            AGREEMENT_PROVIDE_LOCATION(55),
            AGREEMENT_BEACON(56),
            AGREEMENT_CONTENTS_SUGGEST(58),
            AGREEMENT_CONTENTS_SUGGEST_DATA_COLLECTION(59),
            AGREEMENT_OCR_IMAGE_COLLECTION(62),
            AGREEMENT_ICNA(66),
            AGREEMENT_MID(68),
            HOME_NOTIFICATION_NEW_FRIEND(69),
            HOME_NOTIFICATION_FAVORITE_FRIEND_UPDATE(70),
            HOME_NOTIFICATION_GROUP_MEMBER_UPDATE(71),
            HOME_NOTIFICATION_BIRTHDAY(72),
            AGREEMENT_LINE_OUT_USE(73),
            AGREEMENT_LINE_OUT_PROVIDE_INFO(74);
        """
        METHOD_NAME = "getSettingsAttributes2"
        if not isinstance(attributesToRetrieve, list):
            attributesToRetrieve = [attributesToRetrieve]
            print("[attributesToRetrieve] plz using LIST")
        params = [[14, 2, [8, attributesToRetrieve]]]
        return self.__sender.send(METHOD_NAME, params)

    def updateSettingsAttributes2(self, settings: dict, attributesToUpdate: list):
        """Update settings attributes2."""
        METHOD_NAME = "updateSettingsAttributes2"
        if not isinstance(attributesToUpdate, list):
            attributesToUpdate = [attributesToUpdate]
            print("[attributesToRetrieve] plz using LIST")
        settings_type = {
            10: 2,
            11: 10,
            12: 2,
            13: 2,
            14: 2,
            15: 2,
            16: 11,
            17: 11,
            18: 2,
            19: 2,
            20: 2,
            21: 2,
            22: 2,
            23: 2,
            24: 2,
            25: 2,
            26: 2,
            27: 2,
            28: 2,
            29: 2,
            30: 11,
            40: 8,
            41: 11,
            42: 13,
            43: 2,
            44: 8,
            45: 8,
            46: 2,
            47: 8,
            48: 2,
            49: 2,
            50: 11,
            60: 13,
            61: 2,
            62: 2,
            63: 2,
            65: 2,
            66: 10,
            67: 10,
            68: 2,
            69: 10,
            70: 10,
            71: 10,
            72: 2,
            73: 10,
            74: 11,
            75: 10,
            76: 10,
            77: 10,
            78: 8,
            79: 10,
            80: 10,
            81: 8,
            82: 10,
            83: 10,
            85: 8,
            86: 10,
            87: 10,
            88: 8,
            89: 2,
            90: 10,
            91: 2,
            92: 2,
            93: 2,
            94: 10,
            95: 2,
            96: 10,
            97: 2,
            98: 2,
            99: 2,
            100: 2,
            101: 13,
            102: 10,
            103: 10,
            104: 2,
            105: 10,
            106: 11,
            107: 2,
            108: 10,
            109: 2,
            110: 10,
            112: 10,
            113: 10,
            114: 10,
            115: 10,
            116: 10,
            117: 10,
            118: 10,
            119: 10,
            120: 10,
        }
        setting = []
        for k, v in settings:
            v2 = settings_type.get(k)
            if v2 is not None and v2 != 13:
                setting.append([v2, k, v])
        params = [
            [8, 1, self.client.getCurrReqId()],
            [12, 3, setting],
            [14, 4, [8, attributesToUpdate]],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def rejectChatInvitation(self, chatMid: str):
        """Reject chat invitation."""
        METHOD_NAME = "rejectChatInvitation"
        params = [[8, 1, self.client.getCurrReqId()], [11, 2, chatMid]]
        params = [[12, 1, params]]
        return self.__sender.send(METHOD_NAME, params)

    def updateProfileAttribute(self, attr: int, value: str):
        """
        Update profile attribute.

        attr:
            ALL(0),
            EMAIL(1),
            DISPLAY_NAME(2),
            PHONETIC_NAME(4),
            PICTURE(8),
            STATUS_MESSAGE(16),
            ALLOW_SEARCH_BY_USERID(32),
            ALLOW_SEARCH_BY_EMAIL(64),
            BUDDY_STATUS(128),
            MUSIC_PROFILE(256),
            AVATAR_PROFILE(512);
        """
        METHOD_NAME = "updateProfileAttribute"
        params = [[8, 1, 0], [8, 2, attr], [11, 3, value]]
        return self.__sender.send(METHOD_NAME, params)

    def getE2EEPublicKey(self, mid: str, keyVersion: int, keyId: int):
        """Get E2EE public key."""
        METHOD_NAME = "getE2EEPublicKey"
        params = [[11, 2, mid], [8, 3, keyVersion], [8, 4, keyId]]
        return self.__sender.send(METHOD_NAME, params)

    def getE2EEPublicKeys(self):
        """Get E2EE public keys."""
        METHOD_NAME = "getE2EEPublicKeys"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getE2EEPublicKeysEx(self, ignoreE2EEStatus: int):
        """
        Get E2EE public keys ex.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "getE2EEPublicKeysEx"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def removeE2EEPublicKey(self, spec, keyId, keyData):
        """
        Remove E2EE public key.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "removeE2EEPublicKey"
        params = [[12, 2, [[8, 1, spec], [8, 2, keyId], [11, 4, keyData]]]]
        return self.__sender.send(METHOD_NAME, params)

    def registerE2EEPublicKey(
        self, version: int, keyId: Optional[int], keyData: str, time: int
    ):
        """Register E2EE public key."""
        METHOD_NAME = "registerE2EEPublicKey"
        params = [
            [8, 1, version],
            [8, 2, keyId],
            [11, 4, keyData],
            [10, 5, time],
        ]
        params = [
            [8, 1, self.client.getCurrReqId()],
            [12, 2, params],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def registerE2EEGroupKey(
        self,
        keyVersion: int,
        chatMid: str,
        members: List[str],
        keyIds: List[int],
        encryptedSharedKeys: List[ByteString],
    ):
        """Register E2EE group key."""
        METHOD_NAME = "registerE2EEGroupKey"
        if not isinstance(members, list):
            raise Exception("[registerE2EEGroupKey] members must be a list")
        if not isinstance(keyIds, list):
            raise Exception("[registerE2EEGroupKey] keyIds must be a list")
        if not isinstance(encryptedSharedKeys, list):
            raise Exception("[registerE2EEGroupKey] encryptedSharedKeys must be a list")
        params = [
            [8, 2, keyVersion],
            [11, 3, chatMid],
            [15, 4, [11, members]],
            [15, 5, [8, keyIds]],
            [15, 6, [11, encryptedSharedKeys]],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getE2EEGroupSharedKey(self, keyVersion: int, chatMid: str, groupKeyId: int):
        """Get E2EE group shared key."""
        METHOD_NAME = "getE2EEGroupSharedKey"
        params = [
            [8, 2, keyVersion],
            [11, 3, chatMid],
            [8, 4, groupKeyId],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getLastE2EEGroupSharedKey(self, keyVersion: int, chatMid: str):
        """Get last E2EE group shared key."""
        METHOD_NAME = "getLastE2EEGroupSharedKey"
        params = [
            [8, 2, keyVersion],
            [11, 3, chatMid],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getLastE2EEPublicKeys(self, chatMid: str):
        """Get last E2EE public keys."""
        METHOD_NAME = "getLastE2EEPublicKeys"
        params = [
            [11, 2, chatMid],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def requestE2EEKeyExchange(
        self, temporalPublicKey: bytes, keyVersion: int, keyId: int, verifier: str
    ):
        """Request E2EE key exchange."""
        METHOD_NAME = "requestE2EEKeyExchange"
        params = [
            [8, 1, 0],  # reqSeq
            [11, 2, temporalPublicKey],
            [12, 3, [[8, 1, keyVersion], [8, 2, keyId]]],
            [11, 4, verifier],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def respondE2EEKeyExchange(self, encryptedKeyChain: str, hashKeyChain: str):
        """Respond E2EE key exchange."""
        METHOD_NAME = "respondE2EEKeyExchange"
        params = [
            [8, 1, 0],  # reqSeq
            [11, 2, encryptedKeyChain],
            [11, 3, hashKeyChain],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def negotiateE2EEPublicKey(self, mid: str):
        """Negotiate E2EE public key."""
        METHOD_NAME = "negotiateE2EEPublicKey"
        params = [
            [11, 2, mid],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def react(self, messageId: int, reactionType: int = 5):
        """React to message."""
        METHOD_NAME = "react"
        params = [
            [12, 1, [[8, 1, 0], [10, 2, messageId], [12, 3, [[8, 1, reactionType]]]]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def createChat(
        self,
        name: str,
        targetUserMids: List[str],
        type: int = 0,
        picturePath: Optional[str] = None,
    ):
        """Create chat."""
        METHOD_NAME = "createChat"
        params = [
            [8, 1, 0],
            [8, 2, type],
            [11, 3, name],
            [14, 4, [11, targetUserMids]],
            [11, 5, picturePath],
        ]
        params = [[12, 1, params]]
        return self.__sender.send(METHOD_NAME, params)

    def updateRegion(self, region="TW"):
        """
        Update region.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "updateRegion"
        params = [[11, 4, region]]
        return self.__sender.send(METHOD_NAME, params)

    def getChatExistence(self, ids: List[str]):
        """
        Get chat existence.

        DEPRECATED: This is a DevKit method.
        """
        METHOD_NAME = "getChatExistence"
        params = [
            [14, 1, [11, ids]],
        ]
        params = [[12, 2, params]]
        return self.__sender.send(METHOD_NAME, params)

    def getChatMembership(self, chatIds: List[str]):
        """
        Get chat membership.

        DEPRECATED: This is a DevKit method.
        """
        METHOD_NAME = "getChatMembership"
        params = [
            [14, 1, [11, chatIds]],
        ]
        params = [[12, 2, params]]
        return self.__sender.send(METHOD_NAME, params)

    def setChatHiddenStatus(self, chatId: str, lastMessageId: int, hidden: bool):
        """Set chat hidden status."""
        METHOD_NAME = "setChatHiddenStatus"
        params = [
            [11, 2, chatId],
            [10, 3, lastMessageId],
            [2, 4, hidden],
        ]
        params = [[12, 1, params]]
        return self.__sender.send(METHOD_NAME, params)

    def getReadMessageOps(self, chatId: str):
        """
        Get read message ops.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "getReadMessageOps"
        params = [[11, 2, chatId]]
        return self.__sender.send(METHOD_NAME, params)

    def getReadMessageOpsInBulk(self, chatIds: List[str]):
        """
        Get read message ops in bulk.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "getReadMessageOpsInBulk"
        params = [[15, 2, [11, chatIds]]]
        return self.__sender.send(METHOD_NAME, params)

    def getE2EEMessageInfo(self, mid: str, msgid: str, receiverKeyId: int):
        """
        Get E2EE message info.

        DEPRECATED: This is a DevKit method.
        """
        METHOD_NAME = "getE2EEMessageInfo"
        params = [
            [11, 2, mid],
            [11, 3, msgid],
            [8, 4, receiverKeyId],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getMessageBoxCompactWrapUpList(self):
        raise Exception("getMessageBoxCompactWrapUpList is not implemented")
        METHOD_NAME = "getMessageBoxCompactWrapUpList"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getRecentMessages(self, to: str):
        """
        Get recent messages.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "getRecentMessages"
        params = [[11, 2, to], [8, 3, 101]]
        return self.__sender.send(METHOD_NAME, params)

    def getRecentMessagesV2(self, to: str, count: int = 300):
        """
        Get recent messages v2.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "getRecentMessagesV2"
        params = [[11, 2, to], [8, 3, count]]
        return self.__sender.send(METHOD_NAME, params)

    def getPreviousMessageIds(self, to: str, count=100):
        """
        Get previous message ids.

        DEPRECATED: This is a DevKit method.
        """
        METHOD_NAME = "getPreviousMessageIds"
        params = [
            [11, 1, to],
            [8, 4, count],
        ]
        params = [[12, 2, params]]
        return self.__sender.send(METHOD_NAME, params)

    def getMessagesByIds(self, msgIds=[]):
        """
        Get messages by ids.

        DEPRECATED: This is a DevKit method.
        """
        # messagesByIdsRequests
        # - messagesByIdsRequest
        # {1: 1626172142246, 2: 14386851950042}
        raise Exception("getMessagesByIds is not implemented")
        params = [[15, 2, [12, []]]]
        sqrd = self.client.generateDummyProtocol("getMessagesByIds", params, 3)
        return self.client.postPackDataAndGetUnpackRespData("/S3", sqrd, 3)

    def getMessageBoxesByIds(self, mids: List[str]):
        """
        Get message boxes by ids.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "getMessageBoxesByIds"
        params = [[12, 2, [[15, 1, [11, mids]]]]]
        return self.__sender.send(METHOD_NAME, params)

    def getMessageBoxCompactWrapUpListV2(self, start=0, end=1):
        """
        Get message box compact wrap up list v2.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "getMessageBoxCompactWrapUpListV2"
        params = [[8, 2, start], [8, 3, end]]
        return self.__sender.send(METHOD_NAME, params)

    def getPreviousMessagesV2(self, mid: str, time: int, id: int, count=3000):
        """
        Get previous messages v2.

        DEPRECATED: Use 'getPreviousMessagesV2WithRequest' instead.
        """
        METHOD_NAME = "getPreviousMessagesV2"
        params = [[11, 2, mid], [12, 3, [[10, 1, time], [10, 2, id]]], [8, 4, count]]
        return self.__sender.send(METHOD_NAME, params)

    def getPreviousMessagesV2WithReadCount(
        self, mid: str, time: int, id: int, count=101
    ):
        """
        Get previous messages v2 with read count.

        DEPRECATED: Use 'getPreviousMessagesV2WithRequest' instead.
        """
        METHOD_NAME = "getPreviousMessagesV2WithReadCount"
        params = [[11, 2, mid], [12, 3, [[10, 1, time], [10, 2, id]]], [8, 4, count]]
        return self.__sender.send(METHOD_NAME, params)

    def getNextMessagesV2(self, mid: str, time: int, id: int):
        """
        Get next messages v2.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "getNextMessagesV2"
        params = [
            [11, 2, mid],
            [12, 3, [[10, 1, time], [10, 2, id]]],
            [8, 4, 101],  # count, 101 is max? maybe, hehe...
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getAllRoomIds(self):
        """
        Get all room ids.

        DEPRECATED: This is a DevKit method.
        """
        METHOD_NAME = "getAllRoomIds"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getCompactRooms(self, roomIds: List[str]):
        """
        Get compact rooms.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "getCompactRooms"
        params = [[15, 2, [11, roomIds]]]
        return self.__sender.send(METHOD_NAME, params)

    def acquireCallTicket(self, to: str):
        """
        Acquire call ticket.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "acquireCallTicket"
        params = [[11, 1, to]]
        return self.__sender.send(METHOD_NAME, params)

    def isAbusive(self):
        """
        Is abusive.

        DEPRECATED: This is a DevKit method.
        """
        METHOD_NAME = "isAbusive"
        # 2021/09/16 it removed...
        params = [
            [8, 1, 0],
            [8, 2, 1],  # reportSource
        ]
        return self.__sender.send(METHOD_NAME, params)

    def removeBuddySubscriptionAndNotifyBuddyUnregistered(self, contactMids: List[str]):
        """
        Remove buddy subscription and notify buddy unregistered.

        OA only.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "removeBuddySubscriptionAndNotifyBuddyUnregistered"
        params = [[15, 1, [11, contactMids]]]
        return self.__sender.send(METHOD_NAME, params)

    def makeUserAddMyselfAsContact(self, contactMids: List[str]):
        """
        Make user add myself as contact.

        OA only.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "makeUserAddMyselfAsContact"
        params = [[15, 1, [11, contactMids]]]
        return self.__sender.send(METHOD_NAME, params)

    def getFollowers(
        self,
        mid: Optional[str] = None,
        eMid: Optional[str] = None,
        cursor: Optional[str] = None,
    ):
        """Get followers."""
        METHOD_NAME = "getFollowers"
        data = [11, 1, mid]
        if eMid is not None:
            data = [11, 2, eMid]
        params = [[12, 2, [[12, 1, [data]], [11, 2, cursor]]]]
        return self.__sender.send(METHOD_NAME, params)

    def getFollowings(
        self,
        mid: Optional[str] = None,
        eMid: Optional[str] = None,
        cursor: Optional[str] = None,
    ):
        """Get followings."""
        METHOD_NAME = "getFollowings"
        params = [[12, 2, [[12, 1, [[11, 1, mid], [11, 2, eMid]]], [11, 2, cursor]]]]
        return self.__sender.send(METHOD_NAME, params)

    def removeFollower(
        self,
        mid: Optional[str] = None,
        eMid: Optional[str] = None,
    ):
        """Remove follower."""
        METHOD_NAME = "removeFollower"
        params = [[12, 2, [[12, 1, [[11, 1, mid], [11, 2, eMid]]]]]]
        return self.__sender.send(METHOD_NAME, params)

    def follow(
        self,
        mid: Optional[str] = None,
        eMid: Optional[str] = None,
    ):
        """Follow to traget's VOOM."""
        METHOD_NAME = "follow"
        params = [[12, 2, [[12, 1, [[11, 1, mid], [11, 2, eMid]]]]]]
        return self.__sender.send(METHOD_NAME, params)

    def unfollow(
        self,
        mid: Optional[str] = None,
        eMid: Optional[str] = None,
    ):
        """Unfollow."""
        METHOD_NAME = "unfollow"
        params = [[12, 2, [[12, 1, [[11, 1, mid], [11, 2, eMid]]]]]]
        return self.__sender.send(METHOD_NAME, params)

    def bulkFollow(
        self, followTargetMids: List[str], unfollowTargetMids: List[str], hasNext: bool
    ):
        """Bulk follow."""
        METHOD_NAME = "bulkFollow"
        params = [
            [14, 1, [11, followTargetMids]],
            [14, 2, [11, unfollowTargetMids]],
            [2, 3, hasNext],
        ]
        params = [[12, 2, params]]
        return self.__sender.send(METHOD_NAME, params)

    def decryptFollowEMid(self, eMid: str):
        """Decrypt follow EMid"""
        METHOD_NAME = "decryptFollowEMid"
        params = [[11, 2, eMid]]
        return self.__sender.send(METHOD_NAME, params)

    def getMessageReadRange(self, chatIds: List[str]):
        """Get message read range."""
        METHOD_NAME = "getMessageReadRange"
        params = [[15, 2, [11, chatIds]]]
        return self.__sender.send(METHOD_NAME, params)

    def getChatRoomBGMs(self, chatIds: List[str]):
        """Get chat room BGM by chatIds."""
        METHOD_NAME = "getChatRoomBGMs"
        params = [[14, 2, [11, chatIds]]]
        return self.__sender.send(METHOD_NAME, params)

    def updateChatRoomBGM(self, chatId: str, chatRoomBGMInfo: str):
        """Update chat room BGM."""
        METHOD_NAME = "updateChatRoomBGM"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, chatId],
            [11, 3, chatRoomBGMInfo],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def addSnsId(self, snsAccessToken: str):
        """
        Add sns id.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "addSnsId"
        params = [
            [8, 2, 1],  # FB?
            [11, 3, snsAccessToken],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def removeSnsId(self):
        """
        Remove sns id.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "removeSnsId"
        params = [
            [8, 2, 1],  # FB?
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getContactRegistration(self, mid: str, type=0):
        METHOD_NAME = "getContactRegistration"
        """
        Get contact registration.

        DEPRECATED: This is a DevKit method.
        """
        params = [
            [11, 1, mid],
            [8, 2, type],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getHiddenContactMids(self):
        """
        Get hidden contact mids.

        DEPRECATED: Avoid using this method unless you are confident in your understanding of its effects.
        """
        METHOD_NAME = "getHiddenContactMids"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def blockRecommendation(self, mid: str):
        """Block recommendation."""
        METHOD_NAME = "blockRecommendation"
        params = [[11, 2, mid]]
        return self.__sender.send(METHOD_NAME, params)

    def unblockRecommendation(self, mid: str):
        """Unblock recommendation."""
        METHOD_NAME = "unblockRecommendation"
        params = [[11, 2, mid]]
        return self.__sender.send(METHOD_NAME, params)

    def getRecommendationIds(self):
        """Get recommendation ids."""
        METHOD_NAME = "getRecommendationIds"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def sync(
        self,
        revision: int,
        count: int = 100,
        fullSyncRequestReason: Optional[int] = None,
        lastPartialFullSyncs: Optional[dict] = None,
    ):
        """
        sync Ops.

        - fullSyncRequestReason:
            OTHER(0),
            INITIALIZATION(1),
            PERIODIC_SYNC(2),
            MANUAL_SYNC(3),
            LOCAL_DB_CORRUPTED(4);

        """
        METHOD_NAME = "sync"
        # 2021/7/26 it blocked, but 2021/7/20 it working
        # LINE are u here?
        # OH, just work for IOS, but 2021/07/20 it works with ANDROID :)
        # 2022/04/20, sync() added to ANDROID apk
        params = TalkServiceStruct.SyncRequest(
            revision,
            count,
            self.globalRev,
            self.individualRev,
            fullSyncRequestReason,
            lastPartialFullSyncs,
        )
        sqrd = self.client.generateDummyProtocol("sync", params, 4)
        res = self.client.postPackDataAndGetUnpackRespData(
            "/SYNC5",
            sqrd,
            5,
            readWith=f"SyncService.{METHOD_NAME}",
            timeout=180,
            conn=self.sync_conn,
        )
        sht, shd = self.talk_handler.SyncHandler(res)
        if sht == 1:
            return shd
        elif sht == 2 and isinstance(shd, int):
            return self.sync(shd, count)
        raise RuntimeError

    def updateChatRoomAnnouncement(
        self, gid: str, announcementId: int, messageLink: str, text: str, imgLink: str
    ):
        METHOD_NAME = "updateChatRoomAnnouncement"
        params = [
            [11, 2, gid],
            [10, 3, announcementId],
            [12, 4, [[8, 1, 5], [11, 2, text], [11, 3, messageLink], [11, 4, imgLink]]],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def reissueTrackingTicket(self):
        METHOD_NAME = "reissueTrackingTicket"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getExtendedProfile(self, syncReason=7):
        METHOD_NAME = "getExtendedProfile"
        params = [[8, 1, syncReason]]
        return self.__sender.send(METHOD_NAME, params)

    def updateExtendedProfileAttribute(
        self,
        year: str,
        yearPrivacyLevelType: int,
        yearEnabled: bool,
        day: str,
        dayPrivacyLevelType: int,
        dayEnabled: bool,
    ):
        """
        - PrivacyLevelType
            PUBLIC(0),
            PRIVATE(1);
        """
        METHOD_NAME = "updateExtendedProfileAttribute"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [8, 2, 0],  # attr
            [
                12,
                3,
                [
                    [
                        12,
                        1,
                        [
                            [11, 1, year],
                            [8, 2, yearPrivacyLevelType],
                            [2, 3, yearEnabled],
                            [11, 5, day],
                            [8, 6, dayPrivacyLevelType],
                            [2, 7, dayEnabled],
                        ],
                    ]
                ],
            ],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def setNotificationsEnabled(self, type: int, target: str, enablement: bool = True):
        """
        - type
            USER(0),
            ROOM(1),
            GROUP(2),
            SQUARE(3),
            SQUARE_CHAT(4),
            SQUARE_MEMBER(5),
            BOT(6);
        """
        METHOD_NAME = "setNotificationsEnabled"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [8, 2, type],  # attr
            [11, 3, target],
            [2, 4, enablement],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def findAndAddContactsByPhone(
        self,
        phones: list,
        reference: str = '{"screen":"groupMemberList","spec":"native"}',
    ):
        METHOD_NAME = "findAndAddContactsByPhone"
        if type(phones) != list:
            raise Exception("[findAndAddContactsByPhone] phones must be a list")
        params = [
            [8, 1, self.client.getCurrReqId()],
            [14, 2, [11, phones]],
            [11, 3, reference],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def findAndAddContactsByUserid(
        self,
        searchId: str,
        reference: str = '{"screen":"friendAdd:idSearch","spec":"native"}',
    ):
        METHOD_NAME = "findAndAddContactsByUserid"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, searchId],
            [11, 3, reference],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def syncContacts(self, phones: list = [], emails: list = [], userids: list = []):
        """
        - type
            ADD(0),
            REMOVE(1),
            MODIFY(2);

        ** NOTE: need turn on the 'allow_sync' setting.
        """
        METHOD_NAME = "syncContacts"
        if type(phones) != list:
            raise Exception("[syncContacts] phones must be a list")
        if type(emails) != list:
            raise Exception("[syncContacts] emails must be a list")
        if type(userids) != list:
            raise Exception("[syncContacts] userids must be a list")
        localContacts = []
        luid = 0
        for phone in phones:
            luid += 1
            localContacts.append(
                [
                    [8, 1, 0],
                    [11, 2, luid],
                    [15, 11, [11, [phone]]],
                ]
            )
        for email in emails:
            luid += 1
            localContacts.append(
                [
                    [8, 1, 0],
                    [11, 2, luid],
                    [15, 12, [11, [email]]],
                ]
            )
        for userid in userids:
            luid += 1
            localContacts.append(
                [
                    [8, 1, 0],
                    [11, 2, luid],
                    [15, 13, [11, [userid]]],
                ]
            )
        base_localContacts = [
            [8, 1, 0],
            [11, 2, luid],
            [15, 11, [11, phones]],
            [15, 12, [11, emails]],
            [15, 13, [11, userids]],
            # [11, 14, mobileContactName],
            # [11, 15, phoneticName],
        ]
        params = [
            [8, 1, self.client.getCurrReqId()],
            [15, 2, [12, localContacts]],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getContactWithFriendRequestStatus(self, mid: str):
        METHOD_NAME = "getContactWithFriendRequestStatus"
        params = [[8, 1, self.client.getCurrReqId()], [11, 2, mid]]
        return self.__sender.send(METHOD_NAME, params)

    def findContactsByPhone(self, phones: list):
        METHOD_NAME = "findContactsByPhone"
        if type(phones) != list:
            raise Exception("[findContactsByPhone] phones must be a list")
        params = [[14, 2, [11, phones]]]
        return self.__sender.send(METHOD_NAME, params)

    def findContactByUserid(self, searchId: str):
        METHOD_NAME = "findContactByUserid"
        params = [[11, 2, searchId]]
        return self.__sender.send(METHOD_NAME, params)

    def findContactByMetaTag(
        self,
        searchId: str,
        reference: str = '{"screen":"groupMemberList","spec":"native"}',
    ):
        METHOD_NAME = "findContactByMetaTag"
        params = [[11, 2, searchId], [11, 3, reference]]
        return self.__sender.send(METHOD_NAME, params)

    def findAndAddContactByMetaTag(
        self,
        searchId: str,
        reference: str = '{"screen":"groupMemberList","spec":"native"}',
    ):
        METHOD_NAME = "findAndAddContactByMetaTag"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, searchId],
            [11, 3, reference],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def updateContactSetting(self, mid: str, flag: int, value: str):
        """
        - flag
            CONTACT_SETTING_NOTIFICATION_DISABLE(1),
            CONTACT_SETTING_DISPLAY_NAME_OVERRIDE(2),
            CONTACT_SETTING_CONTACT_HIDE(4),
            CONTACT_SETTING_FAVORITE(8),
            CONTACT_SETTING_DELETE(16);
        """
        METHOD_NAME = "updateContactSetting"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, mid],
            [8, 3, flag],
            [11, 4, value],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getFavoriteMids(self):
        METHOD_NAME = "getFavoriteMids"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def sendMessageAwaitCommit(self):
        METHOD_NAME = "sendMessageAwaitCommit"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def findContactByUserTicket(self, ticketIdWithTag: str):
        METHOD_NAME = "findContactByUserTicket"
        params = [[11, 2, ticketIdWithTag]]
        return self.__sender.send(METHOD_NAME, params)

    def invalidateUserTicket(self):
        METHOD_NAME = "invalidateUserTicket"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def unregisterUserAndDevice(self):
        METHOD_NAME = "unregisterUserAndDevice"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def verifyQrcode(self, verifier: str, pinCode: str):
        METHOD_NAME = "verifyQrcode"
        params = [
            [11, 2, verifier],
            [11, 3, pinCode],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def reportAbuseEx(
        self, message: Optional[list] = None, lineMeeting: Optional[list] = None
    ):
        """
        - reportSource
            UNKNOWN(0),
            DIRECT_INVITATION(1),
            DIRECT_CHAT(2),
            GROUP_INVITATION(3),
            GROUP_CHAT(4),
            ROOM_INVITATION(5),
            ROOM_CHAT(6),
            FRIEND_PROFILE(7),
            DIRECT_CHAT_SELECTED(8),
            GROUP_CHAT_SELECTED(9),
            ROOM_CHAT_SELECTED(10),
            DEPRECATED(11);
        - spammerReasons
            OTHER(0),
            ADVERTISING(1),
            GENDER_HARASSMENT(2),
            HARASSMENT(3);
        """
        METHOD_NAME = "reportAbuseEx"
        if message is None and lineMeeting is None:
            raise Exception(
                "Should use reportAbuseExWithMessage() or reportAbuseExWithLineMeeting()"
            )
        params = [
            [
                12,
                2,
                [
                    [
                        12,
                        1,
                        [
                            [12, 1, message],
                            [12, 2, lineMeeting],
                        ],
                    ],
                ],
            ],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def reportAbuseExWithMessage(
        self,
        reportSource: int,
        spammerReasons: int,
        messageIds: list,
        messages: list,
        senderMids: list,
        contentTypes: list,
        createdTimes: list,
        metadatas: list,
        metadata: dict,
        applicationType: int = 384,
    ):
        abuseMessages = []

        def _get(a, b, c):
            return a[b] if len(a) > b else c

        for i in range(len(messageIds)):
            abuseMessages.append(
                [
                    [10, 1, _get(messageIds, i, 0)],
                    [11, 2, _get(messages, i, "")],
                    [11, 3, _get(senderMids, i, "")],
                    [8, 4, _get(contentTypes, i, 0)],
                    [10, 5, _get(createdTimes, i, 0)],
                    [13, 6, [11, 11, _get(metadatas, i, {})]],
                ]
            )
        # metadata["groupMid"] = groupMid
        # metadata["groupName"] = groupName
        # metadata["inviterMid"] = inviterMid
        # metadata["picturePath"] = picturePath
        withMessage = [
            [8, 1, reportSource],
            [8, 2, applicationType],
            [15, 3, [8, [spammerReasons]]],
            [15, 4, [12, abuseMessages]],
            [13, 5, [11, 11, metadata]],
        ]
        return self.reportAbuseEx(message=withMessage)

    def reportAbuseExWithLineMeeting(
        self,
        reporteeMid: str,
        spammerReasons: int,
        spaceIds: list,
        objectIds: list,
        chatMid: str,
    ):
        evidenceIds = []

        def _get(a, b, c):
            return a[b] if len(a) > b else c

        for i in range(len(spaceIds)):
            evidenceIds.append(
                [
                    [11, 1, _get(spaceIds, i, "")],
                    [11, 2, _get(objectIds, i, "")],
                ]
            )
        withLineMeeting = [
            [11, 1, reporteeMid],
            [15, 2, [8, [spammerReasons]]],
            [15, 3, [12, evidenceIds]],
            [11, 4, chatMid],
        ]
        return self.reportAbuseEx(lineMeeting=withLineMeeting)

    def getCountryWithRequestIp(self):
        METHOD_NAME = "getCountryWithRequestIp"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def notifyBuddyOnAir(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("notifyBuddyOnAir is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "notifyBuddyOnAir", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getSuggestRevisions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSuggestRevisions is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getSuggestRevisions", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def updateProfileAttributes(
        self, profileAttribute: int, value: str, meta: dict = {}
    ):
        """Update profile attributes."""
        METHOD_NAME = "updateProfileAttributes"
        ProfileContent = [
            [11, 1, value],
            [13, 2, [11, 11, meta]],
        ]
        UpdateProfileAttributesRequest = [
            [13, 1, [8, 12, {profileAttribute: ProfileContent}]]
        ]
        params = [
            [8, 1, self.client.getCurrReqId()],
            [12, 2, UpdateProfileAttributesRequest],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def updateNotificationToken(self, token: str, type: int = 21):
        METHOD_NAME = "updateNotificationToken"
        params = [[11, 2, token], [8, 3, type]]  # generated by google api
        return self.__sender.send(METHOD_NAME, params)

    def disableNearby(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("disableNearby is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "disableNearby", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def createRoom(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("createRoom is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "createRoom", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def tryFriendRequest(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("tryFriendRequest is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "tryFriendRequest", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def generateUserTicket(self, expirationTime: int, maxUseCount: int):
        METHOD_NAME = "generateUserTicket"
        params = [[10, 3, expirationTime], [8, 4, maxUseCount]]
        return self.__sender.send(METHOD_NAME, params)

    def getRecentFriendRequests(self):
        METHOD_NAME = "getRecentFriendRequests"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def updateSettingsAttribute(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSettingsAttribute is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "updateSettingsAttribute", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def resendPinCode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("resendPinCode is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "resendPinCode", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def notifyRegistrationComplete(
        self,
        udidHash: str,
        applicationTypeWithExtensions: str = "ANDROID\t11.19.1\tAndroid OS\t7.0",
    ):
        METHOD_NAME = "notifyRegistrationComplete"
        params = [
            [11, 2, udidHash],  # len 32 hash
            [11, 3, applicationTypeWithExtensions],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def createGroupV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("createGroupV2 is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "createGroupV2", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def reportSpam(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSpam is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "reportSpam", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def requestResendMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("requestResendMessage is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "requestResendMessage", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def inviteFriendsBySms(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("inviteFriendsBySms is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "inviteFriendsBySms", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def findGroupByTicketV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findGroupByTicketV2 is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "findGroupByTicketV2", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getInstantNews(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getInstantNews is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getInstantNews", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def createQrcodeBase64Image(self, url: str):
        METHOD_NAME = "createQrcodeBase64Image"
        params = [[11, 2, url]]
        return self.__sender.send(METHOD_NAME, params)

    def findSnsIdUserStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findSnsIdUserStatus is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "findSnsIdUserStatus", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getPendingAgreements(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPendingAgreements is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getPendingAgreements", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def verifyIdentityCredentialWithResult(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyIdentityCredentialWithResult is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "verifyIdentityCredentialWithResult", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def registerWithSnsId(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerWithSnsId is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "registerWithSnsId", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def verifyAccountMigration(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyAccountMigration is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "verifyAccountMigration", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getEncryptedIdentityV3(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getEncryptedIdentityV3 is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getEncryptedIdentityV3", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def reissueGroupTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reissueGroupTicket is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "reissueGroupTicket", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getUserTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getUserTicket is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getUserTicket", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def changeVerificationMethod(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("changeVerificationMethod is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "changeVerificationMethod", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getRooms(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRooms is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getRooms", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getAcceptedProximityMatches(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getAcceptedProximityMatches is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getAcceptedProximityMatches", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getChatEffectMetaList(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getChatEffectMetaList is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getChatEffectMetaList", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def notifyInstalled(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("notifyInstalled is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "notifyInstalled", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def reissueUserTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reissueUserTicket is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "reissueUserTicket", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def sendDummyPush(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("sendDummyPush is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "sendDummyPush", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def verifyAccountMigrationPincode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyAccountMigrationPincode is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "verifyAccountMigrationPincode", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def registerDeviceWithoutPhoneNumberWithIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "registerDeviceWithoutPhoneNumberWithIdentityCredential is not implemented"
        )
        params = []
        sqrd = self.client.generateDummyProtocol(
            "registerDeviceWithoutPhoneNumberWithIdentityCredential",
            params,
            self.TalkService_REQ_TYPE,
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def registerDeviceWithoutPhoneNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerDeviceWithoutPhoneNumber is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "registerDeviceWithoutPhoneNumber", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def inviteIntoGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("inviteIntoGroup is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "inviteIntoGroup", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def removeAllMessages(self, lastMessageId: str):
        METHOD_NAME = "removeAllMessages"
        params = [[8, 1, self.client.getCurrReqId()], [11, 1, lastMessageId]]
        return self.__sender.send(METHOD_NAME, params)

    def registerWithPhoneNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerWithPhoneNumber is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "registerWithPhoneNumber", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getRingbackTone(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRingbackTone is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getRingbackTone", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def reportSpammer(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSpammer is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "reportSpammer", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def loginWithVerifierForCerificate(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithVerifierForCerificate is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "loginWithVerifierForCerificate", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def logoutSession(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("logoutSession is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "logoutSession", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def clearIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("clearIdentityCredential is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "clearIdentityCredential", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def updateGroupPreferenceAttribute(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateGroupPreferenceAttribute is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "updateGroupPreferenceAttribute", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def closeProximityMatch(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("closeProximityMatch is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "closeProximityMatch", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def loginWithVerifierForCertificate(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithVerifierForCertificate is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "loginWithVerifierForCertificate", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def respondResendMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("respondResendMessage is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "respondResendMessage", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getProximityMatchCandidateList(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getProximityMatchCandidateList is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getProximityMatchCandidateList", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def reportDeviceState(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportDeviceState is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "reportDeviceState", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def sendChatRemoved(self, chatMid: str, lastMessageId: str):
        METHOD_NAME = "sendChatRemoved"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [11, 2, chatMid],
            [11, 3, lastMessageId],
            # [3, 4, sessionId]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getAuthQrcode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getAuthQrcode is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getAuthQrcode", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def updateAccountMigrationPincode(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateAccountMigrationPincode is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "updateAccountMigrationPincode", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def registerWithSnsIdAndIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerWithSnsIdAndIdentityCredential is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "registerWithSnsIdAndIdentityCredential", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def startUpdateVerification(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("startUpdateVerification is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "startUpdateVerification", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def notifySleep(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("notifySleep is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "notifySleep", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def reportContacts(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportContacts is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "reportContacts", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def acceptGroupInvitation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("acceptGroupInvitation is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "acceptGroupInvitation", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def loginWithVerifier(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithVerifier is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "loginWithVerifier", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def updateSettingsAttributes(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSettingsAttributes is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "updateSettingsAttributes", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def verifyPhoneNumberForLogin(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyPhoneNumberForLogin is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "verifyPhoneNumberForLogin", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getUpdatedMessageBoxIds(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getUpdatedMessageBoxIds is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getUpdatedMessageBoxIds", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def inviteIntoRoom(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("inviteIntoRoom is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "inviteIntoRoom", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def removeFriendRequest(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("removeFriendRequest is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "removeFriendRequest", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def acceptGroupInvitationByTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("acceptGroupInvitationByTicket is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "acceptGroupInvitationByTicket", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def reportProfile(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportProfile is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "reportProfile", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def updateProfile(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateProfile is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "updateProfile", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def createGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("createGroup is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "createGroup", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def resendEmailConfirmation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("resendEmailConfirmation is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "resendEmailConfirmation", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def registerWithPhoneNumberAndPassword(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerWithPhoneNumberAndPassword is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "registerWithPhoneNumberAndPassword", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def openProximityMatch(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("openProximityMatch is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "openProximityMatch", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def verifyPhone(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyPhone is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "verifyPhone", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getSessions(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSessions is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getSessions", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def clearRingbackTone(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("clearRingbackTone is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "clearRingbackTone", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def leaveGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("leaveGroup is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "leaveGroup", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getProximityMatchCandidates(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getProximityMatchCandidates is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getProximityMatchCandidates", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def createAccountMigrationPincodeSession(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("createAccountMigrationPincodeSession is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "createAccountMigrationPincodeSession", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getRoom(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRoom is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getRoom", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def startVerification(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("startVerification is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "startVerification", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def logout(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("logout is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "logout", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def updateNotificationTokenWithBytes(self, bData: bytes, bindType: int = 1):
        """Update notification token with bytes.

        this could be for Google Cloud Messaging(GCM) service or Apple Push Notification(APNS) service.
        """
        METHOD_NAME = "updateNotificationTokenWithBytes"
        params = [[11, 2, bData], [8, 3, bindType]]
        return self.__sender.send(METHOD_NAME, params)

    def confirmEmail(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("confirmEmail is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "confirmEmail", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getIdentityIdentifier(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getIdentityIdentifier is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getIdentityIdentifier", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def updateDeviceInfo(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateDeviceInfo is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "updateDeviceInfo", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def registerDeviceWithIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerDeviceWithIdentityCredential is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "registerDeviceWithIdentityCredential", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def wakeUpLongPolling(self, clientRevision: int):
        METHOD_NAME = "wakeUpLongPolling"
        params = [[10, 2, clientRevision]]
        return self.__sender.send(METHOD_NAME, params)

    def updateAndGetNearby(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateAndGetNearby is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "updateAndGetNearby", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getSettingsAttributes(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSettingsAttributes is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getSettingsAttributes", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def rejectGroupInvitation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("rejectGroupInvitation is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "rejectGroupInvitation", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def loginWithIdentityCredentialForCertificate(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithIdentityCredentialForCertificate is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "loginWithIdentityCredentialForCertificate",
            params,
            self.TalkService_REQ_TYPE,
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def reportSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportSettings is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "reportSettings", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def registerWithExistingSnsIdAndIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "registerWithExistingSnsIdAndIdentityCredential is not implemented"
        )
        params = []
        sqrd = self.client.generateDummyProtocol(
            "registerWithExistingSnsIdAndIdentityCredential",
            params,
            self.TalkService_REQ_TYPE,
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def requestAccountPasswordReset(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("requestAccountPasswordReset is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "requestAccountPasswordReset", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def requestEmailConfirmation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("requestEmailConfirmation is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "requestEmailConfirmation", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def resendPinCodeBySMS(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("resendPinCodeBySMS is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "resendPinCodeBySMS", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getSuggestIncrements(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSuggestIncrements is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getSuggestIncrements", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def noop(self):
        METHOD_NAME = "noop"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getSuggestSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getSuggestSettings is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getSuggestSettings", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def acceptProximityMatches(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("acceptProximityMatches is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "acceptProximityMatches", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def kickoutFromGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("kickoutFromGroup is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "kickoutFromGroup", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def verifyIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyIdentityCredential is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "verifyIdentityCredential", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def loginWithIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("loginWithIdentityCredential is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "loginWithIdentityCredential", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def setIdentityCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("setIdentityCredential is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "setIdentityCredential", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getBuddyLocation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyLocation is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getBuddyLocation", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def verifyPhoneNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("verifyPhoneNumber is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "verifyPhoneNumber", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def registerDevice(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("registerDevice is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "registerDevice", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getRingtone(self):
        METHOD_NAME = "getRingtone"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def findGroupByTicket(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findGroupByTicket is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "findGroupByTicket", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def reportClientStatistics(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportClientStatistics is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "reportClientStatistics", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def updateGroup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateGroup is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "updateGroup", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getEncryptedIdentityV2(self):
        METHOD_NAME = "getEncryptedIdentityV2"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def reportAbuse(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reportAbuse is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "reportAbuse", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getAnalyticsInfo(self):
        METHOD_NAME = "getAnalyticsInfo"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getCompactGroups(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getCompactGroups is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getCompactGroups", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def setBuddyLocation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("setBuddyLocation is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "setBuddyLocation", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def isUseridAvailable(self, searchId: str):
        METHOD_NAME = "isUseridAvailable"
        params = [[11, 2, searchId]]
        return self.__sender.send(METHOD_NAME, params)

    def removeBuddyLocation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("removeBuddyLocation is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "removeBuddyLocation", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def report(self, syncOpRevision: int, category: int, report: str):
        """
        - category:
            PROFILE(0),
        SETTINGS(1),
        OPS(2),
        CONTACT(3),
        RECOMMEND(4),
        BLOCK(5),
        GROUP(6),
        ROOM(7),
        NOTIFICATION(8),
        ADDRESS_BOOK(9);
        """
        METHOD_NAME = "report"
        params = [
            [10, 2, syncOpRevision],
            [8, 3, category],
            [11, 4, report],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def registerUserid(self, searchId: str):
        METHOD_NAME = "registerUserid"
        params = [[8, 1, self.client.getCurrReqId()], [11, 2, searchId]]
        return self.__sender.send(METHOD_NAME, params)

    def finishUpdateVerification(self, sessionId: str):
        METHOD_NAME = "finishUpdateVerification"
        params = [[11, 2, sessionId]]
        return self.__sender.send(METHOD_NAME, params)

    def notifySleepV2(self, revision: int):
        """
        2022/04/25
        """
        METHOD_NAME = "notifySleepV2"
        params = [
            [
                2,
                12,
                [
                    [1, 12, [[10, 1, revision], [8, 2, 1]]],
                    [
                        2,
                        12,
                        [
                            [8, 1, 0],
                            [8, 2, 0],
                        ],
                    ],
                ],
            ]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getCompactRoom(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getCompactRoom is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getCompactRoom", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def cancelGroupInvitation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("cancelGroupInvitation is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "cancelGroupInvitation", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def clearRingtone(self, oid: str):
        METHOD_NAME = "clearRingtone"
        params = [[11, 1, oid]]
        return self.__sender.send(METHOD_NAME, params)

    def notifyUpdated(
        self,
        lastRev: int,
        udidHash: str,
        oldUdidHash: str,
        deviceName: str = "DeachSword",
        systemName: str = "Android OS",
        systemVersion: str = "9.1",
        model: str = "DeachSword",
        webViewVersion: str = "96.0.4664.45",
        carrierCode: int = 0,
        carrierName: str = "",
        applicationType: int = 32,
    ):
        METHOD_NAME = "notifyUpdated"
        params = [
            [10, 2, lastRev],
            [
                12,
                3,
                [
                    [11, 1, deviceName],  # DeachSword
                    [11, 2, systemName],  # Android OS
                    [11, 3, systemVersion],  # 9.1
                    [11, 4, model],  # DeachSword
                    [11, 5, webViewVersion],  # 96.0.4664.45
                    [8, 10, carrierCode],  # 0
                    [11, 10, carrierName],
                    [8, 20, applicationType],  # 32
                ],
            ],
            [11, 4, udidHash],  # 57f44905fd117a5661828440bb7d1bd5
            [11, 4, oldUdidHash],  # 5284047f4ffb4e04824a2fd1d1f0cd62
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getGroupWithoutMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getGroupWithoutMembers is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getGroupWithoutMembers", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def getShakeEventV1(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getShakeEventV1 is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "getShakeEventV1", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def reportPushRecvReports(
        self,
        pushTrackingId: str,
        recvTimestamp: int,
        battery: int = 100,
        batteryMode: int = 1,
        clientNetworkType: int = 1,
        carrierCode: str = "",
        displayTimestamp: int = 0,
    ):
        METHOD_NAME = "reportPushRecvReports"
        pushRecvReports = []
        pushRecvReports.append(
            [
                [11, 1, pushTrackingId],  # E5DNYLDgRI6uEHUNdDWFqg==
                [10, 2, recvTimestamp],  # 1637752269347
                [8, 3, battery],
                [8, 4, batteryMode],
                [8, 5, clientNetworkType],
                [11, 6, carrierCode],
                [10, 7, displayTimestamp],
            ]
        )
        params = [[8, 1, 0], [15, 2, [12, pushRecvReports]]]
        return self.__sender.send(METHOD_NAME, params)

    def getFriendRequests(
        self, direction: int = 1, lastSeenSeqId: Optional[int] = None
    ):
        """
        -  direction:
            INCOMING(1),
            OUTGOING(2);
        """
        METHOD_NAME = "getFriendRequests"
        params = [[8, 1, direction], [10, 2, lastSeenSeqId]]
        return self.__sender.send(METHOD_NAME, params)

    def requestIdentityUnbind(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("requestIdentityUnbind is not implemented")
        params = []
        sqrd = self.client.generateDummyProtocol(
            "requestIdentityUnbind", params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH,
            sqrd,
            self.TalkService_RES_TYPE,
        )

    def addToFollowBlacklist(
        self, mid: Optional[str] = None, eMid: Optional[str] = None
    ):
        METHOD_NAME = "addToFollowBlacklist"
        params = [
            [
                12,
                2,
                [
                    [
                        12,
                        1,
                        [
                            [11, 1, mid],
                            [11, 2, eMid],
                        ],
                    ]
                ],
            ]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def removeFromFollowBlacklist(
        self, mid: Optional[str] = None, eMid: Optional[str] = None
    ):
        METHOD_NAME = "removeFromFollowBlacklist"
        params = [
            [
                12,
                2,
                [
                    [
                        12,
                        1,
                        [
                            [11, 1, mid],
                            [11, 2, eMid],
                        ],
                    ]
                ],
            ]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getFollowBlacklist(self, cursor: Optional[str] = None):
        METHOD_NAME = "getFollowBlacklist"
        params = [[12, 2, [[11, 1, cursor]]]]
        return self.__sender.send(METHOD_NAME, params)

    def determineMediaMessageFlow(self, chatMid: str):
        METHOD_NAME = "determineMediaMessageFlow"
        params = TalkServiceStruct.DetermineMediaMessageFlowRequest(chatMid)
        return self.__sender.send(METHOD_NAME, params)

    def getPublicKeychain(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getPublicKeychain is not implemented")
        METHOD_NAME = "getPublicKeychain"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def sendMessageReceipt(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("sendMessageReceipt is not implemented")
        METHOD_NAME = "sendMessageReceipt"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def commitSendMessages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("commitSendMessages is not implemented")
        METHOD_NAME = "commitSendMessages"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getNotificationPolicy(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getNotificationPolicy is not implemented")
        METHOD_NAME = "getNotificationPolicy"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def sendMessageToMyHome(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("sendMessageToMyHome is not implemented")
        METHOD_NAME = "sendMessageToMyHome"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getWapInvitation(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getWapInvitation is not implemented")
        METHOD_NAME = "getWapInvitation"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getBuddySubscriberStates(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getBuddySubscriberStates is not implemented")
        METHOD_NAME = "getBuddySubscriberStates"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def storeUpdateProfileAttribute(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("storeUpdateProfileAttribute is not implemented")
        METHOD_NAME = "storeUpdateProfileAttribute"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def notifyIndividualEvent(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("notifyIndividualEvent is not implemented")
        METHOD_NAME = "notifyIndividualEvent"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def clearMessageBox(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("clearMessageBox is not implemented")
        METHOD_NAME = "clearMessageBox"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def updateCustomModeSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updateCustomModeSettings is not implemented")
        METHOD_NAME = "updateCustomModeSettings"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def updateSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updateSettings is not implemented")
        METHOD_NAME = "updateSettings"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def sendMessageIgnored(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("sendMessageIgnored is not implemented")
        METHOD_NAME = "sendMessageIgnored"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def findAndAddContactsByEmail(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("findAndAddContactsByEmail is not implemented")
        METHOD_NAME = "findAndAddContactsByEmail"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getMessageBoxCompactWrapUp(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxCompactWrapUp is not implemented")
        METHOD_NAME = "getMessageBoxCompactWrapUp"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getPreviousMessages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getPreviousMessages is not implemented")
        METHOD_NAME = "getPreviousMessages"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def commitUpdateProfile(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("commitUpdateProfile is not implemented")
        METHOD_NAME = "commitUpdateProfile"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def registerBuddyUser(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("registerBuddyUser is not implemented")
        METHOD_NAME = "registerBuddyUser"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getMessagesBySequenceNumber(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessagesBySequenceNumber is not implemented")
        METHOD_NAME = "getMessagesBySequenceNumber"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def commitSendMessagesToMid(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("commitSendMessagesToMid is not implemented")
        METHOD_NAME = "commitSendMessagesToMid"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def isIdentityIdentifierAvailable(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("isIdentityIdentifierAvailable is not implemented")
        METHOD_NAME = "isIdentityIdentifierAvailable"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getMessageBoxList(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxList is not implemented")
        METHOD_NAME = "getMessageBoxList"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def registerWapDevice(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("registerWapDevice is not implemented")
        METHOD_NAME = "registerWapDevice"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def sendContentReceipt(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("sendContentReceipt is not implemented")
        METHOD_NAME = "sendContentReceipt"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def updateC2DMRegistrationId(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updateC2DMRegistrationId is not implemented")
        METHOD_NAME = "updateC2DMRegistrationId"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getMessageBoxListByStatus(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxListByStatus is not implemented")
        METHOD_NAME = "getMessageBoxListByStatus"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def createSession(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("createSession is not implemented")
        METHOD_NAME = "createSession"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getOldReadMessageOpsWithRange(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getOldReadMessageOpsWithRange is not implemented")
        METHOD_NAME = "getOldReadMessageOpsWithRange"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def inviteViaEmail(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("inviteViaEmail is not implemented")
        METHOD_NAME = "inviteViaEmail"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def reportRooms(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("reportRooms is not implemented")
        METHOD_NAME = "reportRooms"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def reportGroups(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("reportGroups is not implemented")
        METHOD_NAME = "reportGroups"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def removeMessageFromMyHome(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("removeMessageFromMyHome is not implemented")
        METHOD_NAME = "removeMessageFromMyHome"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getMessageBoxV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxV2 is not implemented")
        METHOD_NAME = "getMessageBoxV2"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def destroyMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("destroyMessage is not implemented")
        METHOD_NAME = "destroyMessage"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getCompactContactsModifiedSince(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getCompactContactsModifiedSince is not implemented")
        METHOD_NAME = "getCompactContactsModifiedSince"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def notifiedRedirect(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("notifiedRedirect is not implemented")
        METHOD_NAME = "notifiedRedirect"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def updateSettings2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updateSettings2 is not implemented")
        METHOD_NAME = "updateSettings2"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def reissueDeviceCredential(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("reissueDeviceCredential is not implemented")
        METHOD_NAME = "reissueDeviceCredential"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def registerBuddyUserid(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("registerBuddyUserid is not implemented")
        METHOD_NAME = "registerBuddyUserid"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getMessageBox(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBox is not implemented")
        METHOD_NAME = "getMessageBox"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getMessageBoxWrapUpListV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxWrapUpListV2 is not implemented")
        METHOD_NAME = "getMessageBoxWrapUpListV2"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def fetchAnnouncements(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("fetchAnnouncements is not implemented")
        METHOD_NAME = "fetchAnnouncements"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def sendEvent(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("sendEvent is not implemented")
        METHOD_NAME = "sendEvent"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def syncContactBySnsIds(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("syncContactBySnsIds is not implemented")
        METHOD_NAME = "syncContactBySnsIds"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def validateContactsOnBot(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("validateContactsOnBot is not implemented")
        METHOD_NAME = "validateContactsOnBot"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def trySendMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("trySendMessage is not implemented")
        METHOD_NAME = "trySendMessage"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getNextMessages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getNextMessages is not implemented")
        METHOD_NAME = "getNextMessages"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def updatePublicKeychain(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updatePublicKeychain is not implemented")
        METHOD_NAME = "updatePublicKeychain"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getMessageBoxWrapUpList(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxWrapUpList is not implemented")
        METHOD_NAME = "getMessageBoxWrapUpList"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def removeMessage(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("removeMessage is not implemented")
        METHOD_NAME = "removeMessage"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getMessageBoxWrapUp(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxWrapUp is not implemented")
        METHOD_NAME = "getMessageBoxWrapUp"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def releaseSession(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("releaseSession is not implemented")
        METHOD_NAME = "releaseSession"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getMessageBoxWrapUpV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxWrapUpV2 is not implemented")
        METHOD_NAME = "getMessageBoxWrapUpV2"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getActiveBuddySubscriberIds(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getActiveBuddySubscriberIds is not implemented")
        METHOD_NAME = "getActiveBuddySubscriberIds"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getSystemConfiguration(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getSystemConfiguration is not implemented")
        METHOD_NAME = "getSystemConfiguration"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def notifyUpdatePublicKeychain(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("notifyUpdatePublicKeychain is not implemented")
        METHOD_NAME = "notifyUpdatePublicKeychain"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getBlockedContactIdsByRange(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getBlockedContactIdsByRange is not implemented")
        METHOD_NAME = "getBlockedContactIdsByRange"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getLastAnnouncementIndex(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getLastAnnouncementIndex is not implemented")
        METHOD_NAME = "getLastAnnouncementIndex"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getMessageBoxCompactWrapUpV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getMessageBoxCompactWrapUpV2 is not implemented")
        METHOD_NAME = "getMessageBoxCompactWrapUpV2"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def sendContentPreviewUpdated(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("sendContentPreviewUpdated is not implemented")
        METHOD_NAME = "sendContentPreviewUpdated"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getBuddyBlockerIds(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("getBuddyBlockerIds is not implemented")
        METHOD_NAME = "getBuddyBlockerIds"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def updateBuddySetting(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updateBuddySetting is not implemented")
        METHOD_NAME = "updateBuddySetting"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def updateApnsDeviceToken(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("updateApnsDeviceToken is not implemented")
        METHOD_NAME = "updateApnsDeviceToken"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def findContactsByEmail(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:19:19
        """
        raise Exception("findContactsByEmail is not implemented")
        METHOD_NAME = "findContactsByEmail"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def agreeToLabFeature(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:35:49
        """
        raise Exception("agreeToLabFeature is not implemented")
        METHOD_NAME = "agreeToLabFeature"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def toggleLabFeature(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:35:49
        """
        raise Exception("toggleLabFeature is not implemented")
        METHOD_NAME = "toggleLabFeature"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getSymmetricKey(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:35:49
        """
        raise Exception("getSymmetricKey is not implemented")
        METHOD_NAME = "getSymmetricKey"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getAgreedToLabFeatures(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:35:49
        """
        raise Exception("getAgreedToLabFeatures is not implemented")
        METHOD_NAME = "getAgreedToLabFeatures"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def cancelReaction(self, messageId: int):
        """
        cancel message reaction by message id.

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 06/30/2022, 01:51:15
        """
        METHOD_NAME = "cancelReaction"
        params = TalkServiceStruct.CancelReactionRequest(messageId)
        return self.__sender.send(METHOD_NAME, params)

    def getNotificationSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 03/10/2023, 13:41:11
        """
        raise Exception("getNotificationSettings is not implemented")
        METHOD_NAME = "getNotificationSettings"
        params = []
        sqrd = self.client.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.client.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def registerE2EEPublicKeyV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 10/31/2024, 14:52:45
        """
        raise Exception("registerE2EEPublicKeyV2 is not implemented")
        METHOD_NAME = "registerE2EEPublicKeyV2"
        params = []
        sqrd = self.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getIncrementalBackupMessages(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 10/31/2024, 14:52:45
        """
        raise Exception("getIncrementalBackupMessages is not implemented")
        METHOD_NAME = "getIncrementalBackupMessages"
        params = []
        sqrd = self.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def updatePinState(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 10/31/2024, 14:52:45
        """
        raise Exception("updatePinState is not implemented")
        METHOD_NAME = "updatePinState"
        params = []
        sqrd = self.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getPinnedChats(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 10/31/2024, 14:52:45
        """
        raise Exception("getPinnedChats is not implemented")
        METHOD_NAME = "getPinnedChats"
        params = []
        sqrd = self.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )

    def getBackupChats(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 10/31/2024, 14:52:45
        """
        raise Exception("getBackupChats is not implemented")
        METHOD_NAME = "getBackupChats"
        params = []
        sqrd = self.generateDummyProtocol(
            METHOD_NAME, params, self.TalkService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.TalkService_API_PATH, sqrd, self.TalkService_RES_TYPE
        )


class TalkServiceStruct(BaseServiceStruct):
    @staticmethod
    def CancelReactionRequest(messageId: int):
        return __class__.BaseRequest([[10, 2, messageId]])

    @staticmethod
    def DetermineMediaMessageFlowRequest(chatMid: str):
        return __class__.BaseRequest([[11, 1, chatMid]])

    @staticmethod
    def SyncRequest(
        revision: int,
        count: int,
        globalRev: int,
        individualRev: int,
        fullSyncRequestReason: Optional[int],
        lastPartialFullSyncs: Optional[dict],
    ):
        params = [
            [10, 1, revision],
            [8, 2, count],
            [10, 3, globalRev],
            [10, 4, individualRev],
            [8, 5, fullSyncRequestReason],
            [13, 6, [8, 10, lastPartialFullSyncs]],
        ]
        return __class__.BaseRequest(params)


class TalkServiceHandler(BaseServiceHandler):
    def __init__(self, client: "CHRLINE") -> None:
        super().__init__(client)

        self.logger = self._logger.overload("TALK")

    def SyncHandler(self, res: Any):
        """
        Sync handler.

        To simplify some checks, it will respond with (type, data).
        - type:
            1: success, and return ops.
            2: need re-sync, return new one revision.
        """
        if res is None:
            return 1, []
        cl = self.cl
        ll = self.logger.overload("Sync")
        isDebugOnly = True
        operationResponse = cl.checkAndGetValue(res, "operationResponse", 1)
        fullSyncResponse = cl.checkAndGetValue(res, "fullSyncResponse", 2)
        partialFullSyncResponse = cl.checkAndGetValue(res, "partialFullSyncResponse", 2)
        ll.debug(f"Resp: {res}")
        if operationResponse is not None:
            ops = cl.checkAndGetValue(operationResponse, "operations", 1)
            hasMoreOps = cl.checkAndGetValue(operationResponse, "hasMoreOps", 2)
            globalEvents = cl.checkAndGetValue(operationResponse, "globalEvents", 3)
            individualEvents = cl.checkAndGetValue(
                operationResponse, "individualEvents", 4
            )
            if globalEvents is not None:
                events = cl.checkAndGetValue(globalEvents, "events", 1)
                lastRevision = cl.checkAndGetValue(globalEvents, "lastRevision", 2)
                if isinstance(lastRevision, int):
                    cl.globalRev = lastRevision
                    ll.info(f"new globalRev: {cl.globalRev}")
                    ll.debug(f"globalEvents: {events}")

            if individualEvents is not None:
                events = cl.checkAndGetValue(individualEvents, "events", 1)
                lastRevision = cl.checkAndGetValue(individualEvents, "lastRevision", 2)
                if isinstance(lastRevision, int):
                    cl.individualRev = lastRevision
                    ll.info(f"new individualRev: {cl.individualRev}")
                    ll.debug(f"individualEvents: {events}")
            ll.debug(f"operations: {ops}")
            return 1, ops
        elif fullSyncResponse is not None:
            # revision - 1 for sync revision on next req
            reasons = cl.checkAndGetValue(fullSyncResponse, "reasons", 1)
            syncRevision = cl.checkAndGetValue(fullSyncResponse, "nextRevision", 2)
            if not isinstance(syncRevision, int):
                raise ValueError
            ll.info(f"got fullSyncResponse: {reasons}")
            return 2, syncRevision - 1
        else:
            raise EOFError(f"[SyncHandler] sync failed, unknown response: {res}")
