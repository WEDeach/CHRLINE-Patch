# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, List, TypedDict

from .BaseService import BaseService, BaseServiceSender, BaseServiceStruct

if TYPE_CHECKING:
    from ..client import CHRLINE


class TSingleValueMetadata(TypedDict):
    type: int  # 8, 1


class TE2eeMetadata(TypedDict):
    e2eePublicKeyId: int  # 10, 1


class TLifetimePayloadMetadata(TypedDict):
    e2ee: TE2eeMetadata  # 12, 1
    singleValue: TSingleValueMetadata  # 12, 2


class TLifetimePayloadData(TypedDict):
    metadata: TLifetimePayloadMetadata  # 12, 1
    blobPayload: str  # 11, 2


class PasswordUpdateService(BaseService):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/EXT/auth/feature-user/api/primary/password/update"

    def __init__(self, client: "CHRLINE"):
        self.client = client
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def createSession(self):
        """Create update password session."""
        METHOD_NAME = "createSession"
        params = []
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getPasswordHashingParameter(self, sessionId: str):
        """Get password hashing parameter."""
        METHOD_NAME = "getPasswordHashingParameter"
        params = [[11, 1, sessionId]]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def setPassword(self, sessionId: str, hashedPassword: str):
        """Set password."""
        METHOD_NAME = "setPassword"
        params = [[11, 1, sessionId], [11, 2, hashedPassword]]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def updatePassword(
        self,
        sessionId: str,
        hashedPassword: str,
        nextBackupHeader: str,
        withNewMasterKey: bool,
        payloadDataList: List[TLifetimePayloadData],
    ):
        """Update password."""
        METHOD_NAME = "updatePassword"
        _payloadDataList = []
        for payloadData in payloadDataList:
            _e2ee = payloadData["metadata"]["e2ee"]
            _singleValue = payloadData["metadata"]["singleValue"]
            _metadata = [[12, 1, _e2ee], [12, 2, _singleValue]]
            _payloadDataList.append(
                [
                    [12, 1, _metadata],
                    [11, 2, payloadData["blobPayload"]],
                ]
            )
        params = [
            [11, 1, sessionId],
            [11, 2, hashedPassword],
            [11, 3, nextBackupHeader],
            [2, 4, withNewMasterKey],
            [15, 5, [12, _payloadDataList]],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
