from typing import TYPE_CHECKING, Optional

from .serializers.DummyProtocol import DummyThrift

if TYPE_CHECKING:
    from .client import CHRLINE

# TODO: 檢測token過期時間，並刷新token
#       即使ACCESS TOKEN過期, CHANNEL TOKEN的過期時間並不會被影響

class TokenManager:
    def __init__(self, client: "CHRLINE"):
        self._client = client
        self._channel_tokens = {}

    def issueChannelToken(self, channel_id: str) -> Optional[DummyThrift]:
        token = self._client.approveChannelAndIssueChannelToken(channel_id)
        if token is not None:
            self._channel_tokens[channel_id] = token
        return self._channel_tokens.get(channel_id)

    def getChannelToken(
        self, channel_id: str, renew: bool = False
    ) -> Optional[DummyThrift]:
        if renew or channel_id not in self._channel_tokens:
            token_info = self.issueChannelToken(channel_id)
            if token_info is not None:
                self._channel_tokens[channel_id] = token_info
            else:
                raise ValueError(
                    f"Failed to issue channel token for channel_id: {channel_id}"
                )
        return self._channel_tokens.get(channel_id)

    def getChannelAccessToken(
        self, channel_id: str, renew: bool = False
    ) -> Optional[str]:
        return self._client.checkAndGetValue(
            self.getChannelToken(channel_id, renew),
            "channelAccessToken",
            5,
        )
