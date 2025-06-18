# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class CallService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/V4"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            "CallService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def acquireCallRoute(self, to, callType=1, fromEnvInfo={}):
        METHOD_NAME = "acquireCallRoute"
        params = [[11, 2, to], [8, 3, callType], [13, 4, [11, 11, fromEnvInfo]]]
        return self.__sender.send(METHOD_NAME, params)

    def acquireOACallRoute(self, searchId, fromEnvInfo, otp):
        METHOD_NAME = "acquireOACallRoute"
        params = [
            [12, 2, [[11, 1, searchId], [13, 2, [11, 11, fromEnvInfo]], [11, 3, otp]]]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def searchPaidCallUserRate(self, countryCode):
        METHOD_NAME = "searchPaidCallUserRate"
        params = [
            [11, 2, countryCode],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def acquirePaidCallCurrencyExchangeRate(self, countryCode):
        METHOD_NAME = "acquirePaidCallCurrencyExchangeRate"
        params = [
            [11, 2, countryCode],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def lookupPaidCall(self, dialedNumber, language, referer):
        METHOD_NAME = "lookupPaidCall"
        params = [
            [11, 2, dialedNumber],
            [11, 3, language],
            [11, 4, referer],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def acquirePaidCallRoute(
        self,
        paidCallType,
        dialedNumber,
        language,
        networkCode,
        disableCallerId,
        referer,
        adSessionId,
    ):
        METHOD_NAME = "acquirePaidCallRoute"
        params = [
            [8, 2, paidCallType],
            [11, 3, dialedNumber],
            [11, 4, language],
            [11, 5, networkCode],
            [2, 6, disableCallerId],
            [11, 7, referer],
            [11, 8, adSessionId],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getPaidCallBalanceList(self, language):
        METHOD_NAME = "getPaidCallBalanceList"
        params = [
            [11, 2, language],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getPaidCallHistory(self, start, size):
        METHOD_NAME = "getPaidCallHistory"
        params = [
            [10, 2, start],
            [8, 3, size],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getCallCreditProducts(self, appStoreCode, pgCode, country):
        METHOD_NAME = "getCallCreditProducts"
        params = [
            [8, 2, appStoreCode],
            [8, 3, pgCode],
            [11, 4, country],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def reserveCallCreditPurchase(
        self,
        productId,
        country,
        currency,
        price,
        appStoreCode,
        language,
        pgCode,
        redirectUrl,
    ):
        METHOD_NAME = "reserveCallCreditPurchase"
        params = [
            [
                12,
                2,
                [
                    [11, 1, productId],
                    [11, 2, country],
                    [11, 3, currency],
                    [11, 4, price],
                    [8, 5, appStoreCode],
                    [11, 6, language],
                    [8, 7, pgCode],
                    [11, 8, redirectUrl],
                ],
            ]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getCallCreditPurchaseHistory(self, start, size, language, eddt, appStoreCode):
        METHOD_NAME = "getCallCreditPurchaseHistory"
        params = [
            [
                12,
                2,
                [
                    [10, 1, start],
                    [8, 2, size],
                    [11, 3, language],
                    [11, 4, eddt],
                    [8, 5, appStoreCode],
                ],
            ]
        ]
        return self.__sender.send(METHOD_NAME, params)

    def redeemPaidCallVoucher(self, serial):
        METHOD_NAME = "redeemPaidCallVoucher"
        params = [[11, 2, serial]]
        return self.__sender.send(METHOD_NAME, params)

    def getPaidCallMetadata(self, language):
        METHOD_NAME = "getPaidCallMetadata"
        params = [
            [11, 2, language],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def acquireGroupCallRoute(
        self, chatMid, mediaType=1, isInitialHost=True, capabilities=[]
    ):
        METHOD_NAME = "acquireGroupCallRoute"
        params = [
            [11, 2, chatMid],
            [8, 3, mediaType],
            [2, 4, isInitialHost],
            [15, 5, [11, capabilities]],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getGroupCall(self, chatMid):
        METHOD_NAME = "getGroupCall"
        params = [
            [11, 2, chatMid],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def inviteIntoGroupCall(self, chatMid, memberMids, mediaType=1):
        METHOD_NAME = "inviteIntoGroupCall"
        params = [
            [11, 2, chatMid],
            [15, 3, [11, memberMids]],
            [8, 4, mediaType],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def markPaidCallAd(self, dialedNumber, language, disableCallerId):
        METHOD_NAME = "markPaidCallAd"
        params = [
            [11, 2, dialedNumber],
            [11, 3, language],
            [2, 4, disableCallerId],
        ]
        return self.__sender.send(METHOD_NAME, params)

    def getPaidCallAdStatus(self, dialedNumber, language, disableCallerId):
        METHOD_NAME = "getPaidCallAdStatus"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def acquireTestCallRoute(self, dialedNumber, language, disableCallerId):
        METHOD_NAME = "acquireTestCallRoute"
        params = []
        return self.__sender.send(METHOD_NAME, params)

    def getGroupCallUrls(self):
        METHOD_NAME = "getGroupCallUrls"
        params = [[12, 2, []]]
        return self.__sender.send(METHOD_NAME, params)

    def createGroupCallUrl(self, title):
        METHOD_NAME = "createGroupCallUrl"
        params = [[12, 2, [[11, 1, title]]]]
        return self.__sender.send(METHOD_NAME, params)

    def deleteGroupCallUrl(self, urlId):
        METHOD_NAME = "deleteGroupCallUrl"
        params = [[12, 2, [[11, 1, urlId]]]]
        return self.__sender.send(METHOD_NAME, params)

    def updateGroupCallUrl(self, urlId, title):
        METHOD_NAME = "updateGroupCallUrl"
        params = [[12, 2, [[11, 1, urlId], [12, 2, [[11, 1, title]]]]]]
        return self.__sender.send(METHOD_NAME, params)

    def getGroupCallUrlInfo(self, urlId):
        METHOD_NAME = "getGroupCallUrlInfo"
        params = [[12, 2, [[11, 1, urlId]]]]
        return self.__sender.send(METHOD_NAME, params)

    def joinChatByCallUrl(self, urlId):
        METHOD_NAME = "joinChatByCallUrl"
        params = [[12, 2, [[11, 1, urlId], [8, 2, self.client.getCurrReqId()]]]]
        return self.__sender.send(METHOD_NAME, params)

    def kickoutFromGroupCall(self, toMid: str, targetMids: list):
        """
        Kickout from group call.
        ---

        GENERATED BY YinMo0913_DeachSword-DearSakura_v1.0.4.py
        DATETIME: 08/26/2022, 13:18:46
        """
        METHOD_NAME = "kickoutFromGroupCall"
        params = [[12, 2, [[11, 1, toMid], [15, 2, [11, targetMids]]]]]
        return self.__sender.send(METHOD_NAME, params)

    def startPhotobooth(
        self,
        chatMid: str,
    ):
        """Start photobooth."""
        METHOD_NAME = "startPhotobooth"
        params = [
            [11, 1, chatMid],
        ]
        params = [[12, 2, params]]
        return self.__sender.send(METHOD_NAME, params)

    def startPhotoboothForMediaCall(
        self,
        chatMid: str,
    ):
        """Start photobooth for media call."""
        METHOD_NAME = "startPhotoboothForMediaCall"
        params = [
            [11, 1, chatMid],
        ]
        params = [[12, 2, params]]
        return self.__sender.send(METHOD_NAME, params)

    def usePhotoboothTicket(
        self,
        chatMid: str,
        photoboothSessionId: str,
    ):
        """Use photobooth ticket."""
        METHOD_NAME = "usePhotoboothTicket"
        params = [
            [11, 1, chatMid],
            [11, 2, photoboothSessionId],
        ]
        params = [[12, 2, params]]
        return self.__sender.send(METHOD_NAME, params)

    def getPhotoboothBalance(
        self,
    ):
        """Get photobooth balance."""
        METHOD_NAME = "getPhotoboothBalance"
        params = []
        params = [[12, 2, params]]
        return self.__sender.send(METHOD_NAME, params)

    def getMediaCall(self, chatMid: str):
        """Get media call."""
        METHOD_NAME = "getMediaCall"
        params = [[11, 1, chatMid]]
        params = [[12, 2, params]]
        return self.__sender.send(METHOD_NAME, params)

    def acquireMediaCallRoute(self, toMid: str, mediaType: int = 1):
        """Acquire media call route."""
        METHOD_NAME = "acquireMediaCallRoute"
        params = [
            [11, 1, toMid],
            [8, 2, mediaType],
        ]
        params = [[12, 2, params]]
        return self.__sender.send(METHOD_NAME, params)
