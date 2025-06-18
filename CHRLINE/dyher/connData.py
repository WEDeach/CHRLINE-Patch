import json
import struct
from typing import Optional, Union
from enum import IntEnum


class LegyH2PingFrameType(IntEnum):
    NONE = 0
    ACK = 1
    ACK_REQUIRED = 2


class LegyH2PushFrameType(IntEnum):
    NONE = 0
    ACK = 1
    ACK_REQUIRED = 2


class LegyH2Frame:
    def __init__(self, frameType: int):
        self.frame_type = frameType

    def request_packet(self, payload: bytes):
        return struct.pack("!H", len(payload)) + bytes([self.frame_type]) + payload


class LegyH2StatusFrame(LegyH2Frame):
    def __init__(
        self,
        isForeground: Optional[bool] = None,
        serverPingInterval: Optional[int] = None,
    ):
        super().__init__(0)
        self.is_foreground = isForeground
        self.server_ping_interval = serverPingInterval


class LegyH2PingFrame(LegyH2Frame):
    def __init__(
        self,
        pingType: Optional[Union[LegyH2PingFrameType, int]] = None,
        pingId: Optional[int] = None,
    ):
        super().__init__(1)
        self.ping_type = LegyH2PingFrameType(pingType)
        self.ping_id = pingId

    def ack_packet(self):
        return self.request_packet(
            bytes([LegyH2PingFrameType.ACK.value]) + struct.pack("!H", self.ping_id)
        )


class LegyH2SignOnRequestsFrame(LegyH2Frame):
    def __init__(
        self,
        requestId: Optional[int] = None,
        serviceType: Optional[int] = None,
        responsePayload: Optional[bytes] = None,
    ):
        super().__init__(2)
        self.request_id = requestId
        self.service_type = serviceType
        self.response_payload = responsePayload


class LegyH2SignOnResponseFrame(LegyH2Frame):
    def __init__(
        self,
        requestId: Optional[int] = None,
        isFin: Optional[bool] = None,
        responsePayload: Optional[bytes] = None,
    ):
        super().__init__(3)
        self.request_id = requestId
        self.is_fin = isFin
        self.response_payload = responsePayload


class LegyH2PushFrame(LegyH2Frame):
    def __init__(
        self,
        pushType: Optional[Union[LegyH2PushFrameType, int]] = None,
        serviceType: Optional[int] = None,
        pushId: Optional[int] = None,
        pushPayload: Optional[bytes] = None,
    ):
        super().__init__(4)
        self.push_type = LegyH2PushFrameType(pushType)
        self.service_type = serviceType
        self.push_id = pushId
        self.push_payload = pushPayload

    def ack_packet(self):
        if self.service_type and self.push_id:
            return self.request_packet(
                bytes([LegyH2PushFrameType.ACK.value] + [self.service_type])
                + struct.pack("!i", self.push_id)
                + b""
            )
        raise ValueError


class LegyPushData:
    def __init__(self):
        pass


class LegyPushOABot:
    def __init__(
        self,
        *,
        _type: Optional[str] = None,
        timestamp: Optional[str] = None,
        typingSeconds: Optional[str] = None,
        botMid: Optional[str] = None,
        chatMid: Optional[str] = None,
    ):
        self._type = _type
        self.timestamp = timestamp
        self.typing_seconds = typingSeconds
        self.bot_mid = botMid
        self.chat_mid = chatMid

    @staticmethod
    def unwrap(data: bytes):
        s = json.loads(data.decode())
        r = LegyPushOABot
        if s["type"] == "typing":
            r = LegyPushOABotTyping
        return r(
            _type=s["type"],
            timestamp=s["timestamp"],
            typingSeconds=s["typingSeconds"],
            botMid=s["botMid"],
            chatMid=s["chatMid"],
        )


class LegyPushOABotTyping(LegyPushOABot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
