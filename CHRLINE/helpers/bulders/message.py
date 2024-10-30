import base64
import json
from typing import Optional

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

    def __new__(cls, *args, **kwargs):
        ins = kwargs["ins"]
        if isinstance(ins, dict):
            contentType = ins.get(15)
        else:
            contentType = getattr(ins, "contentType")
        if contentType == 0:
            return super().__new__(TextMessage)
        elif contentType in [1, 2, 3, 14]:
            return super().__new__(MediaMessage)
        else:
            return super().__new__(cls)

    @property
    def from_type(self):
        """
        Get from type.

        Just check is self sent:
        - OpType 25 -> return 2.
        - OpType 26 -> return 1.
        """
        if not isinstance(self._ref, DummyThrift):
            raise EOFError
        if self._ref[3] == 26:
            return 1
        return 2

    @property
    def sender(self):
        if not isinstance(self._ref, DummyThrift):
            raise EOFError
        t = 1
        if self[3] == 0:
            t = self.from_type
        return MessageUserData(self[t], _ref=self)

    @property
    def receiver(self):
        if not isinstance(self._ref, DummyThrift):
            raise EOFError
        t = 2
        if self[3] == 0:
            t = 3 - self.from_type
        return MessageUserData(self[t], _ref=self)

    def me(self):
        if self[3] in [0, 1, 2]:
            return MessageUserData(self.client.mid, _ref=self)
        square_chat_mid = self[2]
        mid = self.client.getMySquareMidByChatMid(square_chat_mid)
        return MessageUserData(mid, _ref=self)

    def is_sender(self, mid: str):
        return self[1] == mid


class TextMessage(Message):

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


class MediaMessage(Message):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.url: Optional[str] = None

    @property
    def isE2EE(self):
        return isinstance(self[20], list) and len(self[20]) > 0

    def get_url(self):
        raise NotImplementedError

    def get_object_id(self) -> str:
        if self.isE2EE:
            return self[18]["OID"]
        return self[4]

    def get_service_code(self) -> str:
        t = self[3]
        if t in [0, 1, 2]:
            return "talk"
        elif t == 4:
            return "g2"
        raise ValueError(f"Unknown SID: toType={t}")

    def get_space_id(self) -> str:
        if self.isE2EE:
            return self[18]["SID"]
        return "m"

    def download(self, savePath: Optional[str] = None):
        oid = self.get_object_id()
        svc = self.get_service_code()
        sid = self.get_space_id()
        hrs = {}
        if self.isE2EE:
            params = [[11, 4, self[4]]]
            r = self.client.generateDummyProtocolField(params, 3) + [0]
            r = base64.b64encode(bytes(r)).decode()
            meta = base64.b64encode(json.dumps({"message": r}).encode()).decode()
            hrs = {"X-Talk-Meta": meta}
            enc_obj = self.client.downloadObjectForService(
                oid, savePath, f"{svc}/{sid}", additionalHeaders=hrs
            )
            keyMaterial = self.client.decryptE2EEMessage(self)["keyMaterial"]
            return self.client.decryptByKeyMaterial(enc_obj, keyMaterial)
        return self.client.downloadObjectForService(
            oid, savePath, f"{svc}/{sid}", additionalHeaders=hrs
        )
