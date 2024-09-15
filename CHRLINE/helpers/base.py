# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, Optional

from ..logger import Logger

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

    def log(self, text: str, debugOnly: bool = False):
        logger = self.get_logger()

        if debugOnly:
            return logger.debug(text)
        return logger.info(text)

    @staticmethod
    def get_logger(logger_name: str = "BASE"):
        """Get logger by name."""
        return Logger.new(logger_name)
