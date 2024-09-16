from ...serializers.DummyProtocol import DummyThrift

MessageStruct = [
    [1, 11, "from"],
    [2, 11, "to"],
    [3, 8, "toType"],
    [4, 11, "id"],
    [5, 10, "createdTime"],
    [6, 10, "deliveredTime"],
    #
    [10, 11, "text"],
    # [11, 12, "location", ],
    #
    [14, 2, "hasContent"],
    [15, 8, "contentType"],
    #
    [17, 11, "contentPreview"],
    [18, 13, "contentMetadata", [11, 11]],
    [19, 3, "sessionId"],
    [20, 15, "chunks", [11]],
    [21, 11, "relatedMessageId"],
    [22, 8, "messageRelationType"],
    [23, 8, "readCount"],
    [24, 8, "relatedMessageServiceCode"],
    [25, 8, "appExtensionType"],
    #
    # [27, 15, "reactions", []],
]


class MessageUserData:
    def __init__(self, mid) -> None:
        self.mid = mid


class Message(DummyThrift):

    @property
    def from_type(self):
        if not isinstance(self._ref, DummyThrift):
            raise EOFError
        if self[3] > 0:
            return 1
        return 2

    @property
    def sender(self):
        if not isinstance(self._ref, DummyThrift):
            raise EOFError
        t = self.from_type
        return MessageUserData(self[t])

    @property
    def receiver(self):
        if not isinstance(self._ref, DummyThrift):
            raise EOFError
        if self[3] > 0:
            raise ValueError
        t = 3 - self.from_type
        return MessageUserData(self[t])

    def is_sender(self, mid: str):
        return self.sender_mid == mid
