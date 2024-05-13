# -*- coding: utf-8 -*-
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
