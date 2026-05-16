from contextlib import contextmanager
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from ..client import CHRLINE


class BaseService:
    def __init__(self):
        pass

    @property
    def generateDummyProtocol(self):
        raise NotImplementedError

    @property
    def postPackDataAndGetUnpackRespData(self):
        raise NotImplementedError


class BaseServiceStruct:
    @staticmethod
    def BaseRequest(request: list):
        return [[12, 1, request]]

    @staticmethod
    def SendRequestByName():
        raise NotImplementedError


class BaseServiceHandler:
    def __init__(self, client: "CHRLINE") -> None:
        self.cl = client
        self._logger = self.cl.get_logger("HANDER")


class BaseServiceSender(BaseServiceHandler):
    def __init__(
        self,
        client: "CHRLINE",
        name: str,
        req_type: int,
        res_type: int,
        endpoint: str,
        *,
        baseException: Optional[Dict[str, int]] = None,
    ) -> None:
        BaseServiceHandler.__init__(self, client)

        self.name = name
        self.req_type = req_type
        self.res_type = res_type
        self.res_type = res_type
        self.endpoint = endpoint
        self.base_exception = baseException
        self._dummy_resp = False

    @contextmanager
    def dummy_resp(self):
        self._dummy_resp = True
        try:
            yield self
        finally:
            self._dummy_resp = False

    def send(self, method_name: str, params: list, **kwargs):
        """Send reqest by method name and params."""
        dummy_resp = kwargs.pop("dummy_resp", False) or self._dummy_resp
        payloads = {
            "path": self.endpoint,
            "ttype": self.res_type,
            "readWith": f"{self.name}.{method_name[0].lower()}{method_name[1:]}",
            "baseException": self.base_exception,
        }
        payloads.update(kwargs)
        if "bdata" not in payloads:
            payloads["bdata"] = self.cl.generateDummyProtocol(
                method_name, params, self.req_type
            )
        if dummy_resp:
            return bytes(payloads["bdata"])
        if payloads["ttype"] == -2:
            payloads["path"] += f"/{method_name}"
        return self.cl.postPackDataAndGetUnpackRespData(**payloads)
