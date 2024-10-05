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
    _user_data = None

    def __init__(self, mid: str, _ref: "Message") -> None:
        self.mid = mid
        self._ref = _ref

    @property
    def user_data(self):
        if self._user_data is None:
            t = self._ref.client.getToType(self.mid)
            if t == 0:
                # TODO: fetch by version control
                #       PC      -> getContactsV2
                #       PHONE   -> getContactsV3
                c = self._ref.client.getContactsV3([self.mid])
                if isinstance(c, list) and len(c) > 0:
                    self._user_data = c[0]
                raise ValueError(f"Can't fetch user data by mid: {self.mid}, res={c}")
            elif t == 5:
                c = self._ref.client.getSquareMember(self.mid)
                self._user_data = c
        return self._user_data


    @property
    def name(self):
        t = self._ref.client.getToType(self.mid)
        if t == 5:
            return self._ref._ref._ref[3]
        return "NONAME"



class Message(DummyThrift):

    @property
    def from_type(self):
        if not isinstance(self._ref, DummyThrift):
            raise EOFError
        if self[3] is not None and self[3] > 0:
            return 1
        return 2

    @property
    def sender(self):
        if not isinstance(self._ref, DummyThrift):
            print(type(self._ref), self._ref)
            raise EOFError
        t = self.from_type
        return MessageUserData(self[t], _ref=self)

    @property
    def receiver(self):
        if not isinstance(self._ref, DummyThrift):
            raise EOFError
        t = 3 - self.from_type
        return MessageUserData(self[t], _ref=self)
    
    @property
    def text(self):
        t = self[10]
        if t is not None:
            return t
        if self[15] == 0 and self.isE2EE:
            # E2EE Message
            self[10] = self.client.decryptE2EETextMessage(self)
        return self[10]

    @property
    def isE2EE(self):
        return isinstance(self[20], list) and len(self[20]) > 0

    def is_sender(self, mid: str):
        return self.sender_mid == mid
