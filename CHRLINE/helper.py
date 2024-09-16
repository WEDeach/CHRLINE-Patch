# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .helpers import (
    BaseHelper,
    LiffHelper,
    SquareHelper,
    SysHelper,
    TalkHelper,
    ThriftHelper,
)

if TYPE_CHECKING:
    from .client import CHRLINE


class ChrHelperProtocol(ABC):

    @property
    @abstractmethod
    def client(self) -> "CHRLINE":
        raise NotImplementedError


class ChrHelper(LiffHelper, SquareHelper, SysHelper, TalkHelper, ThriftHelper):
    def __init__(self, cl):
        super().__init__()
        BaseHelper.__init__(self, cl)
