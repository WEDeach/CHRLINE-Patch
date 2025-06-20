# -*- coding: utf-8 -*-
import os
import re
from typing import Optional


class Config(object):
    LINE_HOST_DOMAIN = os.getenv("LINE_HOST_DOMAIN", "http://localhost:8111")
    LINE_OBS_DOMAIN = os.getenv("LINE_OBS_DOMAIN", "http://localhost:8112")
    LINE_API_DOMAIN = os.getenv("LINE_API_DOMAIN", "http://localhost:8113")
    LINE_ACCESS_DOMAIN = os.getenv("LINE_ACCESS_DOMAIN", "http://localhost:8114")

    LINE_BIZ_TIMELINE_DOMAIN = os.getenv(
        "LINE_BIZ_TIMELINE_DOMAIN", "http://localhost:8121"
    )

    LINE_ENCRYPTION_ENDPOINT = "/enc"
    LINE_AGE_CHECK_ENDPOINT = "/ACS4"
    LINE_AUTH_ENDPOINT = "/RS3"
    LINE_AUTH_ENDPOINT_V4 = "/RS4"
    LINE_AUTH_EAP_ENDPOINT = "/ACCT/authfactor/eap/v1"
    LINE_BEACON_ENDPOINT = "/BEACON4"
    LINE_BUDDY_ENDPOINT = "/BUDDY3"
    LINE_CALL_ENDPOINT = "/V3"
    LINE_CANCEL_LONGPOLLING_ENDPOINT = "/CP4"
    LINE_CHANNEL_ENDPOINT = "/CH3"
    LINE_CHANNEL_ENDPOINT_V4 = "/CH4"
    LINE_PERSONAL_ENDPOINT_V4 = "/PS4"
    LINE_CHAT_APP_ENDPOINT = "/CAPP1"
    LINE_COIN_ENDPOINT = "/COIN4"
    LINE_COMPACT_E2EE_MESSAGE_ENDPOINT = "/ECA5"
    LINE_COMPACT_MESSAGE_ENDPOINT = "/C5"
    LINE_COMPACT_PLAIN_MESSAGE_ENDPOINT = "/CA5"
    LINE_CONN_INFO_ENDPOINT = "/R2"
    LINE_EXTERNAL_INTERLOCK_ENDPOINT = "/EIS4"
    LINE_IOT_ENDPOINT = "/IOT1"
    LINE_LIFF_ENDPOINT = "/LIFF1"
    LINE_NORMAL_ENDPOINT = "/S3"
    LINE_SECONDARY_QR_LOGIN_ENDPOINT = "/acct/lgn/sq/v1"
    LINE_SHOP_ENDPOINT = "/SHOP3"
    LINE_SHOP_AUTH_ENDPOINT = "/SHOPA"
    LINE_SNS_ADAPTER_ENDPOINT = "/SA4"
    LINE_SNS_ADAPTER_REGISTRATION_ENDPOINT = "/api/v4p/sa"
    LINE_SQUARE_ENDPOINT = "/SQ1"
    LINE_SQUARE_BOT_ENDPOINT = "/BP1"
    LINE_UNIFIED_SHOP_ENDPOINT = "/TSHOP4"
    LINE_WALLET_ENDPOINT = "/WALLET4"
    LINE_SECONDARY_PWLESS_LOGIN_ENDPOINT = "/acct/lgn/secpwless/v1"
    LINE_SECONDARY_PWLESS_LOGIN_PERMIT_ENDPOINT = "/acct/lp/lgn/secpwless/v1"
    LINE_SECONDARY_AUTH_FACTOR_PIN_CODE_ENDPOINT = "/acct/authfactor/second/pincode/v1"
    LINE_PWLESS_CREDENTIAL_MANAGEMENT_ENDPOINT = "/acct/authfactor/pwless/manage/v1"
    LINE_PWLESS_PRIMARY_REGISTRATION_ENDPOINT = "/ACCT/authfactor/pwless/v1"
    LINE_VOIP_GROUP_CALL_YOUTUBE_ENDPOINT = "/EXT/groupcall/youtube-api"
    LINE_E2EE_KEY_BACKUP_ENDPOINT = "/EKBS4"
    SECONDARY_DEVICE_LOGIN_VERIFY_PIN_WITH_E2EE = "/LF1"
    SECONDARY_DEVICE_LOGIN_VERIFY_PIN = "/Q"
    LINE_NOTIFY_SLEEP_ENDPOINT = "/F4"

    LINE_LANGUAGE = "zh-Hant_TW"
    LINE_SERVICE_REGION = "TW"

    APP_TYPE = "CHROMEOS"
    APP_VER = "11.19.2"
    SYSTEM_NAME = "DeachSword"
    SYSTEM_VER = "12.1.4"
    IP_ADDR = "8.8.8.8"
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    CONSENT_CHANNEL_ID_REGEX = re.compile(
        r"<input type=\"hidden\" name=\"channelId\" value=\"([^\"]+)\""
    )
    CONSENT_CSRF_TOKEN_REGEX = re.compile(
        r"<input type=\"hidden\" name=\"__csrf\" id=\"__csrf\" value=\"([^\"]+)\""
    )

    TOKEN_V3_SUPPORT = ["DESKTOPWIN", "DESKTOPMAC", "CHROMEOS"]
    SYNC_SUPPORT = ["IOS", "IOSIPAD", "ANDROID", "CHROMEOS", "DESKTOPWIN", "DESKTOPMAC"]
    USERDOMAIN = "KORONE-MY-WAIFU"
    SYSTEM_MODEL = "System Product Name"
    MODEL_NAME = "System Product Name"

    def __init__(
        self,
        type: str,
        app_version: Optional[str],
        os_name: Optional[str],
        os_version: Optional[str],
        os_model: Optional[str],
        *,
        support_v3_token: Optional[bool] = None,
        support_sync: Optional[bool] = None,
    ):
        self.APP_NAME = None
        self.DEVICE_TYPE = type
        self.isSecondary = False
        if type == "DESKTOPWIN":
            self.APP_VER = "9.8.0.3597"
            self.SYSTEM_NAME = "WINDOWS"
            self.SYSTEM_VER = "10.0.0-NT-x64"
            self.SYSTEM_MODEL = self.USERDOMAIN
        elif type == "DESKTOPMAC":
            self.APP_VER = "8.1.1.3145"
            self.SYSTEM_NAME = "MAC"
            self.SYSTEM_MODEL = self.USERDOMAIN
        elif type == "CHROMEOS":
            # if you got timeout, just mean version too low.
            # DON'T ask more.
            self.APP_VER = "3.1.0"
            self.SYSTEM_NAME = "Chrome_OS"  # for TokenV3.1
            self.SYSTEM_VER = "1"
            self.USERDOMAIN = "CHROMEOS"
            self.SYSTEM_MODEL = "Chrome" if True else "Whale"
            self.MODEL_NAME = "CHROME"
        # elif type == "ANDROIDLITE":
        # self.APP_VER = "2.17.1"
        # self.SYSTEM_NAME = "Android OS"
        # self.isSecondary = True
        elif type in ["ANDROID", "ANDROIDSECONDARY"]:
            self.APP_VER = "13.4.1"
            self.SYSTEM_NAME = "Android OS"
        elif type == "IOS":
            self.APP_VER = "13.11.0"
            self.SYSTEM_NAME = "iOS"
        elif type == "IOSIPAD":
            self.APP_VER = "13.11.0"
            self.SYSTEM_NAME = "iPadOS"
            self.SYSTEM_MODEL = "iPad5,1"
        elif type == "WATCHOS":
            self.APP_VER = "13.11.0"
            self.SYSTEM_NAME = "Watch OS"
        elif type == "WEAROS":
            self.APP_VER = "1.4.1"
            self.SYSTEM_NAME = "Wear OS"
        elif type == "OPENCHAT_PLUS":
            pass
        elif type == "CHANNELGW":
            pass
        elif type == "CHANNELCP":
            pass
        elif type == "CLOVAFRIENDS":
            pass
        elif type == "BOT":
            pass
        elif type == "WAP":
            pass
        elif type == "WEB":
            pass
        elif type == "BIZWEB":
            pass
        elif type == "DUMMYPRIMARY":
            pass
        elif type == "SQUARE":
            pass
        elif type == "FIREFOXOS":
            pass
        elif type == "TIZEN":
            pass
        elif type == "VIRTUAL":
            pass
        elif type == "CHRONO":
            pass
        elif type == "WINMETRO":
            pass
        elif type == "S40":
            pass
        elif type == "WINPHONE":
            pass
        elif type == "BLACKBERRY":
            pass
        elif type == "INTERNAL":
            pass
        elif type == "VISIONOS":
            self.APP_VER = ""
            self.SYSTEM_NAME = "visionOS"
            self.SYSTEM_MODEL = "RealityDevice14,1"
        elif app_version and os_name and os_version:
            self.APP_VER = app_version
            self.SYSTEM_NAME = os_name
            self.SYSTEM_VER = os_version
        else:
            raise Exception(f"You need to specify `app_version`, `os_name` and `os_version` to use this device type: {type}")
        self.APP_TYPE = type
        self.USER_AGENT = "Line/%s" % self.APP_VER
        if support_v3_token is not None:
            if support_v3_token and type not in self.TOKEN_V3_SUPPORT:
                self.TOKEN_V3_SUPPORT.append(type)
            elif type in self.TOKEN_V3_SUPPORT:
                self.TOKEN_V3_SUPPORT.remove(type)
        if support_sync is not None:
            if support_sync and type not in self.SYNC_SUPPORT:
                self.SYNC_SUPPORT.append(type)
            elif type in self.SYNC_SUPPORT:
                self.SYNC_SUPPORT.remove(type)
        self.initAppConfig(type, app_version, os_name, os_version, os_model)
        self.reloadDomains()

    def initAppConfig(
        self,
        app_type: Optional[str],
        app_version: Optional[str],
        os_name: Optional[str],
        os_version: Optional[str],
        os_model: Optional[str],
    ):
        """Init app config."""
        self.APP_TYPE = "CHROMEOS"
        if app_type is not None:
            self.APP_TYPE = app_type
        if app_version is not None:
            self.APP_VER = app_version
        if os_name is not None:
            self.SYSTEM_NAME = os_name
        if os_version is not None:
            self.SYSTEM_VER = os_version
        if os_model is not None:
            self.SYSTEM_MODEL = os_model
        self.APP_NAME = "%s\t%s\t%s\t%s" % (
            self.APP_TYPE,
            self.APP_VER,
            self.SYSTEM_NAME,
            self.SYSTEM_VER,
        )
        if self.isSecondary:
            self.APP_NAME += ";SECONDARY"

    @property
    def LineUserAgent(self):
        if self.APP_TYPE == "CHROMEOS":
            self.USER_AGENT = "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        elif self.APP_TYPE in ["DESKTOPWIN", "DESKTOPMAC"]:
            _desktop = "MAC"
            if self.APP_TYPE == "DESKTOPWIN":
                _desktop = "WINDOWS"
            self.USER_AGENT = f"DESKTOP:{_desktop}:{self.SYSTEM_NAME}({self.APP_VER})"
        else:
            self.USER_AGENT = (
                f"Line/{self.APP_VER} {self.SYSTEM_MODEL} {self.SYSTEM_VER}"
            )
        return self.USER_AGENT

    def reloadDomains(self):
        self.LINE_HOST_DOMAIN = os.getenv("LINE_HOST_DOMAIN", "http://localhost:8111")
        self.LINE_OBS_DOMAIN = os.getenv("LINE_OBS_DOMAIN", "http://localhost:8112")
        self.LINE_API_DOMAIN = os.getenv("LINE_API_DOMAIN", "http://localhost:8113")
        self.LINE_ACCESS_DOMAIN = os.getenv(
            "LINE_ACCESS_DOMAIN", "http://localhost:8114"
        )
        self.LINE_BIZ_TIMELINE_DOMAIN = os.getenv(
            "LINE_BIZ_TIMELINE_DOMAIN", "http://localhost:8121"
        )
