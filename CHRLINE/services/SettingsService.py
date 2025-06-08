# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class SettingsService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/US4"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def getSetting(self):
        METHOD_NAME = "getSetting"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def contextAgnosticGetSetting(self):
        METHOD_NAME = "contextAgnosticGetSetting"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def setSetting(self):
        METHOD_NAME = "setSetting"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def setSettingWithScope(self):
        METHOD_NAME = "setSettingWithScope"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def resetSetting(self):
        METHOD_NAME = "resetSetting"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def resetSettingWithScope(self):
        METHOD_NAME = "resetSettingWithScope"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def searchSettings(self):
        METHOD_NAME = "searchSettings"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def contextAgnosticSearchSettings(self):
        METHOD_NAME = "contextAgnosticSearchSettings"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def bulkGetSetting(self, settingItems: list = ["sticker.preview"]):
        METHOD_NAME = "bulkGetSetting"
        settings = []
        for i in settingItems:
            settings.append([
                [11, 1, i]
            ])
        params = [
            [12, 2, [
                [14, 1, [12, settings]]
            ]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def bulkSetSetting(self, settingItems: list = ["sticker.preview"], TypedValueItems: list = []):
        """
        - TypedValue:
            ("booleanValue", 2, 1);
            ("i64Value", 10, 2);
            ("stringValue", 11, 3);
            ("stringListValue", 15, 4);
            ("i64ListValue", 15, 5);
            ("rawJsonStringValue", 11, 6);
            ("i8Value", 3, 7);
            ("i16Value", 6, 8);
            ("i32Value", 8, 9);
            ("doubleValue", 4, 10);
            ("i8ListValue", 15, 11);
            ("i16ListValue", 15, 12);
            ("i32ListValue", 15, 13);

        example:
            self.bulkSetSetting(
                ['hometab.service.pinned'], 
                [
                    [15, 13, [8, [1419, 1072, 10]]] 
                ]
            )

            what is [15, 13, [8, [1419, 1072, 10]]]?
            that is "i32ListValue", so it using 15 and 13
            then u can see "i32List", so values is a list (type: 15)
            so the data should be [15, 13, [8, values]]
        """
        METHOD_NAME = "bulkSetSetting"
        settings = []
        c = 0
        for i in settingItems:
            settings.append([
                [11, 1, i],
                [12, 2, [TypedValueItems[c]]],
                [10, 3, 0],  # clientTimestampMillis
                # [8, 4, 0],  # ns
                # [11, 5, 0],  # transactionId
            ])
            c += 1
        params = [
            [12, 2, [
                [14, 1, [12, settings]]
            ]]
        ]
        return self.__sender.send(METHOD_NAME, params)
