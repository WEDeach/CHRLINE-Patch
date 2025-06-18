# -*- coding: utf-8 -*-
from typing import Any

from .base import BaseHelper


class SquareHelper(BaseHelper):
    def __init__(self):
        pass

    def squareMemberIdIsMe(self, squareMemberId):
        if self.client.can_use_square:
            if squareMemberId in self.client.squares.get(2, {}).keys():
                return True
            else:
                return False
        else:
            raise Exception("Not support Square")

    def getSquareMidByChatMid(self, squareChatMid: str):
        square_chat: Any = self.client.getSquareChat(squareChatMid)
        return square_chat[1][2]

    def getMySquareMidByChatMid(self, squareChatMid: str):
        square_chat: Any = self.client.getSquareChat(squareChatMid)
        return square_chat[2][1]
