from typing import TYPE_CHECKING, Any

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

class BaseServiceSender(BaseServiceHandler):
    def __init__(self, client: Any, name: str, req_type: int, res_type: int, endpoint: str) -> None:
        BaseServiceHandler.__init__(self, client)

        self.name = name
        self.req_type = req_type
        self.res_type = res_type
        self.res_type = res_type
        self.endpoint = endpoint
    
    def send(self, method_name: str, params: list):
        sqrd = self.cl.generateDummyProtocol(
            method_name, params, self.req_type
        )
        return self.cl.postPackDataAndGetUnpackRespData(
            self.endpoint,
            sqrd,
            self.res_type,
            readWith=f"{self.name}.{method_name}",
        )


