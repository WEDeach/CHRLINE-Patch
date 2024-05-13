# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import CHRLINE


class BaseHelper:
    __client: Optional["CHRLINE"]

    def __init__(self, cl: Optional["CHRLINE"]):
        self.__client = cl

    @property
    def client(self):
        if not self.__client:
            raise NotImplementedError
        return self.__client

    def log(self, *args, **kwargs):
        return self.client.log
