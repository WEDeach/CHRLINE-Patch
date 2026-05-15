import time
from typing import TYPE_CHECKING, Optional

from .serializers.DummyProtocol import DummyThrift

if TYPE_CHECKING:
    from .client import CHRLINE


STG_T_INFO_MISSING = False
STG_T_TOKEN_EXPIRED = False
STG_T_LOGGER_FORCE_INFO = False


class TokenManager:
    def __init__(self, client: "CHRLINE"):
        self._client = client
        self._channel_tokens = {}

        self.__logger = self._client.logger.new("TOKEN")

    def issueChannelToken(self, channel_id: str) -> Optional[DummyThrift]:
        token = self._client.approveChannelAndIssueChannelToken(channel_id)
        if token is not None:
            self._channel_tokens[channel_id] = token
        return self._channel_tokens.get(channel_id)

    def removeChannelToken(self, channel_id: str):
        if channel_id in self._channel_tokens:
            del self._channel_tokens[channel_id]

    def getChannelToken(
        self, channel_id: str, autoRenew: bool = True
    ) -> Optional[DummyThrift]:
        if channel_id not in self._channel_tokens:
            token_info = self.issueChannelToken(channel_id)
            if token_info is not None:
                self._channel_tokens[channel_id] = token_info
            else:
                raise ValueError(
                    f"Failed to issue channel token for channel_id: {channel_id}"
                )
        token_info = self._channel_tokens.get(channel_id)
        if autoRenew and not self.isValid(token_info):
            self.log(
                f"Channel token for channel_id {channel_id} is expired. Attempting to renew...",
                isDebug=True,
            )
            self.removeChannelToken(channel_id)
            return self.getChannelToken(channel_id, False)

        if STG_T_INFO_MISSING:
            # NOTE: 通常失敗會拋起錯誤, 所以不應該存在TOKEN_INFO為空的情況
            token_info = None
        elif STG_T_TOKEN_EXPIRED and token_info is not None:
            token_info[3] = 0

        if not self.isValid(token_info):
            raise ValueError(
                f"Failed to get channel token for channel_id: {channel_id}, token_info: {token_info}"
            )

        return token_info

    def getChannelAccessToken(
        self, channel_id: str, autoRenew: bool = True
    ) -> Optional[str]:
        return self._client.checkAndGetValue(
            self.getChannelToken(channel_id, autoRenew),
            "channelAccessToken",
            5,
        )

    def isValid(self, token_info: Optional[DummyThrift]) -> bool:
        if token_info is None:
            return False

        expiration = self._client.checkAndGetValue(token_info, "expiration", 3)
        t = time.time()
        if expiration is None:
            raise ValueError(
                f"ChannelToken missing `expiration` field. token_info: {token_info}"
            )
        return t < expiration

    def log(self, message: str, *, isDebug: bool = False):
        if STG_T_LOGGER_FORCE_INFO or not isDebug:
            self.__logger.info(message)
        else:
            self.__logger.debug(message)
