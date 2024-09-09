# -*- coding: utf-8 -*-
from ..helper import ChrHelperProtocol
from .BaseService import BaseServiceSender, BaseServiceStruct


class ShopCollectionService(ChrHelperProtocol):
    __REQ_TYPE = 4
    __RES_TYPE = 4
    __ENDPOINT = "/ext/sapi/sapic"

    def __init__(self):
        self.__sender = BaseServiceSender(
            self.client,
            "ShopCollectionService",
            self.__REQ_TYPE,
            self.__RES_TYPE,
            self.__ENDPOINT,
        )

    def getUserCollections(
        self,
        squalastUpdatedTimeMillisreMid: int,
        includeSummary: bool,
        productType: int,
    ):
        """Get user collections."""
        METHOD_NAME = "getUserCollections"
        params = [
            [10, 1, squalastUpdatedTimeMillisreMid],
            [2, 2, includeSummary],
            [8, 3, productType],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def createCollectionForUser(
        self,
        productType: int,
    ):
        """Create collection for user."""
        METHOD_NAME = "createCollectionForUser"
        params = [
            [8, 1, productType],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def addItemToCollection(
        self,
        collectionId: str,
        productType: int,
        productId: str,
        itemId: str,
    ):
        """Add item to collection."""
        METHOD_NAME = "addItemToCollection"
        params = [
            [11, 1, collectionId],
            [8, 2, productType],
            [11, 3, productId],
            [11, 4, itemId],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def removeItemFromCollection(
        self,
        collectionId: str,
        productId: str,
        itemId: str,
    ):
        """Remove item from collection."""
        METHOD_NAME = "removeItemFromCollection"
        params = [[11, 1, collectionId], [11, 3, productId], [11, 4, itemId]]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)

    def isProductForCollections(
        self,
        productType: int,
        productId: str,
    ):
        """Is product for collections."""
        METHOD_NAME = "isProductForCollections"
        params = [
            [8, 1, productType],
            [11, 2, productId],
        ]
        params = BaseServiceStruct.BaseRequest(params)
        return self.__sender.send(METHOD_NAME, params)
