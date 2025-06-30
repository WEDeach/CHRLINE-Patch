# -*- coding: utf-8 -*-
import base64
import binascii

import rsa

from .exceptions import LineServiceException
from .server import Server
from .services.AccessTokenRefreshService import AccessTokenRefreshService
from .services.AccountAuthFactorEapConnectService import (
    AccountAuthFactorEapConnectService,
)
from .services.AuthService import AuthService
from .services.BuddyService import BuddyService
from .services.CallService import CallService
from .services.ChannelService import ChannelService
from .services.ChatAppService import ChatAppService
from .services.CoinService import CoinService
from .services.E2EEKeyBackupService import E2EEKeyBackupService
from .services.HomeSafetyCheckService import HomeSafetyCheckService
from .services.InterlockService import InterlockService
from .services.LiffService import LiffService
from .services.LoginService import LoginService
from .services.MultiProfileService import MultiProfileService
from .services.PasswordUpdateService import PasswordUpdateService
from .services.PremiumFontService import PremiumFontService
from .services.PremiumStatusService import PremiumStatusService
from .services.PrimaryAccountInitService import PrimaryAccountInitService
from .services.PrimaryAccountReLoginService import PrimaryAccountReLoginService
from .services.PrimaryAccountSmartSwitchRestorePreparationService import (
    PrimaryAccountSmartSwitchRestorePreparationService,
)
from .services.PrimaryAccountSmartSwitchRestoreService import (
    PrimaryAccountSmartSwitchRestoreService,
)
from .services.PrimaryQrCodeMigrationLongPollingService import (
    PrimaryQrCodeMigrationLongPollingService,
)
from .services.PrimaryQrCodeMigrationPreparationService import (
    PrimaryQrCodeMigrationPreparationService,
)
from .services.PrimarySeamlessLoginService import PrimarySeamlessLoginService
from .services.RegistrationAuthService import RegistrationAuthService
from .services.RelationService import RelationService
from .services.SecondaryPwlessLoginPermitNoticeService import (
    SecondaryPwlessLoginPermitNoticeService,
)
from .services.SecondaryPwlessLoginService import SecondaryPwlessLoginService
from .services.SecondarySeamlessLoginService import SecondarySeamlessLoginService
from .services.SettingsService import SettingsService
from .services.ShopCollectionService import ShopCollectionService
from .services.ShopService import ShopService
from .services.SquareBotService import SquareBotService
from .services.SquareLiveTalkService import SquareLiveTalkService
from .services.SquareService import SquareService
from .services.TalkService import TalkService
from .services.TestService import TestService


