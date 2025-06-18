import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Optional, TypedDict, Union

import requests

from ..logger import Logger

if TYPE_CHECKING:
    from ..client import CHRLINE


class BIZProtocol(ABC):

    @property
    @abstractmethod
    def client(self) -> "CHRLINE":
        raise NotImplementedError


class BIZApiProtocol(BIZProtocol):

    @property
    @abstractmethod
    def version(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def prefix(self) -> Union[str, None]:
        raise NotImplementedError

    @abstractmethod
    def url(self, path: str) -> str:
        raise NotImplementedError


class BaseBIZ(BIZProtocol):
    __client: Union["CHRLINE", None]
    __domain: Union[str, None]
    __logger: Union[Logger, None]

    def __init__(self, client: Optional["CHRLINE"]):
        self.__client = client
        self.__domain = None
        self.__logger = None

    @property
    def client(self):
        if not self.__client:
            raise NotImplementedError
        return self.__client

    @property
    def domain(self):
        if not self.__domain:
            raise NotImplementedError
        return self.__domain

    @property
    def logger(self):
        if not self.__logger:
            self.__logger = self.client.get_logger("BIZ")
        return self.__logger

    def request_get(self, path: str, *, headers: Optional[dict] = None):
        return self.client.server._session.get(self.domain + path, headers=headers)


class BaseBIZApi(BaseBIZ, BIZApiProtocol):
    __domain: Union[str, None]
    __version: int
    __prefix: Union[str, None]
    __logger: Union[Logger, None]
    __session: Union[requests.Session, None]

    def __init__(
        self, client: Optional["CHRLINE"], *, version: int, prefix: Optional[str] = None
    ):
        super().__init__(client)

        self.__domain = None
        self.__version = version
        self.__prefix = prefix
        self.__logger = None
        self.__session = None

    @property
    def version(self):
        return self.__version

    @property
    def logger(self):
        if not self.__logger:
            self.__logger = super().logger.overload(self.__class__.__name__)
        return self.__logger

    @property
    def prefix(self):
        if self.__prefix is None:
            return ""
        return self.__prefix

    @property
    def client(self):
        return super().client

    @property
    def domain(self):
        if not self.__domain:
            return self.client.LINE_HOST_DOMAIN
        return self.__domain

    @property
    def session(self):
        if self.__session is None:
            self.__session = self.client.issueHttpClient()
        return self.__session

    def url_with_prefix(self, path: str):
        return self.prefix + path

    def url(self, path: str):
        return self.url_with_prefix(f"/api/v{self.version}" + path)

    def request_get(self, path: str, *, headers: Optional[dict] = None):
        return self.request("GET", self.domain + path, headers=headers)

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[Union[Dict, TypedDict]] = None,
        required_time: bool = False,
    ):
        if params is not None:
            # 某些值實際上為可選, 一旦提供都會造成錯誤
            params = {k: v for k, v in params.items() if v is not None}
        url = self.client.server.urlEncode(self.domain, path, params)
        if headers is not None:
            if "X-LPV" in headers.keys():
                # TODO: 這裡應該檢測 data 以及 json 是否為空
                #       沒有數據時, 理應使用 GET 在 x-lhm
                #       保險起見這裡還是使用原始 method
                headers = self.client.server.additionalHeaders(
                    headers, {"x-lhm": method}
                )
                if method == "POST" and (data is None and json is None):
                    self.logger.warn(
                        f"No data was included in the {method} request to `{path}`."
                    )
                elif method == "GET" and (data is not None or json is not None):
                    self.logger.warn(
                        f"Data or json is included in the {method} request to `{path}`."
                    )
                method = "POST"
        else:
            headers = {}
        if required_time:
            headers["X-Line-App-Request-Time"] = str(int(time.time() * 1000))
        if json is not None:
            headers["Content-Type"] = "application/json; charset=UTF-8"
        self.logger.debug(f"--> {method} '{url}'")
        self.logger.debug(f"--> Headers: {headers}")
        self.logger.debug(f"--> Data: {data or json}")
        r = self.session.request(method, url, headers=headers, data=data, json=json)
        self.logger.debug(f"<-- {r.status_code} {r.content}")
        return r
