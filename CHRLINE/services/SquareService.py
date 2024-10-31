# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, Dict, List, Optional

from .BaseService import BaseService, BaseServiceStruct

if TYPE_CHECKING:
    from ..client import CHRLINE


class SquareService(BaseService):
    SquareService_REQ_TYPE = 4
    SquareService_RES_TYPE = 4
    SquareService_API_PATH = "/SQS1"

    SQUARE_EXCEPTION = {"code": 1, "message": 3, "metadata": 2}

    def __init__(self):
        self.SquareService_API_PATH = self.LINE_SQUARE_ENDPOINT

    def inviteIntoSquareChat(
        self,
        inviteeMids: list,
        squareChatMid: str,
    ):
        """Invite into square chat."""
        METHOD_NAME = "inviteIntoSquareChat"
        params = [
            [15, 1, [11, inviteeMids]],
            [11, 2, squareChatMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def inviteToSquare(
        self,
        squareMid: str,
        invitees: list,
        squareChatMid: str,
    ):
        """Invite to square."""
        METHOD_NAME = "inviteToSquare"
        params = [
            [11, 2, squareMid],
            [15, 3, [11, invitees]],
            [11, 4, squareChatMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getJoinedSquares(
        self,
        continuationToken: Optional[str] = None,
        limit: int = 50,
    ):
        """Get joined squares."""
        METHOD_NAME = "getJoinedSquares"
        params = [
            [11, 2, continuationToken],
            [8, 3, limit],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def markAsRead(
        self,
        squareChatMid: str,
        messageId: str,
        threadMid: Optional[str] = None,
    ):
        """Mark as read for square chat."""
        METHOD_NAME = "markAsRead"
        params = [
            [11, 2, squareChatMid],
            [11, 4, messageId],
        ]
        if threadMid is not None:
            params.append([11, 5, threadMid])
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def reactToMessage(
        self,
        squareChatMid: str,
        messageId: str,
        reactionType: int = 2,
        threadMid: Optional[str] = None,
    ):
        """
        React to message for square chat message.

        - reactionType:
            ALL     = 0,
            UNDO    = 1,
            NICE    = 2,
            LOVE    = 3,
            FUN     = 4,
            AMAZING = 5,
            SAD     = 6,
            OMG     = 7,
        """
        METHOD_NAME = "reactToMessage"
        params = [
            [8, 1, 0],  # reqSeq
            [11, 2, squareChatMid],
            [11, 3, messageId],
            [8, 4, reactionType],
        ]
        if threadMid is not None:
            params.append([11, 5, threadMid])
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def findSquareByInvitationTicket(
        self,
        invitationTicket: str,
    ):
        """Find square by invitation ticket."""
        METHOD_NAME = "findSquareByInvitationTicket"
        params = [[11, 2, invitationTicket]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def fetchMyEvents(
        self,
        subscriptionId: Optional[int] = 0,
        syncToken: Optional[str] = None,
        continuationToken: Optional[str] = None,
        limit: int = 100,
    ):
        """Fetch square events."""
        METHOD_NAME = "fetchMyEvents"
        params = [
            [10, 1, subscriptionId],
            [11, 2, syncToken],
            [8, 3, limit],
            [11, 4, continuationToken],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def fetchSquareChatEvents(
        self,
        squareChatMid: str,
        syncToken: Optional[str] = None,
        continuationToken: Optional[str] = None,
        subscriptionId: int = 0,
        limit: int = 100,
        threadMid: Optional[str] = None,
    ):
        """Fetch square chat events."""
        METHOD_NAME = "fetchSquareChatEvents"
        fetchType = 1  # DEFAULT(1),PREFETCH_BY_SERVER(2),
        # PREFETCH_BY_CLIENT(3);
        params = [
            [10, 1, subscriptionId],
            [11, 2, squareChatMid],
            [11, 3, syncToken],
            [8, 4, limit],
            [8, 5, 1],  # direction
            [8, 6, 1],  # inclusive
            [11, 7, continuationToken],
            [8, 8, fetchType],
            [11, 9, threadMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def sendSquareMessage(
        self,
        squareChatMid: str,
        text: str,
        contentType: int = 0,
        contentMetadata: dict = {},
        relatedMessageId: str = None,
    ):
        """Send message for square chat (OLD)."""
        METHOD_NAME = "sendMessage"
        message = [
            # [11, 1, _from],
            [11, 2, squareChatMid],
            [11, 10, text],
            [8, 15, contentType],  # contentType
            [13, 18, [11, 11, contentMetadata]],
        ]
        if relatedMessageId is not None:
            message.append([11, 21, relatedMessageId])
            message.append(
                [
                    8,
                    22,
                    3,
                ]
            )
            message.append([8, 24, 2])
        params = [
            [8, 1, self.getCurrReqId()],
            [11, 2, squareChatMid],
            [
                12,
                3,
                [
                    [12, 1, message],
                    [8, 3, 4],
                ],
            ],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def sendSquareTextMessage(
        self,
        squareChatMid: str,
        text: str,
        contentMetadata: dict = {},
        relatedMessageId: Optional[str] = None,
    ):
        return self.sendSquareMessage(
            squareChatMid, text, 0, contentMetadata, relatedMessageId
        )

    def getSquare(self, squareMid: str):
        """Get square."""
        METHOD_NAME = "getSquare"
        params = [
            [11, 2, squareMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getJoinableSquareChats(
        self, squareMid: str, continuationToken: Optional[str] = None, limit: int = 100
    ):
        """Get joinable square chats."""
        METHOD_NAME = "getJoinableSquareChats"
        params = [[11, 1, squareMid], [11, 10, continuationToken], [8, 11, limit]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def createSquare(
        self,
        name: str,
        displayName: str,
        profileImageObsHash: str = "0h6tJf0hQsaVt3H0eLAsAWDFheczgHd3wTCTx2eApNKSoefHNVGRdwfgxbdgUMLi8MSngnPFMeNmpbLi8MSngnPFMeNmpbLi8MSngnOA",
        desc: str = "test with CHRLINE API",
        searchable: bool = True,
        SquareJoinMethodType: int = 0,
    ):
        """
        Create square.

        - SquareJoinMethodType
            NONE(0),
            APPROVAL(1),
            CODE(2);
        """
        METHOD_NAME = "createSquare"
        params = [
            [8, 2, self.getCurrReqId()],
            [
                12,
                2,
                [
                    [11, 2, name],
                    [11, 4, profileImageObsHash],
                    [11, 5, desc],
                    [2, 6, searchable],
                    [8, 7, 1],  # type
                    [8, 8, 1],  # categoryId
                    [10, 10, 0],  # revision
                    [2, 11, True],  # ableToUseInvitationTicket
                    [12, 14, [[8, 1, SquareJoinMethodType]]],
                    [2, 15, False],  # adultOnly
                    [15, 16, [11, []]],  # svcTags
                ],
            ],
            [
                12,
                3,
                [
                    [11, 3, displayName],
                    # [11, 4, profileImageObsHash],
                    [2, 5, True],  # ableToReceiveMessage
                    [10, 9, 0],  # revision
                ],
            ],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareChatAnnouncements(self, squareMid: str):
        """Get square chat announcements."""
        METHOD_NAME = "getSquareChatAnnouncements"
        params = [
            [11, 2, squareMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def leaveSquareChat(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("leaveSquareChat is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "leaveSquareChat", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareChatMember(
        self,
        squareMemberMid: str,
        squareChatMid: str,
    ):
        """Get square chat member."""
        METHOD_NAME = "getSquareChatMember"
        params = [
            [11, 2, squareMemberMid],
            [11, 3, squareChatMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def searchSquares(
        self,
        query: str,
        continuationToken: str,
        limit: int,
    ):
        """Search squares."""
        METHOD_NAME = "searchSquares"
        params = [
            [11, 2, query],
            [11, 3, continuationToken],
            [8, 4, limit],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def updateSquareFeatureSet(
        self,
        updateAttributes: List[int],
        squareMid: str,
        revision: int,
        creatingSecretSquareChat: Optional[int] = None,
        invitingIntoOpenSquareChat: Optional[int] = None,
        creatingSquareChat: Optional[int] = None,
        readonlyDefaultChat: Optional[int] = None,
        showingAdvertisement: Optional[int] = None,
        delegateJoinToPlug: Optional[int] = None,
        delegateKickOutToPlug: Optional[int] = None,
        disableUpdateJoinMethod: Optional[int] = None,
        disableTransferAdmin: Optional[int] = None,
        creatingLiveTalk: Optional[int] = None,
        disableUpdateSearchable: Optional[int] = None,
        summarizingMessages: Optional[int] = None,
        creatingSquareThread: Optional[int] = None,
        enableSquareThread: Optional[int] = None,
    ):
        """
        Update square feature set.

        - updateAttributes:
            CREATING_SECRET_SQUARE_CHAT(1),
            INVITING_INTO_OPEN_SQUARE_CHAT(2),
            CREATING_SQUARE_CHAT(3),
            READONLY_DEFAULT_CHAT(4),
            SHOWING_ADVERTISEMENT(5),
            DELEGATE_JOIN_TO_PLUG(6),
            DELEGATE_KICK_OUT_TO_PLUG(7),
            DISABLE_UPDATE_JOIN_METHOD(8),
            DISABLE_TRANSFER_ADMIN(9),
            CREATING_LIVE_TALK(10),
            DISABLE_UPDATE_SEARCHABLE(11),
            SUMMARIZING_MESSAGES(12),
            CREATING_SQUARE_THREAD(13),
            ENABLE_SQUARE_THREAD(14);
        """
        METHOD_NAME = "updateSquareFeatureSet"
        SquareFeatureSet = [
            [11, 1, squareMid],
            [10, 2, revision],
        ]
        features = {
            11: creatingSecretSquareChat,
            12: invitingIntoOpenSquareChat,
            13: creatingSquareChat,
            14: readonlyDefaultChat,
            15: showingAdvertisement,
            16: delegateJoinToPlug,
            17: delegateKickOutToPlug,
            18: disableUpdateJoinMethod,
            19: disableTransferAdmin,
            20: creatingLiveTalk,
            21: disableUpdateSearchable,
            22: summarizingMessages,
            23: creatingSquareThread,
            24: enableSquareThread,
        }
        for fid, fbt in features.items():
            if fbt is not None:
                squareFeature = [
                    [8, 1, 1],
                    [8, 2, fbt],
                ]
                SquareFeatureSet.append([12, fid, squareFeature])
        params = [
            [14, 2, [8, updateAttributes]],
            [12, 3, SquareFeatureSet],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def joinSquare(
        self,
        squareMid,
        displayName,
        ableToReceiveMessage: bool = False,
        passCode: Optional[str] = None,
        squareChatMid: Optional[str] = None,
        claimAdult: Optional[int] = None,
    ):
        METHOD_NAME = "joinSquare"
        member = [
            [11, 2, squareMid],
            [11, 3, displayName],
            [2, 5, ableToReceiveMessage],
        ]
        params = [
            [11, 2, squareMid],
            [12, 3, member],
        ]
        if squareChatMid is not None:
            params.append([11, 4, squareChatMid])
        if passCode is not None:
            codeValue = [
                [11, 1, passCode],
            ]
            squareJoinMethodValue = [
                [12, 2, codeValue],
            ]
            params.append([12, 5, squareJoinMethodValue])
        if claimAdult is not None:
            params.append([8, 6, claimAdult])
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquarePopularKeywords(self):
        """
        Get popular keywords.
        """
        METHOD_NAME = "getPopularKeywords"
        params = []
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def reportSquareMessage(
        self,
        squareMid: str,
        squareChatMid: str,
        squareMessageId: str,
        reportType: int,
        otherReason: Optional[str] = None,
        threadMid: Optional[str] = None,
    ):
        """Report square message."""
        METHOD_NAME = "reportSquareMessage"
        params = [
            [11, 2, squareMid],
            [11, 3, squareChatMid],
            [11, 4, squareMessageId],
            [8, 5, reportType],
        ]
        if otherReason is not None:
            params.append([11, 6, otherReason])
        if threadMid is not None:
            params.append([11, 7, threadMid])
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def updateSquareMemberRelation(
        self,
        squareMid: str,
        targetSquareMemberMid: str,
        updatedAttrs: List[int],
        state: int,
        revision: int,
    ):
        """Update square member relation."""
        METHOD_NAME = "updateSquareMemberRelation"
        relation = [
            [8, 1, state],
            [10, 2, revision],
        ]
        params = [
            [11, 2, squareMid],
            [11, 3, targetSquareMemberMid],
            [14, 4, [8, updatedAttrs]],
            [12, 5, relation],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def leaveSquare(self, squareMid: str):
        """
        Leave square.
        """
        METHOD_NAME = "leaveSquare"
        params = [
            [11, 2, squareMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareMemberRelations(
        self, state: int, continuationToken: Optional[str] = None, limit: int = 20
    ):
        """
        Get square member relations.
        """
        METHOD_NAME = "getSquareMemberRelations"
        params = [[8, 2, state], [11, 3, continuationToken], [8, 4, limit]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def removeSquareSubscriptions(self, subscriptionIds: list = []):
        params = [
            [
                12,
                1,
                [
                    [15, 2, [10, subscriptionIds]],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol("removeSubscriptions", params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareMembers(self, mids: List[str]):
        """Get square members."""
        METHOD_NAME = "getSquareMembers"
        params = [
            [14, 2, [11, mids]],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def updateSquareChat(
        self,
        updatedAttrs: List[int],
        squareChatMid: str,
        squareMid: str,
        _type: int,
        name: str,
        chatImageObsHash: str,
        squareChatRevision: int,
        maxMemberCount: int,
        showJoinMessage: bool,
        showLeaveMessage: bool,
        showKickoutMessage: bool,
        state: int,
        invitationUrl: Optional[str] = None,
        ableToSearchMessage: Optional[int] = None,
    ):
        """Update square chat."""
        METHOD_NAME = "updateSquareChat"
        messageVisibility = [
            [2, 1, showJoinMessage],
            [2, 2, showLeaveMessage],
            [2, 3, showKickoutMessage],
        ]
        squareChat = [
            [11, 1, squareChatMid],
            [11, 2, squareMid],
            [8, 3, _type],
            [11, 4, name],
            [11, 5, chatImageObsHash],
            [10, 6, squareChatRevision],
            [8, 7, maxMemberCount],
            [8, 8, state],
        ]
        if invitationUrl is not None:
            squareChat.append([11, 9, invitationUrl])
        if messageVisibility is not None:
            squareChat.append([12, 10, messageVisibility])
        if ableToSearchMessage is not None:
            squareChat.append([8, 11, ableToSearchMessage])
        params = [
            [14, 2, [8, updatedAttrs]],
            [12, 3, squareChat],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareMessageReactions(
        self,
        squareChatMid: str,
        messageId: str,
        _type: int,
        continuationToken: str,
        limit: int,
        threadMid: Optional[str],
    ):
        """
        Get square message reactions.
        """
        METHOD_NAME = "getSquareMessageReactions"
        params = [
            [11, 1, squareChatMid],
            [11, 2, messageId],
            [8, 3, _type],
            [11, 4, continuationToken],
            [8, 5, limit],
            [11, 6, threadMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def destroySquareMessage(
        self, squareChatMid: str, messageId: str, threadMid: Optional[str]
    ):
        """
        Destroy message for square.
        """
        METHOD_NAME = "destroyMessage"
        params = [[11, 2, squareChatMid], [11, 4, messageId], [11, 5, threadMid]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def reportSquareChat(
        self,
        squareMid: str,
        squareChatMid: str,
        reportType: int,
        otherReason: Optional[str] = None,
    ):
        """Report square chat."""
        METHOD_NAME = "reportSquareChat"
        params = [
            [11, 2, squareMid],
            [11, 3, squareChatMid],
            [8, 5, reportType],
        ]
        if otherReason is not None:
            params.append([11, 6, otherReason])
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def unsendSquareMessage(self, squareChatMid: str, messageId: str):
        """
        Unsend message for square.

        2022/09/19: Added.
        """
        METHOD_NAME = "unsendMessage"
        params = SquareServiceStruct.UnsendMessageRequest(squareChatMid, messageId)
        sqrd = self.generateDummyProtocol(
            METHOD_NAME, params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
            readWith=f"{__class__.__name__}.{METHOD_NAME}",
        )

    def deleteSquareChatAnnouncement(self, squareChatMid: str, announcementSeq: int):
        """
        Delete square chat announcement.
        """
        METHOD_NAME = "deleteSquareChatAnnouncement"
        params = [[11, 2, squareChatMid], [10, 3, announcementSeq]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def createSquareChat(
        self,
        squareChatMid: str,
        name: str,
        chatImageObsHash: str,
        squareChatType: int = 1,
        maxMemberCount: int = 5000,
        ableToSearchMessage: int = 1,
        squareMemberMids: list = [],
    ):
        """
        - SquareChatType:
            OPEN(1),
            SECRET(2),
            ONE_ON_ONE(3),
            SQUARE_DEFAULT(4);
        - ableToSearchMessage:
            NONE(0),
            OFF(1),
            ON(2);
        """
        params = [
            [
                12,
                1,
                [
                    [8, 1, self.getCurrReqId()],
                    [
                        12,
                        2,
                        [
                            [11, 1, squareChatMid],
                            [8, 3, squareChatType],
                            [11, 4, name],
                            [11, 5, chatImageObsHash],
                            [8, 7, maxMemberCount],
                            [8, 11, ableToSearchMessage],
                        ],
                    ],
                    [15, 3, [11, squareMemberMids]],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol(
            "createSquareChat", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def deleteSquareChat(
        self,
        squareChatMid: str,
        revision: int,
    ):
        """
        Delete square chat.
        """
        METHOD_NAME = "deleteSquareChat"
        params = [[11, 2, squareChatMid], [10, 3, revision]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareChatMembers(
        self,
        squareChatMid: str,
        continuationToken: Optional[str] = None,
        limit: int = 200,
    ):
        METHOD_NAME = "getSquareChatMembers"
        GetSquareChatMembersRequest = [[11, 1, squareChatMid], [8, 3, limit]]
        if continuationToken is not None:
            GetSquareChatMembersRequest.append([11, 2, continuationToken])
        params = [[12, 1, GetSquareChatMembersRequest]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareFeatureSet(
        self,
        squareMid: str,
    ):
        """Get square feature set."""
        METHOD_NAME = "getSquareFeatureSet"
        params = [
            [11, 2, squareMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def updateSquareAuthority(
        self,
        updateAttributes: List[int],
        squareMid: str,
        updateSquareProfile: int,
        inviteNewMember: int,
        approveJoinRequest: int,
        createPost: int,
        createOpenSquareChat: int,
        deleteSquareChatOrPost: int,
        removeSquareMember: int,
        grantRole: int,
        enableInvitationTicket: int,
        revision: int,
        createSquareChatAnnouncement: int,
        updateMaxChatMemberCount: Optional[int] = None,
        useReadonlyDefaultChat: Optional[int] = None,
    ):
        """Update square authority."""
        METHOD_NAME = "updateSquareAuthority"
        authority = [
            [11, 1, squareMid],
            [8, 2, updateSquareProfile],
            [8, 3, inviteNewMember],
            [8, 4, approveJoinRequest],
            [8, 5, createPost],
            [8, 6, createOpenSquareChat],
            [8, 7, deleteSquareChatOrPost],
            [8, 8, removeSquareMember],
            [8, 9, grantRole],
            [8, 10, enableInvitationTicket],
            [10, 11, revision],
            [8, 12, createSquareChatAnnouncement],
        ]
        if updateMaxChatMemberCount is not None:
            authority.append([8, 13, updateMaxChatMemberCount])
        if useReadonlyDefaultChat is not None:
            authority.append([8, 14, useReadonlyDefaultChat])
        params = [
            [14, 2, [8, updateAttributes]],
            [12, 3, authority],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def rejectSquareMembers(
        self,
        squareMid: str,
        requestedMemberMids: List[str],
    ):
        """Reject square members."""
        METHOD_NAME = "rejectSquareMembers"
        params = [[11, 2, squareMid], [15, 3, [11, requestedMemberMids]]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def deleteSquare(
        self,
        mid: str,
        revision: int,
    ):
        """
        Delete square.
        """
        METHOD_NAME = "deleteSquare"
        params = [[11, 2, mid], [10, 3, revision]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def reportSquare(
        self,
        squareMid: str,
        reportType: int,
        otherReason: Optional[str],
    ):
        """Report square."""
        METHOD_NAME = "reportSquare"
        params = [
            [11, 2, squareMid],
            [8, 3, reportType],
        ]
        if otherReason is not None:
            params.append([11, 4, otherReason])
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareInvitationTicketUrl(
        self,
        mid: str,
    ):
        """Get square invitation ticket url"""
        METHOD_NAME = "getInvitationTicketUrl"
        params = [
            [11, 2, mid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def updateSquareChatMember(
        self,
        squareMemberMid: str,
        squareChatMid: str,
        notificationForMessage: bool = True,
        notificationForNewMember: bool = True,
        updatedAttrs: List[int] = [6],
    ):
        """
        Update square chat member.

        - SquareChatMemberAttribute:
            MEMBERSHIP_STATE(4),
            NOTIFICATION_MESSAGE(6),
            NOTIFICATION_NEW_MEMBER(7);
        """
        METHOD_NAME = "updateSquareChatMember"
        chatMember = [
            [11, 1, squareMemberMid],
            [11, 2, squareChatMid],
            [2, 5, notificationForMessage],
            [2, 6, notificationForNewMember],
        ]
        params = [
            [14, 2, [8, updatedAttrs]],
            [12, 3, chatMember],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def updateSquareMember(
        self,
        updatedAttrs: list,
        updatedPreferenceAttrs: list,
        squareMemberMid: str,
        squareMid: str,
        revision: int,
        displayName: str = None,
        membershipState: int = None,
        role: int = None,
    ):
        """
        Update square member.

        SquareMemberAttribute:
            DISPLAY_NAME(1),
            PROFILE_IMAGE(2),
            ABLE_TO_RECEIVE_MESSAGE(3),
            MEMBERSHIP_STATE(5),
            ROLE(6),
            PREFERENCE(7);
        SquareMembershipState:
            JOIN_REQUESTED(1),
            JOINED(2),
            REJECTED(3),
            LEFT(4),
            KICK_OUT(5),
            BANNED(6),
            DELETED(7);
        """
        METHOD_NAME = "updateSquareMember"
        squareMember = [[11, 1, squareMemberMid], [11, 2, squareMid]]
        if 1 in updatedAttrs:
            if displayName is None:
                raise ValueError("displayName is None")
            squareMember.append([11, 3, displayName])
        if 5 in updatedAttrs:
            if membershipState is None:
                raise ValueError("membershipState is None")
            squareMember.append([8, 7, membershipState])
        if 6 in updatedAttrs:
            if role is None:
                raise ValueError("role is None")
            squareMember.append([8, 8, role])
        squareMember.append([10, 9, revision])
        params = [
            [14, 2, [8, updatedAttrs]],
            [14, 3, [8, updatedPreferenceAttrs]],
            [12, 4, squareMember],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    # https://discord.com/channels/466066749440393216/1076212330620256296
    def deleteOtherFromSquare(self, sid: str, pid: str):
        """Kick out member for square."""
        UPDATE_PREF_ATTRS = []
        UPDATE_ATTRS = [5]
        MEMBERSHIP_STATE = 5
        getSquareMemberResp = self.getSquareMember(pid)
        squareMember = self.checkAndGetValue(getSquareMemberResp, "squareMember", 1)
        squareMemberRevision = self.checkAndGetValue(squareMember, "revision", 9)
        revision = squareMemberRevision
        self.updateSquareMember(
            UPDATE_ATTRS,
            UPDATE_PREF_ATTRS,
            pid,
            sid,
            revision,
            membershipState=MEMBERSHIP_STATE,
        )

    def updateSquare(
        self,
        updatedAttrs: List[int],
        mid: str,
        name: str,
        welcomeMessage: str,
        profileImageObsHash: str,
        desc: str,
        searchable: bool,
        _type: int,
        categoryId: int,
        invitationURL: str,
        revision: int,
        ableToUseInvitationTicket: bool,
        state: int,
        joinMethodType: int,
        emblems: Optional[List[int]] = None,
        joinMethodMessage: Optional[str] = None,
        joinMethodCode: Optional[str] = None,
        adultOnly: Optional[int] = None,
        svcTags: Optional[List[str]] = None,
        createdAt: Optional[int] = None,
    ):
        """Update square."""
        METHOD_NAME = "updateSquare"
        approvalValue = [
            [11, 1, joinMethodMessage],
        ]
        codeValue = [
            [11, 1, joinMethodCode],
        ]
        joinMethodValue = [
            [12, 1, approvalValue],
            [12, 2, codeValue],
        ]
        joinMethod = [
            [8, 1, joinMethodType],
            [12, 2, joinMethodValue],
        ]
        square = [
            [11, 1, mid],
            [11, 2, name],
            [11, 3, welcomeMessage],
            [11, 4, profileImageObsHash],
            [11, 5, desc],
            [2, 6, searchable],
            [8, 7, _type],
            [8, 8, categoryId],
            [11, 9, invitationURL],
            [10, 10, revision],
            [2, 11, ableToUseInvitationTicket],
            [8, 12, state],
            [12, 14, joinMethod],
        ]
        if emblems is not None:
            square.append([15, 13, [8, emblems]])
        if adultOnly is not None:
            square.append([8, 15, adultOnly])
        if svcTags is not None:
            square.append([15, 16, [11, svcTags]])
        if createdAt is not None:
            square.append([10, 17, createdAt])
        params = [
            [14, 2, [11, updatedAttrs]],
            [12, 3, square],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareAuthorities(self, squareMids: List[str]):
        """
        Get square authorities.
        """
        METHOD_NAME = "getSquareAuthorities"
        params = [[14, 2, [11, squareMids]]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def updateSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateSquareMembers", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareChatStatus(self, squareChatMid: str):
        """
        Get square chat status.
        """
        METHOD_NAME = "getSquareChatStatus"
        params = [[11, 2, squareChatMid]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def approveSquareMembers(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("approveSquareMembers is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "approveSquareMembers", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareStatus(self, squareMid: str):
        """Get square status."""
        METHOD_NAME = "getSquareStatus"
        params = [
            [11, 2, squareMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def searchSquareMembers(
        self,
        squareMid: str,
        membershipState: int,
        includingMe: bool,
        excludeBlockedMembers: bool,
        continuationToken: str,
        limit: int = 20,
        memberRoles: Optional[List[int]] = None,
        displayName: Optional[str] = None,
        ableToReceiveMessage: Optional[int] = None,
        ableToReceiveFriendRequest: Optional[int] = None,
        chatMidToExcludeMembers: Optional[str] = None,
        includingMeOnlyMatch: Optional[bool] = None,
    ):
        """Search square members."""
        METHOD_NAME = "searchSquareMembers"
        searchOption = [
            [8, 1, membershipState],
            [2, 7, includingMe],
            [2, 8, excludeBlockedMembers],
        ]
        if memberRoles is not None:
            searchOption.append([14, 2, [8, memberRoles]])
        if ableToReceiveMessage is not None:
            searchOption.append([11, 3, displayName])
        if ableToReceiveMessage is not None:
            searchOption.append([8, 4, ableToReceiveMessage])
        if ableToReceiveFriendRequest is not None:
            searchOption.append([8, 5, ableToReceiveFriendRequest])
        if chatMidToExcludeMembers is not None:
            searchOption.append([11, 6, chatMidToExcludeMembers])
        if includingMeOnlyMatch is not None:
            searchOption.append([2, 9, includingMeOnlyMatch])
        params = [
            [11, 2, squareMid],
            [12, 3, searchOption],
            [11, 4, continuationToken],
            [8, 5, limit],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def checkSquareJoinCode(self, squareMid: str, code: str):
        params = [
            [
                12,
                1,
                [
                    [11, 2, squareMid],
                    [11, 3, code],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol("checkJoinCode", params, 4)
        return self.postPackDataAndGetUnpackRespData(
            self.LINE_SQUARE_ENDPOINT,
            sqrd,
            4,
            encType=0,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def createSquareChatAnnouncement(
        self,
        squareChatMid: str,
        messageId: str,
        text: str,
        senderSquareMemberMid: str,
        createdAt: int,
        announcementType: int = 0,
    ):
        """
        - SquareChatAnnouncementType:
            TEXT_MESSAGE(0);
        """
        params = [
            [
                12,
                1,
                [
                    [8, 1, self.getCurrReqId()],
                    [11, 2, squareChatMid],
                    [
                        12,
                        3,
                        [
                            [8, 2, announcementType],
                            [
                                12,
                                3,
                                [
                                    [
                                        12,
                                        1,
                                        [
                                            [11, 1, messageId],
                                            [11, 2, text],
                                            [11, 3, senderSquareMemberMid],
                                            [10, 4, createdAt],
                                        ],
                                    ]
                                ],
                            ],
                        ],
                    ],
                ],
            ]
        ]
        sqrd = self.generateDummyProtocol(
            "createSquareChatAnnouncement", params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH,
            sqrd,
            self.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
        )

    def getSquareAuthority(
        self,
        squareMid: str,
    ):
        """
        Get square authority.
        """
        METHOD_NAME = "getSquareAuthority"
        params = [[11, 1, squareMid]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareChat(
        self,
        squareChatMid: str,
    ):
        """
        Get square chat.
        """
        METHOD_NAME = "getSquareChat"
        params = [[11, 1, squareChatMid]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def refreshSquareSubscriptions(
        self,
        subscriptions: List[int],
    ):
        """Refresh subscriptions."""
        METHOD_NAME = "refreshSubscriptions"
        params = [
            [15, 2, [10, subscriptions]],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getJoinedSquareChats(
        self,
        continuationToken: str,
        limit: int,
    ):
        """
        Get joined square chats.
        """
        METHOD_NAME = "getJoinedSquareChats"
        params = [[11, 2, continuationToken], [8, 3, limit]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def joinSquareChat(
        self,
        squareChatMid: str,
    ):
        """Join square chat."""
        METHOD_NAME = "joinSquareChat"
        params = [
            [11, 1, squareChatMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def findSquareByEmid(
        self,
        emid: str,
    ):
        """
        Find square by emid.
        """
        METHOD_NAME = "findSquareByEmid"
        params = [
            [11, 1, emid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareMemberRelation(
        self,
        squareMid: str,
        targetSquareMemberMid: str,
    ):
        """
        Get square member relation.
        """
        METHOD_NAME = "getSquareMemberRelation"
        params = [
            [11, 2, squareMid],
            [11, 3, targetSquareMemberMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareMember(
        self,
        squareMemberMid: str,
    ):
        """Get square member."""
        METHOD_NAME = "getSquareMember"
        params = [
            [11, 2, squareMemberMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def destroySquareMessages(
        self,
        squareChatMid: str,
        messageIds: list,
        threadMid: Optional[str] = None,
    ):
        """
        Destroy messages for Square.
        """
        METHOD_NAME = "destroyMessages"
        params = [
            [11, 2, squareChatMid],
            [14, 4, [11, messageIds]],
            [11, 5, threadMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareCategories(self):
        """
        Get categories
        """
        METHOD_NAME = "getCategories"
        params = []
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def reportSquareMember(
        self,
        squareMemberMid: str,
        reportType: int,
        otherReason: str,
        squareChatMid: str,
        threadMid: str,
    ):
        """Report square member"""
        METHOD_NAME = "reportSquareMember"
        params = [
            [11, 2, squareMemberMid],
            [8, 3, reportType],
        ]
        if otherReason is not None:
            params.append([11, 4, otherReason])
        if squareChatMid is not None:
            params.append([11, 5, squareChatMid])
        if threadMid is not None:
            params.append([11, 6, threadMid])
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareNoteStatus(
        self,
        squareMid: str,
    ):
        """
        Get note status.
        """
        METHOD_NAME = "getNoteStatus"
        params = [
            [11, 2, squareMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def searchSquareChatMembers(
        self,
        squareChatMid: str,
        displayName: str,
        continuationToken: Optional[str] = None,
        limit: int = 20,
        includingMe: bool = True,
    ):
        METHOD_NAME = "searchSquareChatMembers"
        searchOption = [[11, 1, displayName], [2, 2, includingMe]]
        params = [
            [11, 1, squareChatMid],
            [12, 2, searchOption],
            [8, 4, limit],
        ]
        if continuationToken is not None:
            params.append([11, 3, continuationToken])
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareChatFeatureSet(
        self,
        squareChatMid: str,
    ):
        """Get square chat feature set."""
        METHOD_NAME = "getSquareChatFeatureSet"
        params = [
            [11, 2, squareChatMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareEmid(
        self,
        squareMid: str,
    ):
        """
        Get square eMid.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.5.py
        DATETIME: 02/03/2023, 23:02:07
        """
        METHOD_NAME = "getSquareEmid"
        params = [[11, 1, squareMid]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareMembersBySquare(
        self,
        squareMid: str,
        squareMemberMids: List[str],
    ):
        """
        Get square members by square.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.5.py
        DATETIME: 02/03/2023, 23:02:07
        """
        METHOD_NAME = "getSquareMembersBySquare"
        params = [
            [11, 2, squareMid],
            [14, 3, [11, squareMemberMids]],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def manualRepair(
        self,
        syncToken: str,
        limit: int,
        continuationToken: Optional[str] = None,
    ):
        """
        Manual repair.

        Example:
            `cl.manualRepair(limit=200)`

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.5.py
        DATETIME: 02/03/2023, 23:02:07
        """
        METHOD_NAME = "manualRepair"
        params = [
            [11, 1, syncToken],
            [8, 2, limit],
            [11, 3, continuationToken],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getJoinedSquareChatThreads(
        self,
        squareChatMid: str,
        limit: int = 20,
        continuationToken: str = None,
    ):
        """
        Get joined square chat threads.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 04/24/2023, 18:07:51
        """
        METHOD_NAME = "getJoinedSquareChatThreads"
        params = [
            [11, 1, squareChatMid],
            [8, 2, limit],
            [11, 3, continuationToken],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def createSquareChatThread(
        self,
        squareChatMid: str,
        squareMid: str,
        messageId: str,
    ):
        """
        Create square chat thread.

        Usages:
            `cl.createSquareChatThread(SQ_CHAT_MID, SQ_MID, MSG_ID)`

        Example:
            `cl.createSquareChatThread("mxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "sxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "123456")`

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 04/24/2023, 18:07:51
        """
        METHOD_NAME = "createSquareThread"
        squareChatThread = [
            [11, 2, squareChatMid],
            [11, 3, squareMid],
            [11, 4, messageId],
        ]
        params = [
            [8, 1, self.getCurrReqId("sq")],
            [12, 2, squareChatThread],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareChatThread(
        self,
        squareChatMid: str,
        squareChatThreadMid: str,
    ):
        """
        Get square chat thread.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 04/24/2023, 18:07:51
        """
        METHOD_NAME = "getSquareChatThread"
        params = [
            [11, 1, squareChatMid],
            [11, 2, squareChatThreadMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def joinSquareChatThread(
        self,
        squareChatMid: str,
        squareChatThreadMid: str,
    ):
        """
        Join square chat thread.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 04/24/2023, 18:07:51
        """
        METHOD_NAME = "joinSquareChatThread"
        params = [
            [11, 1, squareChatMid],
            [11, 2, squareChatThreadMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def syncSquareMembers(
        self,
        squareMid: str,
        squareMembers: Dict[str, int],
    ):
        """
        Sync square members.

        Usages:
            `cl.syncSquareMembers(SQ_MID, {MBER_MID: REV})`

        Example:
            `cl.syncSquareMembers("sxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", {'pxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx': 0})`

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 04/24/2023, 18:07:51
        """
        METHOD_NAME = "syncSquareMembers"
        params = [
            [11, 1, squareMid],
            [13, 2, [11, 10, squareMembers]],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def hideSquareMemberContents(
        self,
        squareMemberMid: str,
    ):
        """
        Hide square member contents.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "hideSquareMemberContents"
        params = [
            [11, 1, squareMemberMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def markChatsAsRead(
        self,
        chatMids: List[str],
    ):
        """
        Mark chats as read.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "markChatsAsRead"
        params = [
            [14, 2, [11, chatMids]],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def reportMessageSummary(
        self,
        chatEmid: str,
        messageSummaryRangeTo: int,
        reportType: int,
    ):
        """
        Report message summary.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "reportMessageSummary"
        params = [
            [11, 1, chatEmid],
            [10, 2, messageSummaryRangeTo],
            [8, 3, reportType],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getGoogleAdOptions(
        self,
        squareMid: str,
        chatMid: str,
        adScreen: int,
    ):
        """
        Get google ad options.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "getGoogleAdOptions"
        params = [
            [11, 1, squareMid],
            [11, 2, chatMid],
            [8, 3, adScreen],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def unhideSquareMemberContents(
        self,
        squareMemberMid: str,
    ):
        """
        Unhide square member contents.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "unhideSquareMemberContents"
        params = [
            [11, 1, squareMemberMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareChatEmid(
        self,
        squareChatMid: str,
    ):
        """
        Get square chat emid.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "getSquareChatEmid"
        params = [
            [11, 1, squareChatMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareThread(
        self,
        threadMid: str,
        includeRootMessage: bool = True,
    ):
        """
        Get square thread.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "getSquareThread"
        params = [
            [11, 1, threadMid],
            [2, 2, includeRootMessage],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getSquareThreadMid(
        self,
        chatMid: str,
        messageId: str,
    ):
        """
        Get square thread mid.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "getSquareThreadMid"
        params = [
            [11, 1, chatMid],
            [11, 2, messageId],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def getUserSettings(
        self,
        requestedAttrs: list = [1],
    ):
        """
        Get user settings.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "getUserSettings"
        params = [
            [14, 1, [8, requestedAttrs]],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def markThreadsAsRead(
        self,
        chatMid: str,
    ):
        """
        Mark threads as read.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "markThreadsAsRead"
        params = [
            [11, 1, chatMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def sendSquareThreadMessage(
        self,
        chatMid: str,
        threadMid: str,
        text: str,
    ):
        """
        Send square thread message.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "sendSquareThreadMessage"
        message = [
            [11, 2, threadMid],
            [11, 10, text],
            [8, 15, 0],
        ]
        threadMessage = [
            [12, 1, message],
            [8, 3, 5],
        ]
        params = [
            [8, 1, self.getCurrReqId("sq")],
            [11, 2, chatMid],
            [11, 3, threadMid],
            [12, 4, threadMessage],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def findSquareByInvitationTicketV2(
        self,
        invitationTicket: str,
    ):
        """
        Find square by invitation ticket v2.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "findSquareByInvitationTicketV2"
        params = [[11, 1, invitationTicket]]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def leaveSquareThread(
        self,
        chatMid: str,
        threadMid: str,
    ):
        """
        Remove the thread from my favorites.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "leaveSquareThread"
        params = [
            [11, 1, chatMid],
            [11, 2, threadMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def joinSquareThread(
        self,
        chatMid: str,
        threadMid: str,
    ):
        """
        Add the thread to my favorites.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "joinSquareThread"
        params = [
            [11, 1, chatMid],
            [11, 2, threadMid],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def updateUserSettings(
        self,
        updatedAttrs: List[int],
        liveTalkNotification: Optional[bool] = None,
    ):
        """
        Update user settings.

        ---
        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 05/29/2024, 19:02:42
        """
        METHOD_NAME = "updateUserSettings"
        userSettings = []
        if liveTalkNotification is not None:
            userSettings.append([8, 1, liveTalkNotification])
        params = [
            [14, 1, [8, updatedAttrs]],
            [12, 2, userSettings],
        ]
        return SquareServiceStruct.SendRequestByName(self, METHOD_NAME, params)

    def searchMentionables(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.6.py
        DATETIME: 10/31/2024, 14:52:45
        """
        raise Exception("searchMentionables is not implemented")
        METHOD_NAME = "searchMentionables"
        params = []
        sqrd = self.generateDummyProtocol(
            METHOD_NAME, params, self.SquareService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.SquareService_API_PATH, sqrd, self.SquareService_RES_TYPE
        )


class SquareServiceStruct(BaseServiceStruct):
    @staticmethod
    def UnsendMessageRequest(squareChatMid: str, messageId: str):
        return __class__.BaseRequest([[11, 2, squareChatMid], [11, 3, messageId]])

    @staticmethod
    def SendRequestByName(client: "CHRLINE", name: str, request: list):
        payload = __class__.BaseRequest(request)
        sqrd = client.generateDummyProtocol(
            name, payload, client.SquareService_REQ_TYPE
        )
        return client.postPackDataAndGetUnpackRespData(
            client.SquareService_API_PATH,
            sqrd,
            client.SquareService_RES_TYPE,
            baseException=SquareService.SQUARE_EXCEPTION,
            readWith=f"SquareService.{name}",
        )
