# -*- coding: utf-8 -*-
import json
import re
from typing import Optional
from urllib.parse import urlparse

import requests

from ..exceptions import LineServiceException
from .base import BaseHelper


class LiffHelper(BaseHelper):
    def __init__(self):
        self.liff_token_cache = {}

    def sendLiff(
        self,
        to,
        messages,
        tryConsent=True,
        forceIssue=False,
        liffId="1562242036-RW04okm",
    ):
        cache_key = f"{to}"
        use_cache = False
        if cache_key not in self.liff_token_cache or forceIssue:
            try:
                liff = self.client.issueLiffView(to, liffId)
            except LineServiceException as e:
                self.log(f"[sendLiff] issueLiffView error: {e}")
                if e.code == 3 and tryConsent:
                    payload = e.metadata
                    consentRequired = self.client.checkAndGetValue(
                        payload, "consentRequired", 3
                    )
                    channelId = self.client.checkAndGetValue(
                        consentRequired, "channelId", 1
                    )
                    consentUrl = self.client.checkAndGetValue(
                        consentRequired, "consentUrl", 2
                    )
                    toType = self.client.getToType(to)
                    hasConsent = False
                    hasConsent = self.tryConsentLiff(channelId)
                    hasConsent = self.tryConsentAuthorize(consentUrl)
                    if hasConsent:
                        return self.sendLiff(
                            to, messages, tryConsent=False, liffId=liffId
                        )
                raise Exception(f"Failed to send Liff: {to}")
            except Exception as e:
                return e
            token = self.client.checkAndGetValue(liff, "accessToken", 3)
            self.log(f"[sendLiff] issue new token for {cache_key}...")
        else:
            token = self.liff_token_cache[cache_key]
            use_cache = True
            self.log(f"[sendLiff] using cache token for {cache_key}", True)
        liff_headers = {
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Linux; Android 4.4.2; G730-U00 Build/JLS36C) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36 Line/9.8.0",
            "Accept-Encoding": "gzip, deflate",
            "content-Type": "application/json",
            "X-Requested-With": "jp.naver.line.android",
        }
        liff_headers["authorization"] = "Bearer %s" % (token)
        if isinstance(messages, list):
            messages = {"messages": messages}
        else:
            messages = {"messages": [messages]}
        resp = self.client.server.postContent(
            "https://api.line.me/message/v3/share",
            headers=liff_headers,
            data=json.dumps(messages),
        )
        if resp.status_code == 200:
            self.liff_token_cache[cache_key] = token
        elif use_cache:
            return self.sendLiff(to, messages, False, True, liffId)
        return resp.text

    def tryConsentLiff(self, channelId, on=None, referer=None):
        if on is None:
            on = ["P", "CM"]
        payload = {"on": on, "off": []}
        data = json.dumps(payload)
        hr = {
            "X-LINE-ChannelId": str(channelId),
            "X-LINE-Access": self.client.authToken,
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.1; SAMSUNG Realise/DeachSword; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36",
            "Content-Type": "application/json",
            "X-Line-Application": self.client.APP_NAME,
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Language": "zh-TW,en-US;q=0.8",
        }
        if referer is not None:
            hr["referer"] = referer
        r = self.client.server.postContent(
            "https://access.line.me/dialog/api/permissions", data=data, headers=hr
        )
        if r.status_code == 200:
            return True
        print(f"tryConsentLiff failed: {r.status_code}")
        return False

    def tryConsentAuthorize(
        self, consentUrl, allPermission=None, approvedPermission=None
    ):
        if allPermission is None:
            allPermission = ["P", "CM", "OC"]
        if approvedPermission is None:
            approvedPermission = ["P", "CM", "OC"]
        CHANNEL_ID = None
        CSRF_TOKEN = None
        session = requests.session()
        hr = {
            "X-Line-Access": self.client.authToken,
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.1; SAMSUNG Realise/DeachSword; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36",
            "X-Line-Application": self.client.APP_NAME,
        }
        if self.client.APP_TYPE == "IOS":
            hr["User-Agent"] = (
                f"Mozilla/5.0 (iPhone; CPU iPhone OS {self.client.SYSTEM_VER} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari Line/{self.client.APP_VER}"
            )
        r = session.get(consentUrl, headers=hr)
        print(r.text)
        if r.status_code == 200:
            resp = r.text
            # GET CSRF TOKEN
            CHANNEL_ID = re.findall(self.client.CONSENT_CHANNEL_ID_REGEX, resp)[0]
            CSRF_TOKEN = re.findall(self.client.CONSENT_CSRF_TOKEN_REGEX, resp)[0]
            self.log(f"CHANNEL_ID: {CHANNEL_ID}")
            self.log(f"CSRF_TOKEN: {CSRF_TOKEN}")
        if CHANNEL_ID and CSRF_TOKEN:
            url = "https://access.line.me/oauth2/v2.1/authorize/consent"
            patch_url = urlparse(consentUrl)._replace(query="").geturl()
            if url != patch_url:
                self.log(f"Using `{patch_url}` to authorize...")
                url = patch_url
            payload = {
                "allPermission": allPermission,
                "approvedPermission": allPermission,
                "channelId": CHANNEL_ID,
                "__csrf": CSRF_TOKEN,
                "__WLS": "",
                "addFriendMode": "ALREADY_FRIENDED_MODE",
                "addFriend": "true",
                "allow": "true",
            }
            r = session.post(url, data=payload, headers=hr)
            if r.status_code == 200:
                print(r.text)
                return True
            print(f"tryConsentAuthorize failed: {r.status_code}")
        else:
            raise Exception(
                f"tryConsentAuthorize failed: STATUS_CODE: {r.status_code}, CHANNEL_ID: {CHANNEL_ID}, CSRF_TOKEN: {CSRF_TOKEN}"
            )
        return False

    def getAccessToken(self, client_id, redirect_uri, otp, code):
        data = {
            "client_id": str(client_id),  # channel id
            # intent://result#Intent;package=xxx;scheme=lineauth;end",
            "redirect_uri": redirect_uri,
            "otp": otp,  # len 20
            "code": code,  # len 20
            "grant_type": "authorization_code",
        }
        hr = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.1; SAMSUNG Realise/DeachSword; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36",
        }
        r = self.client.server.postContent(
            "https://access.line.me/v2/oauth/accessToken", data=data, headers=hr
        )
        return r.json()["access_token"]

    def getLiffOtt(self, liffId: str, liffAccessToken: str):
        url = f"https://api.line.me/liff/v2/apps/{liffId}/ott"
        hr = {"Authorization": f"Bearer {liffAccessToken}"}
        r = self.client.server.getContent(url, headers=hr)
        return r.json()["ott"]

    def getLiffShareTargetPickerPage(self, liffId: str, ott: str, liffAccessToken: str):
        url = f"https://access.line.me/oauth2/v2.1/liff/shareTargetPicker?liffId={liffId}&ott={ott}"
        hr = {"Authorization": f"Bearer {liffAccessToken}"}
        r = self.client.server.getContent(url, headers=hr)
        return r.text

    def getLiffShareTargetPickerFriendList(
        self,
        liffAccessToken: str,
        csrfToken: str,
        pageToken: Optional[str] = None,
        displayCount: int = 200,
        fetchType="friends",
    ):
        url = f"https://access.line.me/oauth2/v2.1/liff/shareTargetPicker/{fetchType}?pageToken={pageToken}&__csrf={csrfToken}&display={displayCount}"

        # TODO: patch cookies.

        hr = {"Authorization": f"Bearer {liffAccessToken}"}
        r = self.client.server.getContent(url, headers=hr)
        return r.text
