# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING, Dict, List

from .BaseService import BaseService, BaseServiceSender, BaseServiceStruct

if TYPE_CHECKING:
    from ..client import CHRLINE


class MultiProfileService(BaseService):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/PFS4"

    def __init__(self, client: "CHRLINE"):
        self.client = client
        self.__sender = BaseServiceSender(
            client,
            "MultiProfileService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def deleteMultiProfile(
        self,
        profileId: str,
    ):
        """Delete multi profile."""
        METHOD_NAME = "deleteMultiProfile"
        params = [
            [11, 1, profileId],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def getMappedProfileIds(
        self,
        targetUserMids: List[str],
    ):
        """Get mapped profile ids."""
        METHOD_NAME = "getMappedProfileIds"
        params = [
            [15, 1, [11, targetUserMids]],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def mapProfileToUsers(
        self,
        profileId: str,
        targetUserMids: List[str],
    ):
        """Map profile to users."""
        METHOD_NAME = "mapProfileToUsers"
        params = [
            [11, 1, profileId],
            [15, 2, [11, targetUserMids]],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def updateProfileAttributesByProfileId(
        self,
        profileId: str,
        profileAttributes: Dict[str, str],
    ):
        """Update profile attributes."""
        METHOD_NAME = "updateProfileAttributes"
        params = [
            [8, 1, self.client.getCurrReqId()],
            [13, 2, [8, 12, profileAttributes]],
            [11, 3, profileId],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def createMultiProfile(
        self,
        displayName: str,
    ):
        """Create multi profile."""
        METHOD_NAME = "createMultiProfile"
        params = [
            [11, 1, displayName],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
