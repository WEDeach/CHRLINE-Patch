from typing import TYPE_CHECKING, Union

import requests

from .base import BaseBIZ

if TYPE_CHECKING:
    from ..client import CHRLINE


class TimelineBiz(BaseBIZ):
    def __init__(self, client: "CHRLINE"):
        super().__init__(client)
        self.__cmsSession: Union[requests.Session, None] = None

    @property
    def domain(self):
        return self.client.LINE_BIZ_TIMELINE_DOMAIN

    @property
    def token(self):
        return self.client.biz.token_with_cms

    @property
    def get_cms_session(self):
        if self.__cmsSession is None:
            return self.init_cms_session()
        return self.__cmsSession

    def init_cms_session(self):
        url = "/api/auth/getSessionByIdToken?idToken=" + self.token
        self.__cmsSession = requests.session()
        res = self.__cmsSession.get(url)
        if res.status_code == 200:
            return self.__cmsSession
        else:
            raise Exception(f"failed to get Cms Session: {res.status_code}")

    def get_cms_user(self):
        url = "/api/cmsUser"
        res = self.get_cms_session.get(url)
        return res.json()

    def get_bot_list(self):
        url = "/api/timeline/v2/bot/list"
        res = self.get_cms_session.get(url)
        return res.json()

    def create_bot(self, displayName, count=100):
        url = "/api/timeline/v2/bot/create"
        data = {
            "displayName": displayName,
            "category": 189,
            "statusMessage": "台灣台灣台灣灣鴻妳好帥台灣台灣台灣台灣",
        }
        headers = {
            "referer": "/liff/liff-account/information-terms",
            "origin": self.domain,
            "user-agent": "Mozilla/5.0 (Linux; Android 9.0.0; SOV38 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Line/12.1.0-dev LIFF",
            "x-botcms-lastclickedelement": "",
            "x-botcms-scriptrevision": "1.0.0-rc",
            "x-requested-with": "jp.naver.line.android",
            "x-xsrf-token": self.get_cms_session.cookies["XSRF-TOKEN"],
            "content-type": "application/json;charset=UTF-8",
        }
        bots = []
        for i in range(count):
            data["displayName"] = f"{displayName} - {i + 1}"
            res = self.get_cms_session.post(url, json=data, headers=headers)
            bots.append(res.json())
        return bots
