# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class ChannelService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/CH4"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def issueChannelToken(self, channelId="1341209950"):
        METHOD_NAME = "issueChannelToken"
        params = [[11, 1, channelId]]
        return self.__sender.send(METHOD_NAME, params)

    def approveChannelAndIssueChannelToken(self, channelId="1341209950"):
        METHOD_NAME = "approveChannelAndIssueChannelToken"
        params = [[11, 1, channelId]]
        return self.__sender.send(METHOD_NAME, params)

    def getChannelInfo(self, channelId):
        METHOD_NAME = "getChannelInfo"
        params = [[11, 2, channelId]]
        return self.__sender.send(METHOD_NAME, params)

    def getCommonDomains(self, lastSynced: int = 0):
        METHOD_NAME = "getCommonDomains"
        params = [[10, 1, lastSynced]]
        return self.__sender.send(METHOD_NAME, params)

    def issueRequestTokenWithAuthScheme(self, channelId, otpId, authScheme, returnUrl):
        METHOD_NAME = "issueRequestTokenWithAuthScheme"
        params = [
            [11, 1, channelId],
            [11, 2, otpId],
            [15, 3, [11, authScheme]],
            [11, 4, returnUrl],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getReturnUrlWithRequestTokenForAutoLogin(self, url, sessionString=None):
        METHOD_NAME = "getReturnUrlWithRequestTokenForAutoLogin"
        params = [[12, 2, [[11, 1, url], [11, 2, sessionString]]]]
        return self.__sender.send(METHOD_NAME, params)

    def getWebLoginDisallowedUrl(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getWebLoginDisallowedUrl is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getWebLoginDisallowedUrl", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def updateChannelNotificationSetting(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateChannelNotificationSetting is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateChannelNotificationSetting", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def updateChannelSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("updateChannelSettings is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "updateChannelSettings", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def syncChannelData(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("syncChannelData is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "syncChannelData", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def getUpdatedChannelIds(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getUpdatedChannelIds is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getUpdatedChannelIds", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def getChannels(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getChannels is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getChannels", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def getDomains(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getDomains is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("getDomains", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def revokeAccessToken(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("revokeAccessToken is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "revokeAccessToken", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def approveChannelAndIssueRequestToken(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("approveChannelAndIssueRequestToken is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "approveChannelAndIssueRequestToken", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def getChannelNotificationSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getChannelNotificationSettings is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getChannelNotificationSettings", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def reserveCoinUse(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("reserveCoinUse is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "reserveCoinUse", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def getApprovedChannels(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getApprovedChannels is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getApprovedChannels", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def issueRequestToken(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("issueRequestToken is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "issueRequestToken", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def issueRequestTokenForAutoLogin(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("issueRequestTokenForAutoLogin is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "issueRequestTokenForAutoLogin", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def getNotificationBadgeCount(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getNotificationBadgeCount is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getNotificationBadgeCount", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def revokeChannel(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("revokeChannel is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "revokeChannel", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def getChannelSettings(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getChannelSettings is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getChannelSettings", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def issueOTP(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("issueOTP is not implemented")
        params = []
        sqrd = self.generateDummyProtocol("issueOTP", params, ChannelService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def fetchNotificationItems(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("fetchNotificationItems is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "fetchNotificationItems", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def getFriendChannelMatrices(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getFriendChannelMatrices is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getFriendChannelMatrices", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def getChannelNotificationSetting(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getChannelNotificationSetting is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getChannelNotificationSetting", params, ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            ChannelService_API_PATH, sqrd, ChannelService_RES_TYPE
        )

    def issueChannelAppView(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:35:49
        """
        raise Exception("issueChannelAppView is not implemented")
        METHOD_NAME = "issueChannelAppView"
        params = []
        sqrd = self.generateDummyProtocol(
            METHOD_NAME, params, self.ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.ChannelService_API_PATH, sqrd, self.ChannelService_RES_TYPE
        )

    def getWebLoginDisallowedURL(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 03/27/2022, 05:35:49
        """
        raise Exception("getWebLoginDisallowedURL is not implemented")
        METHOD_NAME = "getWebLoginDisallowedURL"
        params = []
        sqrd = self.generateDummyProtocol(
            METHOD_NAME, params, self.ChannelService_REQ_TYPE
        )
        return self.postPackDataAndGetUnpackRespData(
            self.ChannelService_API_PATH, sqrd, self.ChannelService_RES_TYPE
        )
