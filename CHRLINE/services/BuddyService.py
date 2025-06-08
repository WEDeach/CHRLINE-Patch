# -*- coding: utf-8 -*-


from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class BuddyService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/BUDDY4"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def getPromotedBuddyContacts(self, language="zh_TW", country="TW"):
        METHOD_NAME = "getPromotedBuddyContacts"
        params = [
            [11, 2, language],
            [11, 3, country],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getBuddyCategoryView(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyCategoryView is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyCategoryView", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getBuddyChatBarV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyChatBarV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyChatBarV2", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getBuddyChatBar(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyChatBar is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyChatBar", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getCountriesHavingBuddy(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getCountriesHavingBuddy is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getCountriesHavingBuddy", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getPopularBuddyBanner(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPopularBuddyBanner is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getPopularBuddyBanner", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getBuddyStatusBarV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyStatusBarV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyStatusBarV2", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getBuddyDetailWithPersonal(self, buddyMid: str, attributeSet: list):
        METHOD_NAME = "getBuddyDetailWithPersonal"
        params = [
            [11, 1, buddyMid],
            [14, 2, [11, attributeSet]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getBuddyLive(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyLive is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyLive", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getBuddyContacts(self, language: str, country: str, classification: str, fromIndex: int, count: int):
        METHOD_NAME = "getBuddyContacts"
        params = [
            [11, 2, language],
            [11, 3, country],
            [11, 4, classification],
            [10, 5, fromIndex],
            [8, 6, count],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getBuddyTopView(self, language: str, country: str):
        """REMOVED"""
        METHOD_NAME = "getBuddyTopView"
        params = [
            [11, 2, language],
            [11, 3, country],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getBuddyCollectionEntries(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyCollectionEntries is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyCollectionEntries", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getPopularBuddyLists(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getPopularBuddyLists is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getPopularBuddyLists", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getNewlyReleasedBuddyIds(self):
        METHOD_NAME = "getNewlyReleasedBuddyIds"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getBuddyOnAir(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyOnAir is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyOnAir", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getBuddyNewsView(self, language: str, country: str, fromIndex: int, count: int):
        """REMOVED"""
        METHOD_NAME = "getBuddyNewsView"
        params = [
            [11, 2, language],
            [11, 3, country],
            [10, 4, fromIndex],
            [8, 5, count],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getCountriesServingOfficialAccountPromotionV2(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception(
            "getCountriesServingOfficialAccountPromotionV2 is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getCountriesServingOfficialAccountPromotionV2", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getBuddyStatusBar(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyStatusBar is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyStatusBar", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getRichMenuContents(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getRichMenuContents is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getRichMenuContents", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getBuddyDetail(self, buddyMid: str):
        METHOD_NAME = "getBuddyDetail"
        params = [
            [11, 4, buddyMid]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def findBuddyContactsByQuery(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("findBuddyContactsByQuery is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "findBuddyContactsByQuery", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getBuddyProfilePopup(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getBuddyProfilePopup is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getBuddyProfilePopup", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")

    def getLatestBuddyNewsTimestamp(self):
        """
        AUTO_GENERATED_CODE! DONT_USE_THIS_FUNC!!
        """
        raise Exception("getLatestBuddyNewsTimestamp is not implemented")
        params = []
        sqrd = self.generateDummyProtocol(
            "getLatestBuddyNewsTimestamp", params, self.BuddyService_REQ_TYPE)
        return self.postPackDataAndGetUnpackRespData(self.BuddyService_API_PATH, sqrd, self.BuddyService_RES_TYPE, readWith=f"BuddyService.{METHOD_NAME}")
