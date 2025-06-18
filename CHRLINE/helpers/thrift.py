# -*- coding: utf-8 -*-
from .base import BaseHelper
from .bulders.message import Message

TTYPE_MAP = {"ttypes.Message": Message}


class ThriftHelper(BaseHelper):
    def __init__(self):
        pass

    @staticmethod
    def getTypeWrapper(ttype_name: str):
        return TTYPE_MAP.get(ttype_name)
