# -*- coding: utf-8 -*-

from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender


class SecondaryPwlessLoginPermitNoticeService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/acct/lp/lgn/secpwless/v1"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            __class__.__name__,
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def checkPwlessPinCodeVerified(self, session):
        METHOD_NAME = "checkPinCodeVerified"
        params = [
            [
                12,
                1,
                [
                    [11, 1, session],
                ],
            ]
        ]
        return self.__sender.send(METHOD_NAME, params, access_token=session)

    def checkPaakAuthenticated(self, session):
        METHOD_NAME = "checkPaakAuthenticated"
        params = [[12, 1, [[11, 1, session], [11, 2, "CHANNELGW"], [2, 3, True]]]]
        return self.__sender.send(METHOD_NAME, params, access_token=session)
