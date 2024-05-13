# -*- coding: utf-8 -*-
from .helpers import *


class ChrHelper(LiffHelper, SquareHelper, SysHelper, TalkHelper):
    def __init__(self, cl):
        super().__init__()
        BaseHelper.__init__(self, cl)