class API(
    TalkService,
    ShopService,
    LiffService,
    ChannelService,
    SquareService,
    BuddyService,
    PrimaryAccountInitService,
    AuthService,
    SettingsService,
    AccessTokenRefreshService,
    CallService,
    SecondaryPwlessLoginService,
    SecondaryPwlessLoginPermitNoticeService,
    ChatAppService,
    AccountAuthFactorEapConnectService,
    E2EEKeyBackupService,
    SquareBotService,
    TestService,
    HomeSafetyCheckService,
    PrimaryQrCodeMigrationLongPollingService,
    PrimaryQrCodeMigrationPreparationService,
    LoginService,
    InterlockService,
    RelationService,
    SquareLiveTalkService,
    CoinService,
    ShopCollectionService,
    PremiumFontService,
    RegistrationAuthService,
):
    _msgSeq = 0

    def __init__(self, forwardedIp=None):
        self.__logger = self.client.get_logger("API")
        self.server = Server()
        self.req = self.client.issueHttpClient()
        self.req_h2 = self.client.issueHttpClient(1)
        self.server.Headers = {
            "x-line-application": self.client.APP_NAME,
            "x-le": self.client.le,
            "x-lap": "5",
            "x-lpv": "1",
            "x-lcs": self.client._encryptKey,
            "User-Agent": self.client.LineUserAgent,
            "content-type": "application/x-thrift; protocol=TBINARY",
            "x-lal": self.client.LINE_LANGUAGE,
            "x-lhm": "POST",
        }
        self.__logger.info(f"Use User-Agent: {self.client.USER_AGENT}")
        if forwardedIp is not None:
            self.server.Headers["X-Forwarded-For"] = forwardedIp
        self.authToken = None
        self.revision = 0
        self.globalRev = 0
        self.individualRev = 0
        self._msgSeq = 0
        TalkService.__init__(self)
        ShopService.__init__(self)
        LiffService.__init__(self)
        ChannelService.__init__(self)
        SquareService.__init__(self)
        BuddyService.__init__(self)
        PrimaryAccountInitService.__init__(self)
        AuthService.__init__(self)
        SettingsService.__init__(self)
        AccessTokenRefreshService.__init__(self)
        CallService.__init__(self)
        SecondaryPwlessLoginService.__init__(self)
        SecondaryPwlessLoginPermitNoticeService.__init__(self)
        ChatAppService.__init__(self)
        AccountAuthFactorEapConnectService.__init__(self)
        E2EEKeyBackupService.__init__(self)
        SquareBotService.__init__(self)
        TestService.__init__(self)
        HomeSafetyCheckService.__init__(self)
        PrimaryQrCodeMigrationLongPollingService.__init__(self)
        PrimaryQrCodeMigrationPreparationService.__init__(self)
        LoginService.__init__(self)
        InterlockService.__init__(self)
        RelationService.__init__(self)
        SquareLiveTalkService.__init__(self)
        CoinService.__init__(self)
        ShopCollectionService.__init__(self)
        PremiumFontService.__init__(self)
        RegistrationAuthService.__init__(self)
        self.s_smart_switch = PrimaryAccountSmartSwitchRestorePreparationService(self)
        self.s_smart_switch_sec = PrimaryAccountSmartSwitchRestoreService(self)
        self.s_multi_profile = MultiProfileService(self.client)
        self.s_premium_status = PremiumStatusService(self.client)
        self.s_seamless = PrimarySeamlessLoginService(self.client)
        self.s_seamless_sec = SecondarySeamlessLoginService(self.client)
        self.s_relogin = PrimaryAccountReLoginService(self.client)
        self.s_pwd_update = PasswordUpdateService(self.client)

    def requestPwlessLogin(self, phone, region):
        pwless_code = self.client.checkAndGetValue(
            self.createPwlessSession(phone, region), 1, "val_1"
        )
        print(f"PWLESS SESSION: {pwless_code}")
        cert = self.client.getCacheData(".pwless", phone)
        try:
            self.verifyLoginCertificate(pwless_code, "" if cert is None else cert)
        except Exception as _:
            pwless_pincode = self.client.checkAndGetValue(
                self.requestPinCodeVerif(pwless_code), 1, "val_1"
            )
            print(f"PWLESS PINCODE: {pwless_pincode}")
            self.checkPwlessPinCodeVerified(pwless_code)
        secret, secretPK = self.client.createSqrSecret(True)
        self.putExchangeKey(pwless_code, secretPK)
        self.requestPaakAuth(pwless_code)
        print("need Paak Auth Confind")
        self.checkPaakAuthenticated(pwless_code)
        ek = self.getE2eeKey(pwless_code)
        try:
            loginInfo = self.pwlessLoginV2(pwless_code)
            cert = self.client.checkAndGetValue(loginInfo, 2, "val_2")
            tokenInfo = self.client.checkAndGetValue(loginInfo, 3, "val_3")
            token = self.client.checkAndGetValue(tokenInfo, 1, "val_1")
            token2 = self.client.checkAndGetValue(tokenInfo, 2, "val_2")
            mid = self.client.checkAndGetValue(loginInfo, 5, "val_5")
        except Exception as _:
            loginInfo = self.pwlessLogin(pwless_code)
            token = self.client.checkAndGetValue(loginInfo, 1, "val_1")
            cert = self.client.checkAndGetValue(loginInfo, 2, "val_2")
            mid = self.client.checkAndGetValue(loginInfo, 4, "val_4")
        self.authToken = token
        print(f"Auth Token: {self.authToken}")
        self.client.saveCacheData(".pwless", phone, cert)
        metadata = self.client.checkAndGetValue(ek, 1, "val_1")
        if metadata is not None:
            self.client.decodeE2EEKeyV1(metadata, secret, mid)
        return True

    def requestEmailLogin(self, email, pw, e2ee=True):
        rsaKey = self.getRSAKeyInfo()
        keynm = self.client.checkAndGetValue(rsaKey, 1, "val_1")
        nvalue = self.client.checkAndGetValue(rsaKey, 2, "val_2")
        evalue = self.client.checkAndGetValue(rsaKey, 3, "val_3")
        sessionKey = self.client.checkAndGetValue(rsaKey, 4, "val_4")
        certificate = self.client.getEmailCert(email)
        if sessionKey is None:
            raise ValueError("sessionKey is nil")
        if nvalue is None or evalue is None:
            raise ValueError("nvalue and evalue can't be nil")
        message = (
            chr(len(sessionKey))
            + sessionKey
            + chr(len(email))
            + email
            + chr(len(pw))
            + pw
        ).encode("utf-8")
        pub_key = rsa.PublicKey(int(nvalue, 16), int(evalue, 16))
        crypto = binascii.hexlify(rsa.encrypt(message, pub_key)).decode()
        secret, secretPK = self.client.createSqrSecret(True)
        pincode = "202202"
        _secret = self.client._encryptAESECB(
            self.client.getSHA256Sum(pincode.encode()), base64.b64decode(secretPK)
        )
        _req = {
            "keynm": keynm,
            "encData": crypto,
            "secret": _secret,
            "deviceName": self.client.SYSTEM_MODEL,
            "calledName": "loginZ",
        }
        if not e2ee:
            _req["secret"] = None
        try:
            res = self.loginV2(**_req, cert=certificate)
        except LineServiceException as e:
            res = {}
            if e.code == 89:
                if not e2ee:
                    raise e
                return self.requestEmailLogin(email, pw, False)
            raise e
        if self.client.checkAndGetValue(res, 1, "val_1") is None:
            verifier = self.client.checkAndGetValue(res, 3, "val_3")
            if not e2ee:
                pincode = self.client.checkAndGetValue(res, 4)
            print(f"Enter Pincode: {pincode}")
            if e2ee:
                e2eeInfo = self.checkLoginV2PinCode(verifier)["metadata"]
                try:
                    self.client.decodeE2EEKeyV1(e2eeInfo, secret)
                except Exception as _:
                    raise Exception("e2eeInfo decode failed, try again")
                blablabao = self.client.encryptDeviceSecret(
                    base64.b64decode(e2eeInfo["publicKey"]),
                    secret,
                    base64.b64decode(e2eeInfo["encryptedKeyChain"]),
                )
                e2eeLogin = self.confirmE2EELogin(verifier, blablabao)
            else:
                e2eeLogin = self.checkLoginZPinCode(verifier)["verifier"]
            try:
                res = self.loginV2(**_req, verifier=e2eeLogin)
                self.client.saveEmailCert(
                    email, self.client.checkAndGetValue(res, 2, "val_2")
                )
            except Exception as _:
                raise Exception("confirmE2EELogin failed, try again")
        self.authToken = self.client.checkAndGetValue(res, 1)
        print(f"AuthToken: {self.authToken}")
        return True

    def requestEmailLoginV2(self, email, pw):
        rsaKey = self.getRSAKeyInfo()
        keynm = self.client.checkAndGetValue(rsaKey, 1, "val_1")
        nvalue = self.client.checkAndGetValue(rsaKey, 2, "val_2")
        evalue = self.client.checkAndGetValue(rsaKey, 3, "val_3")
        sessionKey = self.client.checkAndGetValue(rsaKey, 4, "val_4")
        certificate = self.client.getEmailCert(email)
        if sessionKey is None:
            raise ValueError("sessionKey is nil")
        if nvalue is None or evalue is None:
            raise ValueError("nvalue and evalue can't be nil")
        message = (
            chr(len(sessionKey))
            + sessionKey
            + chr(len(email))
            + email
            + chr(len(pw))
            + pw
        ).encode("utf-8")
        pub_key = rsa.PublicKey(int(nvalue, 16), int(evalue, 16))
        crypto = binascii.hexlify(rsa.encrypt(message, pub_key)).decode()
        secret, secretPK = self.client.createSqrSecret(True)
        pincode = b"1314520"
        _secret = self.client._encryptAESECB(
            self.client.getSHA256Sum(pincode), base64.b64decode(secretPK)
        )
        try:
            res = self.loginV2(
                keynm,
                crypto,
                _secret,
                deviceName=self.client.SYSTEM_MODEL,
                cert=certificate,
            )
        except LineServiceException as e:
            if e.code == 89:
                print(f"can't login: {e.message}, try use LoginZ...")
                return self.requestEmailLogin(email, pw)
            raise e
        if self.client.checkAndGetValue(res, 9, "val_9") is None:
            verifier = self.client.checkAndGetValue(res, 3, "val_3")
            if self.client.checkAndGetValue(res, 5, "val_5") == 3:
                print("need device confirm")
            print(f"Enter Pincode: {pincode.decode()}")
            e2eeInfo = self.checkLoginV2PinCode(verifier)["metadata"]
            try:
                e2eeKeyInfo = self.client.decodeE2EEKeyV1(e2eeInfo, secret)
            except Exception as _:
                raise Exception("e2eeInfo decode failed, try again")
            blablabao = self.client.encryptDeviceSecret(
                base64.b64decode(e2eeInfo["publicKey"]),
                secret,
                base64.b64decode(e2eeInfo["encryptedKeyChain"]),
            )
            e2eeLogin = self.confirmE2EELogin(verifier, blablabao)
            try:
                res = self.loginV2(
                    None,
                    None,
                    None,
                    deviceName=self.client.SYSTEM_NAME,
                    verifier=e2eeLogin,
                )
            except LineServiceException as e:
                print(e)
                if e.code in [20, 89]:
                    print(f"can't login: {e.message}, try use LoginZ...")
                    return self.requestEmailLogin(email, pw)
            self.client.saveEmailCert(
                email, self.client.checkAndGetValue(res, 2, "val_2")
            )
        loginInfo = self.client.checkAndGetValue(res, 9, "val_9")
        self.authToken = self.client.checkAndGetValue(loginInfo, 1, "val_1")
        refreshToken = self.client.checkAndGetValue(loginInfo, 2, "val_2")
        self.client.saveCacheData(".refreshToken", self.client.authToken, refreshToken)
        print(f"AuthToken: {self.authToken}")
        print(f"RefreshToken: {refreshToken}")
        return True

    def requestSQR(self, isSelf=True):
        sqr = self.client.checkAndGetValue(self.createSession(), 1, "val_1")
        url = self.client.checkAndGetValue(self.createQrCode(sqr), 1, "val_1")
        if sqr is None:
            raise ValueError("sqr is nil")
        secret, secretUrl = self.client.createSqrSecret()
        url = url + secretUrl
        imgPath = self.client.genQrcodeImageAndPrint(url)
        yield f"URL: {url}"
        yield f"IMG: {imgPath}"
        if self.checkQrCodeVerified(sqr):
            try:
                self.verifyCertificate(sqr, self.client.getSqrCert())
            except Exception as _:
                c = self.client.checkAndGetValue(self.createPinCode(sqr), 1, "val_1")
                yield f"請輸入pincode: {c}"
                self.checkPinCodeVerified(sqr)
            e = self.qrCodeLogin(sqr, secret)
            if isSelf:
                self.authToken = e
                print(f"AuthToken: {self.authToken}")
            else:
                yield e
            return
            raise Exception("can not check pin code, try again?")
        raise Exception("can not check qr code, try again?")

    def requestSQR2(self, isSelf=True):
        sqr = self.client.checkAndGetValue(self.createSession(), 1, "val_1")
        url = self.client.checkAndGetValue(self.createQrCode(sqr), 1, "val_1")
        secret, secretUrl = self.client.createSqrSecret()
        url = url + secretUrl
        imgPath = self.client.genQrcodeImageAndPrint(url)
        yield f"URL: {url}"
        yield f"IMG: {imgPath}"
        if self.checkQrCodeVerified(sqr):
            try:
                self.verifyCertificate(sqr, self.client.getSqrCert())
            except Exception as _:
                c = self.createPinCode(sqr)
                yield f"請輸入pincode: {c}"
                self.checkPinCodeVerified(sqr)
            try:
                e = self.qrCodeLoginV2(
                    sqr, self.client.MODEL_NAME, self.client.USERDOMAIN, False
                )
                cert = self.client.checkAndGetValue(e, 1)
                self.client.saveSqrCert(cert)
                tokenV3Info = self.client.checkAndGetValue(e, 3)
                _mid = self.client.checkAndGetValue(e, 4)
                bT = self.client.checkAndGetValue(e, 9)
                metadata = self.client.checkAndGetValue(e, 10)
                if metadata:
                    e2eeKeyInfo = self.client.decodeE2EEKeyV1(metadata, secret)
                authToken = self.client.checkAndGetValue(tokenV3Info, 1)
                refreshToken = self.client.checkAndGetValue(tokenV3Info, 2)
                self.client.saveCacheData(".refreshToken", authToken, refreshToken)
                print(f"AuthToken: {authToken}")
                print(f"RefreshToken: {refreshToken}")
                if isSelf:
                    self.authToken = authToken
                yield authToken
            except LineServiceException as e:
                if e.code == 100:
                    # BANNED.
                    raise e
                print(e)
                yield "try using requestSQR()..."
                for _ in self.requestSQR(isSelf):
                    yield _
            return
            raise Exception("can not check pin code, try again?")
        raise Exception("can not check qr code, try again?")

    def requestSQR3(self, isSelf=True):
        """
        Request Secondary QrCode Login for secure.

        Source: https://github.com/DeachSword/CHRLINE/blob/445e433b1fbe9a020f6bc1cbd0eb7af3f75ce196/examples/test_sqr_4_secure.py
        """
        log4Debug = False
        sqr = self.client.checkAndGetValue(self.createSession(), 1)
        if sqr is None:
            raise ValueError("sqr is nil")
        qr4s = self.createQrCodeForSecure(sqr)
        url = self.client.checkAndGetValue(qr4s, "callbackUrl", 1)
        nonce = self.client.checkAndGetValue(qr4s, "nonce", 4)
        if nonce is None:
            raise ValueError("nonce is nil")
        self.client.log(f"nonce: {nonce}", log4Debug)
        secret, secretUrl = self.client.createSqrSecret()
        url = url + secretUrl
        imgPath = self.client.genQrcodeImageAndPrint(url)
        yield f"URL: {url}"
        yield f"IMG: {imgPath}"
        if self.checkQrCodeVerified(sqr):
            try:
                self.verifyCertificate(sqr, self.client.getSqrCert())
            except Exception as _:
                c = self.createPinCode(sqr)
                yield f"Enter Pincode: {c}"
                self.checkPinCodeVerified(sqr)
            try:
                e = self.qrCodeLoginV2ForSecure(
                    sqr, self.client.MODEL_NAME, self.client.USERDOMAIN, nonce
                )
                self.client.log(e, log4Debug)
                cert = self.client.checkAndGetValue(e, "certificate", 1)
                self.client.saveSqrCert(cert)
                tokenV3Info = self.client.checkAndGetValue(e, "tokenV3IssueResult", 3)
                _mid = self.client.checkAndGetValue(e, "mid", 4)
                metadata = self.client.checkAndGetValue(e, "metaData", 10)
                if metadata:
                    self.client.decodeE2EEKeyV1(metadata, secret, _mid)
                authToken = self.client.checkAndGetValue(tokenV3Info, "accessToken", 1)
                refreshToken = self.client.checkAndGetValue(
                    tokenV3Info, "refreshToken", 2
                )
                self.client.saveCacheData(".refreshToken", authToken, refreshToken)
                print(f"AuthToken: {authToken}")
                print(f"RefreshToken: {refreshToken}")
                if isSelf:
                    self.authToken = authToken
                yield authToken
            except LineServiceException as e:
                if e.code == 100:
                    # BANNED.
                    raise e
                print(e)
                yield "try using requestSQR()..."
                for _ in self.requestSQR(isSelf):
                    yield _
            return
        raise Exception("can not check qr code, try again?")

    def createSession(self):
        """Create SQR session."""
        params = []
        sqrd = self.client.generateDummyProtocol("createSession", params, 4)
        return self.client.postPackDataAndGetUnpackRespData("/acct/lgn/sq/v1", sqrd, 4)

    def createQrCode(self, qrcode):
        params = [[12, 1, [[11, 1, qrcode]]]]
        sqrd = self.client.generateDummyProtocol("createQrCode", params, 3)
        return self.client.postPackDataAndGetUnpackRespData("/acct/lgn/sq/v1", sqrd, 3)

    def checkQrCodeVerified(self, qrcode):
        params = [
            [
                12,
                1,
                [
                    [11, 1, qrcode],
                ],
            ],
        ]
        sqrd = self.client.generateDummyProtocol("checkQrCodeVerified", params, 3)
        headers = self.server.additionalHeaders(
            self.server.Headers, {"x-lst": "150000"}  # timeout
        )
        try:
            self.client.postPackDataAndGetUnpackRespData(
                "/acct/lp/lgn/sq/v1",
                sqrd,
                3,
                headers=headers,
                access_token=qrcode,
                conn=self.client.issueHttpClient(),
            )
        except Exception as e:
            print(f"[checkQrCodeVerified] {e}")
            return False
        return True

    def verifyCertificate(self, qrcode, cert=None):
        params = [
            [
                12,
                1,
                [
                    [11, 1, qrcode],
                    [11, 2, cert],
                ],
            ],
        ]
        sqrd = self.client.generateDummyProtocol("verifyCertificate", params, 3)
        return self.client.postPackDataAndGetUnpackRespData(
            self.client.LINE_SECONDARY_QR_LOGIN_ENDPOINT, sqrd, 3
        )

    def createPinCode(self, qrcode):
        params = [
            [
                12,
                1,
                [
                    [11, 1, qrcode],
                ],
            ],
        ]
        sqrd = self.client.generateDummyProtocol("createPinCode", params, 3)
        return self.client.postPackDataAndGetUnpackRespData("/acct/lgn/sq/v1", sqrd, 3)

    def checkPinCodeVerified(self, qrcode):
        params = [
            [
                12,
                1,
                [
                    [11, 1, qrcode],
                ],
            ],
        ]
        sqrd = self.client.generateDummyProtocol("checkPinCodeVerified", params, 3)
        headers = self.server.additionalHeaders(
            self.server.Headers, {"x-lst": "150000"}  # timeout
        )
        try:
            self.client.postPackDataAndGetUnpackRespData(
                "/acct/lp/lgn/sq/v1",
                sqrd,
                3,
                headers=headers,
                access_token=qrcode,
                conn=self.client.issueHttpClient(),
            )
        except Exception as e:
            print(f"[checkPinCodeVerified] {e}")
            return False
        return True

    def qrCodeLogin(
        self, authSessionId: str, secret: bytes, autoLoginIsRequired: bool = True
    ):
        params = [
            [
                12,
                1,
                [
                    [11, 1, authSessionId],
                    [11, 2, self.client.SYSTEM_NAME],
                    [2, 3, autoLoginIsRequired],
                ],
            ]
        ]
        sqrd = self.client.generateDummyProtocol("qrCodeLogin", params, 3)
        data = self.client.postPackDataAndGetUnpackRespData("/acct/lgn/sq/v1", sqrd, 3)
        pem = self.client.checkAndGetValue(data, 1, "val_1")
        self.client.saveSqrCert(pem)
        print("證書: ", pem)
        _token = self.client.checkAndGetValue(data, 2, "val_2")
        e2eeInfo = self.client.checkAndGetValue(data, 4, "val_4")
        _mid = self.client.checkAndGetValue(data, 5, "val_5")
        if e2eeInfo is not None:
            self.client.decodeE2EEKeyV1(e2eeInfo, secret, _mid)
        return _token

    def qrCodeLoginV2(
        self,
        authSessionId,
        modelName="彥彥好睡",
        systemName="鴻鴻好暈",
        autoLoginIsRequired=True,
    ):
        params = [
            [
                12,
                1,
                [
                    [11, 1, authSessionId],
                    [11, 2, systemName],
                    [11, 3, modelName],
                    [2, 4, autoLoginIsRequired],
                ],
            ]
        ]
        sqrd = self.client.generateDummyProtocol("qrCodeLoginV2", params, 3)
        return self.client.postPackDataAndGetUnpackRespData("/acct/lgn/sq/v1", sqrd, 3)

    def CPF(self):
        sqrd = []
        return self.client.postPackDataAndGetUnpackRespData("/CPF", sqrd)

    def getRSAKeyInfo(self, provider=1):
        """
        provider:
         - UNKNOWN(0),
         - LINE(1),
         - NAVER_KR(2),
         - LINE_PHONE(3)
        """
        params = [
            [8, 2, provider],
        ]
        sqrd = self.client.generateDummyProtocol("getRSAKeyInfo", params, 3)
        return self.client.postPackDataAndGetUnpackRespData(
            "/api/v3/TalkService.do", sqrd, 3
        )

    def loginV2(
        self,
        keynm,
        encData,
        secret,
        deviceName="Chrome",
        cert=None,
        verifier=None,
        calledName="loginV2",
    ):
        loginType = 2
        if secret is None:
            loginType = 0
        if verifier is not None:
            loginType = 1
        params = [
            [
                12,
                2,
                [
                    [8, 1, loginType],
                    [8, 2, 1],  # provider
                    [11, 3, keynm],
                    [11, 4, encData],
                    [2, 5, 0],
                    [11, 6, ""],
                    [11, 7, deviceName],
                    [11, 8, cert],
                    [11, 9, verifier],
                    [11, 10, secret],
                    [8, 11, 1],
                    [11, 12, "System Product Name"],
                ],
            ]
        ]
        sqrd = self.client.generateDummyProtocol(calledName, params, 3)
        return self.client.postPackDataAndGetUnpackRespData("/api/v3p/rs", sqrd, 3)

    def checkLoginZPinCode(self, accessSession):
        hr = self.server.additionalHeaders(self.server.Headers, {"x-lhm": "GET"})
        r = self.client.postPackDataAndGetUnpackRespData(
            self.client.SECONDARY_DEVICE_LOGIN_VERIFY_PIN,
            [],
            -3,
            headers=hr,
            access_token=accessSession,
            conn=self.client.issueHttpClient(),
        )
        if isinstance(r, dict):
            return r["result"]
        raise EOFError("checkLoginZPinCode resp is not a Dict: {r}")

    def checkLoginV2PinCode(self, accessSession):
        hr = self.server.additionalHeaders(self.server.Headers, {"x-lhm": "GET"})
        r = self.client.postPackDataAndGetUnpackRespData(
            self.client.SECONDARY_DEVICE_LOGIN_VERIFY_PIN_WITH_E2EE,
            [],
            -3,
            headers=hr,
            access_token=accessSession,
            conn=self.client.issueHttpClient(),
        )
        if isinstance(r, dict):
            return r["result"]
        raise EOFError("checkLoginV2PinCode resp is not a Dict: {r}")

    def testTBinary(self):
        METHOD_NAME = "getProfile"
        params = []
        sqrd = self.client.generateDummyProtocol(METHOD_NAME, params, 3)
        res = self.client.postPackDataAndGetUnpackRespData("/S3", sqrd, -1)
        return res

    def testTCompact(self):
        METHOD_NAME = "getProfile"
        params = []
        sqrd = self.client.generateDummyProtocol(METHOD_NAME, params, 4)
        res = self.client.postPackDataAndGetUnpackRespData("/S4", sqrd, -1)
        return res

    def testTMoreCompact(self):
        METHOD_NAME = "getProfile"
        params = []
        sqrd = self.client.generateDummyProtocol(METHOD_NAME, params, 4)
        res = self.client.postPackDataAndGetUnpackRespData("/S5", sqrd, -1)
        return res
