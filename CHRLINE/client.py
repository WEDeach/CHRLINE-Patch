from typing import Any, List, Optional

import gevent.monkey

from .services.thrift.ttypes import SquareException

gevent.monkey.patch_all()

from os import system

from .api import API
from .config import Config
from .cube import LineCube
from .e2ee import E2EE
from .exceptions import LineServiceException
from .helper import ChrHelper
from .models import Models
from .object import Object
from .poll import Poll
from .thrift import Thrift
from .timeline import Timeline
from .timelineBiz import TimelineBiz


class CHRLINE(
    ChrHelper,
    Models,
    Config,
    API,
    Thrift,
    Poll,
    Object,
    Timeline,
    TimelineBiz,
    LineCube,
    E2EE,
):
    def __init__(
        self,
        authTokenOrEmail: Optional[str] = None,
        password: Optional[str] = None,
        device: str = "CHROMEOS",
        version: Optional[str] = None,
        os_name: Optional[str] = None,
        os_version: Optional[str] = None,
        noLogin: bool = False,
        encType: int = 1,
        debug: bool = False,
        customDataId: Optional[str] = None,
        phone: Optional[str] = None,
        region: Optional[str] = None,
        forwardedIp: Optional[str] = None,
        useThrift: bool = False,
        forceTMCP: bool = False,
        savePath: Optional[str] = None,
        os_model: Optional[str] = None,
        rootLogLevel: int = 20,
        logFilterNs: List[str] = [],
    ):
        r"""
        Line client for CHRLINE.

        Use authToken or Email & Password to Login
        phone + region to Login secondary devices (and Android).

        ------------------------
        device: `str`
            Line special device name, you can view and add in config.py.
        version: `str`
            The device's version. it may affect some functions.
        os_name: `str`
            Customized system OS name.
        os_version: `str`
            Customized system OS version.
        noLogin: `bool`
            Set whether not to login
        encType: `int`
            Encryption for requests.
            - 0: no encryption.
            - 1: legy encryption

        debug: `bool`
            *Developer options*
            For view some params and logs
        customDataId: `str`
            Special the customData id
        forwardedIp: `str`
            Fake ip used to spoof the server.
            ** not necessarily work **
        useThrift: `bool`
            Set whether to use line thrift.
            If true, you must place line thrifts in `services\thrift`.
        forceTMCP: `bool`
            It will force the use of TMoreCompact protocol on TalkService.
        savePath: `str`
            Set base-save dir path.
        os_model: `str`
            Set System model name.
        """
        if device == "CHROMEOS" and version is None and not noLogin:
            raise ValueError(
                'Please specify the version of LINE for CHROMEOS: `CHRLINE(..., version="3")`\nor just use other device type to login: `CHRLINE(..., device="DESTOPWIN")`'
            )
        self.encType = encType
        self.isDebug = debug
        if customDataId is None:
            customDataId = "CHRLINE_CUSTOM_0"
        self.customDataId = customDataId
        self.can_use_square = False
        self.squares: Any = None
        ChrHelper.__init__(self, cl=self)
        self.logger = self.get_logger()
        if self.isDebug:
            rootLogLevel = 0
        self.logger.set_root_level(rootLogLevel)
        if logFilterNs:
            self.logger.add_log_fliters(*logFilterNs)
        Models.__init__(self, savePath)
        Config.__init__(self, device)
        self.initAppConfig(device, version, os_name, os_version, os_model)
        API.__init__(self, forwardedIp)
        Thrift.__init__(self)
        self.is_login = False
        self.use_thrift = useThrift
        self.force_tmore = forceTMCP
        if region is not None:
            self.LINE_SERVICE_REGION = region

        if authTokenOrEmail is not None and password is not None:
            email_func = self.requestEmailLogin
            if device in self.TOKEN_V3_SUPPORT:
                email_func = self.requestEmailLoginV2
            email_func(authTokenOrEmail, password)
        elif authTokenOrEmail:
            self.authToken = authTokenOrEmail
        elif phone:
            self.requestPwlessLogin(phone, self.LINE_SERVICE_REGION)
        else:
            if not noLogin:
                sqr_func = self.requestSQR
                if device in self.TOKEN_V3_SUPPORT:
                    sqr_func = self.requestSQR2
                for b in sqr_func():
                    print(b)
        if self.authToken:
            self.initAll()

    def initAll(self):
        self.checkNextToken(False)
        self.profile = self.getProfile()
        if self.profile is None:
            raise RuntimeError(
                f"Can't get user profile, maybe the device version {self.APP_VER} is too old.\nTry use CHRLINE(..., version='...') to set new version."
            )
        __profile_err = self.checkAndGetValue(self.profile, "error")
        if __profile_err is not None:
            self.log(f"Login failed... {__profile_err}")
            b = None
            try:
                for b in self.requestSQR(False):
                    print(b)
            except Exception as _:
                raise Exception(f"Login failed... {__profile_err}")
            if b is not None:
                self.handleNextToken(b)
            return self.initAll()
        mid = self.checkAndGetValue(self.profile, "mid", 1)
        if not isinstance(mid, str):
            raise TypeError(
                "`mid` expected type `str`, but got type `%s`: %r"
                % (type(mid), mid)
            )
        self.mid = mid
        __displayName = self.checkAndGetValue(self.profile, "displayName", 20)
        self.logger.info(
            f"[{__displayName}] 登入成功 ({self.mid}) / {self.DEVICE_TYPE}"
        )
        if self.customDataId is None:
            self.customDataId = self.mid
        try:
            system(f"title CHRLINE - {__displayName}")
        except Exception as _:
            pass
        self.revision = -1
        try:
            self.groups = self.checkAndGetValue(
                self.getAllChatMids(), "memberChatMids", 1
            )
        except Exception as e:
            self.log(f"[getAllChatMids] {e}")
            self.groups = []

        E2EE.__init__(self)
        Timeline.__init__(self)
        TimelineBiz.__init__(self)
        Poll.__init__(self)
        Object.__init__(self)
        LineCube.__init__(self)

        self.is_login = True

        self.can_use_square = False
        try:
            _squares = self.getJoinedSquares()
            self.can_use_square = True
            self.squares = _squares
        except SquareException as e:
            self.log(f"Not support Square: {getattr(e, 'reason')}")
        except LineServiceException as e:
            self.log(f"Not support Square: {e.message}")

        self.custom_data = {}
        self.getCustomData()
