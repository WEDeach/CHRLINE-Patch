import base64
import binascii
import glob
import json
import os
import ssl
import struct
import sys
import time
from base64 import b64encode
from hashlib import md5
from importlib.util import module_from_spec, spec_from_file_location
from typing import Any, Optional, Union
from urllib.parse import quote

import axolotl_curve25519 as curve
import Crypto.Cipher.PKCS1_OAEP as rsaenc
import httpx
import requests
import xxhash
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad

from thrift.protocol.TCompactProtocol import TCompactProtocol as tcProtocol
from thrift.transport.TTransport import TMemoryBuffer

from .exceptions import E2EESelfKeyNotFoundException, LineServiceException
from .helper import ChrHelperProtocol
from .serializers.DummyProtocol import (
    DummyProtocol,
    DummyProtocolData,
    DummyProtocolSerializer,
    DummyThrift,
)
from .services.thrift.ttypes import TalkException
from .utils.patchs import p_patch_all


class Models(ChrHelperProtocol):
    def __init__(self, savePath):
        self.savePath = savePath or os.path.dirname(os.path.realpath(__file__))
        self.lcsStart = "0005"
        self.le = "18"
        self.PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0LRokSkGDo8G5ObFfyKiIdPAU5iOpj+UT+A3AcDxLuePyDt8IVp9HpOsJlf8uVk3Wr9fs+8y7cnF3WiY6Ro526hy3fbWR4HiD0FaIRCOTbgRlsoGNC2rthp2uxYad5up78krSDXNKBab8t1PteCmOq84TpDCRmainaZQN9QxzaSvYWUICVv27Kk97y2j3LS3H64NCqjS88XacAieivELfMr6rT2GutRshKeNSZOUR3YROV4THa77USBQwRI7ZZTe6GUFazpocTN58QY8jFYODzfhdyoiym6rXJNNnUKatiSC/hmzdpX8/h4Y98KaGAZaatLAgPMRCe582q4JwHg7rwIDAQAB\n-----END PUBLIC KEY-----"
        self.key = RSA.importKey(self.PUBLIC_KEY)
        self.encryptKey = os.urandom(16)
        self.IV = bytes(
            [78, 9, 72, 62, 56, 245, 255, 114, 128, 18, 123, 158, 251, 92, 45, 51]
        )
        self.cipher = AES.new(self.encryptKey, AES.MODE_CBC, iv=self.IV)
        self.d_cipher = AES.new(self.encryptKey, AES.MODE_CBC, iv=self.IV)
        self.encEncKey()
        # self.initWithBiz()
        # self.initWithAndroid(4)
        self.__logger = self.client.logger.new("MODEL")

        # Init 3rd Models
        from .dyher.connManager import ConnManager

        p_patch_all()

        self.legyPushers = ConnManager(self.client)

    def getSavePath(self, dirname: str):
        savePath = os.path.join(self.savePath, dirname)
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        return savePath

    def genOBSParams(self, newList, returnAs="json", ext="jpg"):
        oldList = {"name": f"CHRLINE-{int(time.time())}.{ext}", "ver": "1.0"}
        if returnAs not in ["json", "b64", "default"]:
            raise Exception("Invalid parameter returnAs")
        oldList.update(newList)
        if "range" in oldList:
            new_range = "bytes 0-%s\/%s" % (
                str(int(oldList["range"]) - 1),
                str(oldList["range"]),
            )
            oldList.update({"range": new_range})
        if returnAs == "json":
            oldList = json.dumps(oldList)
            return oldList
        elif returnAs == "b64":
            oldList = json.dumps(oldList)
            return b64encode(oldList.encode("utf-8"))
        elif returnAs == "default":
            return oldList

    def checkNextToken(self, log4NotDebug: bool = True):
        savePath = self.getSavePath(".tokens")
        fn = md5(self.authToken.encode()).hexdigest()
        old = self.authToken
        if os.path.exists(savePath + f"/{fn}"):
            self.authToken = open(savePath + f"/{fn}", "r").read()
            if old != self.authToken:
                self.client.log(f"New Token: {self.authToken}", not log4NotDebug)
                self.checkNextToken(log4NotDebug)
        return self.authToken

    def handleNextToken(self, newToken):
        savePath = self.getSavePath(".tokens")
        fn = md5(self.authToken.encode()).hexdigest()
        open(savePath + f"/{fn}", "w").write(newToken)
        self.authToken = newToken
        self.client.log(f"New Token: {newToken}")
        self.client.biz.renew_tokens()

    def tryRefreshToken(self):
        """Try to refresh token."""
        refreshToken = self.getCacheData(".refreshToken", self.authToken)
        self.client.log(f"try to refresh access token... {refreshToken}")
        if refreshToken is not None:
            RATR = self.client.refreshAccessToken(refreshToken)
            token = self.client.checkAndGetValue(RATR, "accessToken", 1)
            # refreshToken = self.checkAndGetValue(RATR, 'refreshToken', 5)
            self.handleNextToken(token)
            self.saveCacheData(".refreshToken", token, refreshToken)
        else:
            raise ValueError("RefreshToken missing.")
        return True

    def getCustomData(self):
        savePath = self.getSavePath(".data")
        fn = md5(self.client.customDataId.encode()).hexdigest()
        if os.path.exists(savePath + f"/{fn}"):
            self.custom_data = json.loads(open(savePath + f"/{fn}", "r").read())
        self.client.log(f"Loading Custom Data: {fn}")
        return True

    def saveCustomData(self):
        savePath = self.getSavePath(".data")
        fn = md5(self.client.customDataId.encode()).hexdigest()
        open(savePath + f"/{fn}", "w").write(json.dumps(self.custom_data))
        return True

    def getSqrCert(self):
        savePath = self.getSavePath(".data")
        fn = "cert.pem"
        if os.path.exists(savePath + f"/{fn}"):
            return open(savePath + f"/{fn}", "r").read()
        return None

    def saveSqrCert(self, cert):
        savePath = self.getSavePath(".data")
        fn = "cert.pem"
        open(savePath + f"/{fn}", "w").write(cert)
        return True

    def getEmailCert(self, email):
        savePath = self.getSavePath(".data")
        fn = f"{email}.crt"
        if os.path.exists(savePath + f"/{fn}"):
            return open(savePath + f"/{fn}", "r").read()
        return None

    def saveEmailCert(self, email, cert):
        savePath = self.getSavePath(".data")
        fn = f"{email}.crt"
        open(savePath + f"/{fn}", "w").write(cert)
        return True

    def initWithAndroid(self, ver=7):
        if ver == 1:
            self.lcsStart = "0001"
            self.le = "1"
            self.PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCZAAoZNRwIlLUXaUgrgYi8bAYq\nQeFVtXvCNIEm+F4/jAyTU3YoDwmoLaKQ6itGOonykGtwy2k/3BeWefL/q5eUGjVG\nBEa1vBeUNEb4IFU8n9WK3N/GIIPuD6ZiusB+U1FPg/NaEiVX8ldmEQJgmuG1hykk\n2dU3oy7O1M+Kwl1lJQIDAQAB\n-----END PUBLIC KEY-----"
        elif ver == 4:
            self.lcsStart = "0004"
            self.le = "7"  # LegyEncHelper.cpp::decryptStream -> legy xle value
            self.PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwpAwTVluR1Z++tVzxtOD\nr7XxSv6oqrwvj/8c8SkfFsS8zM7CvIT8j+x+6Qs1JjNRDtYjAwPKO3tO+qOAdA+8\n7FHpx0THDJIi4VYxSZ2uDh0U8Luxh02whwM8gPbPQNN3sEd5++kJ3cCh5eeAIiUd\nDrwPhHzxO8swpBRdxJB/pzibEqpG2U2764JlPscN9D896qmBN6CBRKpXk/MmUDAI\n4xg+uQk/ykn3SNXJSgQwI1UD9KuiR+X9tbJlKRMN5JpUrSuEwRPQQDMaWpSIdCJM\noFqJLNwt9b1RR/JEB01Eup+3QCub20/CObCmHZY6G26KTDHLoTRZ1xzymdYhdJ43\nCwIDAQAB\n-----END PUBLIC KEY-----"
        elif ver == 6:
            self.lcsStart = "0007"
            self.le = "7"
            self.PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5ABzJbexh+HH1+RzVTH4\nDFj8b/42vRqUp0NWLIBAgi5+bAgeJYzyVBI7Pk6YkQnd44HPvUvFMF3V3TocRXLP\nZV/NSawgcAh+VrXe3VIlruCOe14qrd/ZMpTRTxtBJ5aRpVhTsnGpZtGggPYnPh4c\n6V/R7Wxymj4SBZ1Ipsa7ZI83z/XIPFXT38qTJN3UAW5YhjQon1eNbwaxALVajuvI\npUE52aIBi05gE/V0HEoOUjfOg1V6RHFbcchTgmcze6Vbye+7kmdsIboDXnNpm/fJ\nuItub+iwLKSWf9OPc/bYpU4YVBxZXzmSCXFMLeCe2i5wJeMg4iG8NpVpwVv2W+Hb\nQQIDAQAB\n-----END PUBLIC KEY-----"
        elif ver == 7:
            self.lcsStart = "0008"
            self.le = "7"
            self.PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsMC6HAYeMq4R59e2yRw6\nW1OWT2t9aepiAp4fbSCXzRj7A29BOAFAvKlzAub4oxN13Nt8dbcB+ICAufyDnN5N\nd3+vXgDxEXZ/sx2/wuFbC3B3evSNKR4hKcs80suRs8aL6EeWi+bAU2oYIc78Bbqh\nNzx0WCzZSJbMBFw1VlsU/HQ/XdiUufopl5QSa0S246XXmwJmmXRO0v7bNvrxaNV0\ncbviGkOvTlBt1+RerIFHMTw3SwLDnCOolTz3CuE5V2OrPZCmC0nlmPRzwUfxoxxs\n/6qFdpZNoORH/s5mQenSyqPkmH8TBOlHJWPH3eN1k6aZIlK5S54mcUb/oNRRq9wD\n1wIDAQAB\n-----END PUBLIC KEY-----"
        self.key = RSA.importKey(self.PUBLIC_KEY)
        self.IV = bytes(
            [78, 9, 72, 62, 56, 245, 255, 114, 128, 18, 123, 158, 251, 92, 45, 51]
        )
        self.encryptKey = b"DearSakura+2021/"
        self.encEncKey()

    def encHeaders(self, headers):
        t = headers.keys()
        data = []
        self.mFhrnmxnNF(len(t), data)
        for i in t:
            self.mFhrnmxnNF(len(i), data)
            self.wYEpEYldst(i, data)
            self.mFhrnmxnNF(len(headers[i]), data)
            self.wYEpEYldst(headers[i], data)
        o = len(data)
        data = [255 & o] + data
        data = [255 & o >> 8] + data
        return data

    def decHeaders(self, data):
        headers = {}
        tbin = self.client.TBinaryProtocol(self)
        tbin.data = data
        dataLen = tbin.readI16() + 2
        headerLen = tbin.readI16()
        for _ in range(headerLen):
            size = tbin.readI16()
            _k = tbin.y(size).decode()
            size = tbin.readI16()
            _v = tbin.y(size).decode()
            headers[_k] = _v
        return headers, data[dataLen:]

    def encEncKey(self):
        # heh
        a = rsaenc.new(self.key)
        self._encryptKey = (
            self.lcsStart + b64encode(a.encrypt(self.encryptKey)).decode()
        )

    def encData(self, data):
        _data = AES.new(self.encryptKey, AES.MODE_CBC, iv=self.IV).encrypt(
            pad(data, AES.block_size)
        )
        debug = []
        return _data

    def decData(self, data):
        data = pad(data, AES.block_size)
        _data = AES.new(self.encryptKey, AES.MODE_CBC, iv=self.IV).decrypt(data)[:-16]
        _data = unpad(_data, AES.block_size)
        i = 1
        data = self.yVdzCLDwMN(_data, i)
        i = 3
        return _data

    def mFhrnmxnNF(self, t, e):
        i = 65536
        if t < -1 * 32768 or t >= i:
            raise Exception(t + " is incorrect for i16.")
        e.append(255 & t >> 8)
        e.append(255 & t)

    def wYEpEYldst(self, t, e):
        for i in range(len(t)):
            e.append(ord(t[i]))

    def xZVpUuXFru(self, t):
        if 8 == len(t):
            return t
        e = ""
        i = 0
        n = 8 - len(t)
        while i < n:
            e += "0"
            i += 1
        return e + t

    def pmAWhahfKx(self, t):
        e = []
        i = 0
        n = len(t)
        while i < n:
            _i = 0
            try:
                _i = int(t[i : i + 2], 16)
            except:
                _i = 16
            e.append(_i)
            i += 2
        return e

    def XQqwlHlXKK(self, e, i):
        r = []
        for o in range(16):
            r.append(92 ^ e[o])
        n = xxhash.xxh32(b"", seed=0)
        s = xxhash.xxh32(b"", seed=0)
        n.update(bytes(r))
        for o in range(16):
            r[o] ^= 106
        s.update(bytes(r))
        s.update(i)
        a = s.hexdigest()  # is b8a7c677?
        n.update(bytes(self.pmAWhahfKx(a)))
        c = n.hexdigest()  # is 3f97d2f6?
        d = self.pmAWhahfKx(c)
        return bytes(d)

    def yVdzCLDwMN(self, d, i):
        return (255 & self.xnEmbaRWhy(d, i)) << 8 | 255 & self.xnEmbaRWhy(d, i + 1)

    def xnEmbaRWhy(self, d, i):
        t = d[i]
        if t > 127:
            t = 0 - (t - 1 ^ 255)
        return t

    def generateDummyProtocol(
        self, name: str, params: list, _type: int
    ) -> DummyProtocolSerializer:
        return DummyProtocolSerializer(self, name, params, _type)

    def generateDummyProtocol2(
        self, params: DummyProtocol, proto: int = 3, fixSuccessHeaders: bool = False
    ):
        newParams = []
        d = params.data
        if d is not None:
            newParams.append(thrift2dummy(d))
        return bytes(self.generateDummyProtocolField(newParams, proto) + [0])

    def generateDummyProtocolField(self, params, proto):
        isCompact = False
        data = []
        tcp = self.client.TCompactProtocol(self)
        for param in params:
            # [10, 2, revision]
            _type = param[0]
            _id = param[1]
            _data = param[2]
            if _data is None:
                continue
            if _type == 12 and isinstance(_data, DummyThrift):
                # only for structs
                _data = _data.dd_slist()
            if _type == 13:
                if _data[2] is None:
                    continue
            elif _type in [14, 15]:
                if _data[1] is None:
                    continue
            if proto == 3:
                data += [_type, 0, _id]
                isCompact = False
            elif proto == 4:
                if _type == 2:
                    data += tcp.getFieldHeader(0x01 if _data else 0x02, _id)
                    continue
                data += tcp.getFieldHeader(tcp.CTYPES[_type], _id)
                isCompact = True
            data += self.generateDummyProtocolData(_data, _type, isCompact)
        return data

    def generateDummyProtocolData(self, _data, ttype, isCompact=False):
        data = []
        tbp = self.client.TBinaryProtocol(self)
        tcp = self.client.TCompactProtocol(self)
        proto = 4 if isCompact else 3
        if ttype == 2:
            if isCompact:
                # CONTAINER_WRITE
                data += tcp.writeByte(0x01 if _data else 0x02)
            else:
                data += [1] if _data is True else [0]
        elif ttype == 3:
            if isCompact:
                data += tcp.writeByte(_data)
            else:
                data += tbp.writeByte(_data)
        elif ttype == 4:
            data = self.getFloatBytes(_data, isCompact=isCompact)
        elif ttype == 8:
            data += self.getIntBytes(_data, isCompact=isCompact)
        elif ttype == 10:
            data += self.getIntBytes(_data, 8, isCompact=isCompact)
        elif ttype == 11:
            data += self.getStringBytes(_data, isCompact=isCompact)
        elif ttype == 12:
            if isinstance(_data, DummyProtocolData):
                _data = thrift2dummy(_data)
            data += self.generateDummyProtocolField(_data, proto) + [0]
        elif ttype == 13:
            _ktype = _data[0]
            _vtype = _data[1]
            _vdata = _data[2]
            if isCompact:
                data += tcp.writeMapBegin(_ktype, _vtype, len(_vdata))
            else:
                data += [_ktype, _vtype] + self.getIntBytes(
                    len(_vdata), isCompact=isCompact
                )
            for vd in _vdata:
                data += self.generateDummyProtocolData(vd, _ktype, isCompact)
                data += self.generateDummyProtocolData(_vdata[vd], _vtype, isCompact)
        elif ttype == 14 or ttype == 15:
            # [11, targetUserMids]
            _vtype = _data[0]
            _vdata = _data[1]
            if isCompact:
                data += tcp.writeCollectionBegin(_vtype, len(_vdata))
            else:
                data += [_vtype] + self.getIntBytes(len(_vdata), isCompact=isCompact)
            for vd in _vdata:
                data += self.generateDummyProtocolData(vd, _vtype, isCompact)
        else:
            raise Exception(f"[generateDummyProtocolData] not support type: {type}")
        return data

    def postPackDataAndGetUnpackRespData(
        self,
        path: str,
        bdata: Union[bytes, DummyProtocolSerializer, list, dict],
        ttype: int = 3,
        encType: Optional[int] = None,
        headers: Optional[dict] = None,
        access_token: Optional[str] = None,
        baseException: Optional[dict] = None,
        readWith: Optional[str] = None,
        conn: Optional[Any] = None,
        files: Optional[dict] = None,
        expectedRespCode: Optional[list] = None,
        timeout: Optional[int] = None,
    ):
        logger = self.__logger.overload("GATE")
        if expectedRespCode is None:
            expectedRespCode = [200]
        if headers is None:
            headers = self.client.server.Headers.copy()
        if access_token is None:
            access_token = self.authToken
        ptype = "TBINARY" if ttype == 3 else "TCOMPACT"
        if ttype in [1, 2, 3, 4, 5]:
            headers["content-type"] = "application/x-thrift; protocol=" + ptype
            # headers["accept"] = "application/x-thrift"
            if isinstance(bdata, DummyProtocolSerializer):
                # Import DummyProtocolSerializer in v2.5.3,
                # it can be change the protocol type.
                if self.client.force_tmore:
                    # Force TMoreCompact
                    if path in [self.client.LINE_NORMAL_ENDPOINT, "/S4"]:
                        path = "/S5"
                        ttype = 5
                else:
                    # 2023/07/21 PATCH.
                    # on new version || CHROMEOS
                    # bin protocol will got timeout and respone None.
                    if path == self.client.LINE_NORMAL_ENDPOINT:
                        ttype = 4
                        path = "/S4"

                bdata.protocol = ttype
        headers["x-lal"] = self.client.LINE_LANGUAGE
        if encType is None:
            encType = self.client.encType

        # 2022/08/24 PATCH
        if self.client.DEVICE_TYPE == "CHROMEOS":
            headers["origin"] = "chrome-extension://ophjlpahpchlmihnnnihgmmeilfjmjjc"
        data = bdata
        if type(data) in [DummyProtocolSerializer, list]:
            data = bdata = bytes(bdata)
        elif not isinstance(bdata, bytes):
            bdata = str(bdata).encode()
        self.client.log("----------------- START POST", True)
        self.client.log(
            f"--> POST {path} {f'({self.client.LINE_ENCRYPTION_ENDPOINT})' if encType == 1 else ''}",
            True,
        )
        self.client.log(
            f"--> {bdata.hex()}",
            True,
        )
        if encType == 0:
            if conn is None:
                conn = self.client.req_h2
            if "x-le" in headers:
                del headers["x-le"]
                del headers["x-lcs"]
            if access_token is not None:
                headers["X-Line-Access"] = access_token
            self.client.log(f"--> Headers: {headers}", True)
            res = doLoopReq(
                conn.post,
                {
                    "url": self.client.LINE_HOST_DOMAIN + path,
                    "data": data,
                    "headers": headers,
                    "files": files,
                    "timeout": timeout,
                },
            )
            data = res.content
        elif encType == 1:
            if conn is None:
                conn = self.client.req
            if access_token is not None:
                _headers = {"x-lt": access_token, "x-lpqs": path}
            else:
                _headers = {"x-lpqs": path}
            a = self.encHeaders(_headers)
            _data = bytes(a) + bytes(bdata)
            fix_bytes = False
            if (int(self.le) & 4) == 4:
                _data = bytes([int(self.le)]) + _data
                fix_bytes = True
            if (int(self.le) & 2) != 2:
                data = self.encData(_data)
            else:
                data = self.encData(_data)
                data += self.XQqwlHlXKK(self.encryptKey, data)
            headers["accept-encoding"] = "gzip, deflate"
            self.client.log(f"--> Headers: {headers} ({_headers})", True)
            res = doLoopReq(
                conn.post,
                {
                    "url": self.client.LINE_HOST_DOMAIN
                    + self.client.LINE_ENCRYPTION_ENDPOINT,
                    "data": data,
                    "files": files,
                    "headers": headers,
                    "timeout": timeout,
                },
            )
            if res.content:
                data = self.decData(res.content)
            else:
                data = res.content
            if fix_bytes:
                data = data[1:]
        else:
            raise Exception(f"Unknown encType: {encType}")
        self.client.log(f"<--  {res.status_code}", True)
        self.client.log(f"{data.hex()}", True)
        if res.status_code in expectedRespCode:
            if (
                res.headers.get("x-lc") is not None
                and int(res.headers["x-lc"]) not in expectedRespCode
            ):
                raise Exception(f'Invalid response code: {res.headers["x-lc"]}')
            if encType == 1:
                respHeaders, data = self.decHeaders(data)
            else:
                respHeaders = {}
            respHeaders.update(res.headers)
            self.client.log(f"RespHraders: {respHeaders}", True)
            for _rh in respHeaders:
                _rht = str(_rh)
                if _rht == "x-line-next-access":
                    self.handleNextToken(respHeaders[_rh])
                elif _rht.startswith("x-"):
                    if _rht not in [
                        "x-ls",
                        "x-lc",
                        "x-le",
                        "x-line-http",
                        "x-lcr",
                        "x-lts",
                        "x-obs-oid",
                        "x-obs-hash",
                        "x-obs-debug-object-location",
                        "x-obs-debug-id",
                        "x-obs-content-type",
                        # "x-line-next-access-max-age",
                    ]:
                        self.client.log(
                            f"[HTTP] unhandled header:  {_rht} => {respHeaders[_rh]}"
                        )
            # x-line-access-refresh-required
            conn_res = res
            res = None
            if ttype == -7:
                # COMPACT
                # TODO: ADD DECODER
                compact = self.client.TCompactProtocol(self)
                _type = compact.readByte(data)
                data = data[1:]
                if _type == 1:
                    _seq, _offset = compact.readI32(data, True)
                    data = data[_offset:]
                    _msgId, _offset = compact.readI32(data, True)
                    data = data[_offset:]
                    _ts, _offset = compact.readI32(data, True)
                    data = data[_offset:]
                    compact.res = {"_seq": _seq, "messageId": _msgId, "time": _ts}
                    res = compact
                elif _type == 2:
                    raise LineServiceException({"code": compact.readI32(data)})
            elif ttype == -3:
                # JSON RAW
                return json.loads(data)
            elif ttype == -1:
                # CONTENT RAW
                return data
            elif ttype == 0:
                # RESP
                return conn_res
            else:
                # THRIFT
                try:
                    if ttype == 3:
                        res = self.client.TBinaryProtocol(
                            self, data, baseException=baseException
                        )
                    elif ttype == 4:
                        res = self.client.TCompactProtocol(
                            self, data, baseException=baseException
                        )
                    elif ttype == 5:
                        tmore = self.client.TMoreCompactProtocol(
                            self, data, baseException=baseException
                        )
                        res = tmore
                    else:
                        raise ValueError(f"Unknown ThriftType: {ttype}, data={data}")

                    # 2024/9/2: CHANGE ALL RES TO DUMMY.
                    res = self.serializeDummyProtocolToThrift(
                        res.dummyProtocol, baseException, readWith
                    )

                except Exception as e:
                    _err: dict[str, Any] = {
                        "code": None,
                        "message": None,
                        "metadata": None,
                        "raw": None,
                    }
                    if isinstance(e, LineServiceException):
                        _err["code"] = e.code
                        _err["message"] = e.message
                        _err["metadata"] = e.metadata
                    elif isinstance(e, TalkException):
                        _err["code"] = getattr(e, "code")
                        _err["message"] = getattr(e, "reason")
                        _err["metadata"] = getattr(e, "parameterMap")
                        _err["raw"] = e
                    else:
                        # non handler
                        raise e
                    res = {"error": _err}
            if isinstance(res, dict) and "error" in res:
                # idk why it got int on sometime
                resMsg = str(res["error"]["message"])
                logOutList = [
                    "EXPIRED",
                    "REVOKE",
                    "LOG_OUT",
                    "AUTHENTICATION_DIVESTED_BY_OTHER_DEVICE",
                    "DEVICE_LOSE",
                    "IDENTIFY_MODIFIED",
                    "V3_TOKEN_CLIENT_LOGGED_OUT",
                    "DELETED_ACCOUNT",
                ]
                if resMsg is not None and (
                    resMsg in logOutList or resMsg.startswith("suspended")
                ):
                    self.is_login = False
                    self.client.log(f"LOGIN OUT: {resMsg}")
                elif res["error"]["code"] == 119:
                    if self.tryRefreshToken():
                        return self.postPackDataAndGetUnpackRespData(
                            path, bdata, ttype, encType, headers
                        )
                    self.client.log(f"LOGIN OUT: {resMsg}")
                logger.error(res)
                raise LineServiceException(res["error"])
            self.client.log(f"Result: {res}", True)
            self.client.log("----------------- END POST", True)
            return res
        elif res.status_code in [400, 401, 403]:
            self.is_login = False
        elif res.status_code == 410:
            return None
        raise Exception(
            f"Invalid response status code: {res.status_code}, Headers: {res.headers}"
        )

    def getCurrReqId(self, whatFor: str = ""):
        self._msgSeq = 0
        unitKey = f"{whatFor}_reqseq"
        if unitKey in self.custom_data:
            self._msgSeq = self.custom_data[unitKey]
        self._msgSeq += 1
        self.custom_data[unitKey] = self._msgSeq
        self.saveCustomData()
        return self._msgSeq

    def getIntBytes(self, i, j=4, isCompact=False):
        i = int(i)
        if isCompact:
            _compact = self.client.TCompactProtocol(self)
            a = _compact.makeZigZag(i, 32 if j**2 == 16 else 64)
            b = _compact.writeVarint(a)
            return b
        if j**2 == 16:
            res = struct.pack("!i", i)
        else:
            res = struct.pack("!q", i)
        return list(res)

    def getStringBytes(self, text, isCompact=False):
        if text is None:
            text = ""
        if isinstance(text, bytes):
            pass
        else:
            text = str(text).encode()
        if isCompact:
            _compact = self.client.TCompactProtocol(self)
            sqrd = _compact.writeVarint(len(text))
        else:
            sqrd = self.getIntBytes(len(text))
        for value in text:
            sqrd.append(value)
        return sqrd

    def getFloatBytes(self, val, isCompact=False):
        res = []
        _t = "!d"
        if isCompact:
            _t = "<d"
        for value in struct.pack(_t, val):
            res.append(value)
        return res

    def getMagicStringBytes(self, val, rev=False):
        res = []
        if rev:
            res = binascii.b2a_hex(val)
        else:
            if len(val) == 32:
                for ii in range(16):
                    iii = ii * 2
                    i = iii + 1
                    mgc = (int(val[iii], 16) << 4) + int(val[i], 16)
                    res.append(mgc)
            else:
                raise ValueError(
                    f"getMagicStringBytes() expected 32, but got {len(val)}"
                )
        return res

    def createSqrSecret(self, base64Only=False):
        private_key = curve.generatePrivateKey(os.urandom(32))
        public_key = curve.generatePublicKey(private_key)
        secret = quote(b64encode(public_key).decode())
        version = 1
        if base64Only:
            return [private_key, b64encode(public_key).decode()]
        return [private_key, f"?secret={secret}&e2eeVersion={version}"]

    def getAllE2EESelfKey(self):
        r = []
        keys = self.client.getE2EEPublicKeys()
        if not isinstance(keys, list):
            raise ValueError
        for k in keys:
            key_id = k[2]  # keyId
            key_pk = k[4]  # keyData
            local_key_data = self.getE2EESelfKeyDataByKeyId(key_id)
            if local_key_data is not None:
                local_key_data["createdTime"] = k[5]
                r.append(local_key_data)
            else:
                self.client.logger.warn(f"E2EE Self Key not found: {k}")
        return r

    def getE2EESelfKeyData(self, mid: str):
        savePath = self.getSavePath(".e2eeKeys")
        fn = f"{mid}.json"
        if os.path.exists(savePath + f"/{fn}"):
            return json.loads(open(savePath + f"/{fn}", "r").read())
        keys = self.client.getE2EEPublicKeys()
        if isinstance(keys, list):
            for key in keys:
                keyId = self.client.checkAndGetValue(key, "keyId", 2)
                _keyData = self.getE2EESelfKeyDataByKeyId(keyId)
                if _keyData is not None:
                    return _keyData
        else:
            raise TypeError(
                "`getE2EEPublicKeys` expected type `list`, but got type `%s`: %r"
                % (type(keys), keys)
            )
        raise E2EESelfKeyNotFoundException(
            "E2EE Key has not been saved, try register or use SQR Login"
        )

    def getE2EESelfKeyDataByKeyId(self, keyId):
        savePath = self.getSavePath(".e2eeKeys")
        fn = f"key_{keyId}.json"
        if os.path.exists(savePath + f"/{fn}"):
            return json.loads(open(savePath + f"/{fn}", "r").read())
        return None

    def saveE2EESelfKeyData(self, mid, pubK, privK, kI, e2eeVersion):
        savePath = self.getSavePath(".e2eeKeys")
        fn = f"{mid}.json"
        fn2 = f"key_{kI}.json"
        data = json.dumps(
            {
                "keyId": kI,
                "privKey": b64encode(privK).decode(),
                "pubKey": b64encode(pubK).decode(),
                "e2eeVersion": e2eeVersion,
            }
        )
        if mid is not None:
            open(savePath + f"/{fn}", "w").write(data)
        open(savePath + f"/{fn2}", "w").write(data)
        return True

    def registerE2EESelfKey(self, privK: Optional[bytes] = None):
        if privK is None:
            privK = curve.generatePrivateKey(os.urandom(32))
        if privK is None or len(privK) != 32:
            raise ValueError("Invalid private key.")
        pubK = curve.generatePublicKey(privK)
        EPK = self.client.registerE2EEPublicKey(1, None, pubK, 0)
        keyId = self.client.checkAndGetValue(EPK, "keyId", 2)
        return self.saveE2EESelfKeyData(self.client.mid, pubK, privK, keyId, 1)

    def getCacheData(self, cT, cN, needHash=True, pathOnly=False):
        savePath = self.getSavePath(cT)
        fn = f"{cN}"
        if needHash:
            fn = md5(cN.encode()).hexdigest()
        if pathOnly:
            return savePath + f"/{fn}"
        if os.path.exists(savePath + f"/{fn}"):
            return open(savePath + f"/{fn}", "r").read()
        return None

    def saveCacheData(self, cT, cN, cD, needHash=True):
        savePath = self.getSavePath(cT)
        fn = f"{cN}"
        if needHash:
            fn = md5(cN.encode()).hexdigest()
        data = cD
        open(savePath + f"/{fn}", "w").write(data)
        return True

    def decodeE2EEKeyV1(self, data: dict, secret: bytes, mid: Optional[str] = None):
        if "encryptedKeyChain" in data:
            self.__logger.debug("Try to decode E2EE Key")
            encryptedKeyChain = base64.b64decode(data["encryptedKeyChain"])
            # hashKeyChain = data['hashKeyChain']
            keyId = data["keyId"]
            publicKey = base64.b64decode(data["publicKey"])
            e2eeVersion = data["e2eeVersion"]
            e2eeKey = self.client.decryptKeyChain(publicKey, secret, encryptedKeyChain)
            self.__logger.debug(f"E2EE Priv Key: {e2eeKey[0]}")
            self.__logger.debug(f"E2EE Pub Key: {e2eeKey[1]}")
            self.__logger.debug(f"keyId: {keyId}")
            self.__logger.debug(f"e2eeVersion: {e2eeVersion}")
            self.saveE2EESelfKeyData(mid, e2eeKey[1], e2eeKey[0], keyId, e2eeVersion)
            return {
                "keyId": keyId,
                "privKey": e2eeKey[0],
                "pubKey": e2eeKey[1],
                "e2eeVersion": e2eeVersion,
            }

    def readGenThrifts(self):
        path = os.path.join(os.path.dirname(__file__), "services", "thrift", "*.py")
        if self.client.path_gen_thrift is not None:
            path = os.path.join(self.client.path_gen_thrift, "*.py")
            self.__logger.info(f"Read GenThrifts from '{self.client.path_gen_thrift}'...")

        module_files = glob.glob(path)

        # https://github.com/DeachSword/MakiyuiSoul/blob/187186f910939bdfe4a38cd5b82a07ab4f30971c/__init__.py
        for filepath in module_files:
            filename = os.path.basename(filepath)
            if filename == "__init__.py":
                continue
            module_name = filename[:-3]

            spec = spec_from_file_location(
                module_name,
                filepath,
                submodule_search_locations=[os.path.dirname(filepath)],
            )
            if spec:
                module = module_from_spec(spec)
                sys.modules[module_name] = module
                globals()[module_name] = module
                if spec.loader:
                    spec.loader.exec_module(module)
            else:
                raise RuntimeError(f"Can't import {module_name}")

    def issueHttpClient(self, clientType: int = 0, **kwargs):
        if clientType == 0:
            return requests.session(**kwargs)
        elif clientType == 1:
            return httpx.Client(http2=True, verify=ssl.create_default_context(), **kwargs)

        # ENV: dev
        from curl_cffi import requests as curl_requests
        return curl_requests.Session(**kwargs)

    def tryReadThriftContainerStruct(self, data, id=0, get_data_len=False):
        _data = {}
        _dec = self.client.TCompactProtocol(self)
        ftype = data[0] & 15
        fid = (data[0] >> 4) + id
        offset = 1
        nextPos = 0
        if ftype == 0:
            _data = None
        elif ftype == 4:
            _data[fid] = _dec.readDouble(data[offset:])
            nextPos += 8
        elif ftype == 5:
            (_data[fid], nextPos) = _dec.readI32(data[offset:], True)
            nextPos += 1
        elif ftype == 6:
            (_data[fid], nextPos) = _dec.readI64(data[offset:], True)
            nextPos += 1
        elif ftype == 8:
            (_data[fid], nextPos) = _dec.readBinary(data[offset:])
        elif ftype == 9 or ftype == 10:
            (vtype, vsize, vlen) = _dec.readCollectionBegin(data[offset:])
            offset += vlen
            _data[fid] = []
            _nextPos = 0
            for i in range(vsize):
                if vtype == 12:
                    _r: Any = self.client.tryReadThriftContainerStruct(
                        data[offset:], get_data_len=True
                    )
                    _aaa, _bbb = _r
                    _data[fid].append(_aaa)
                    offset += _bbb + 1
        else:
            self.__logger.warning(
                f"[tryReadThriftContainerStruct]不支援Type: {ftype} => ID: {fid}"
            )
        if nextPos > 0:
            data = data[nextPos:]
            c = self.tryReadThriftContainerStruct(data, id=fid, get_data_len=True)
            if _data and c[0] is not None:
                _data.update(c[0])
            nextPos += c[1]
        if get_data_len:
            return [_data, nextPos]
        return _data

    def serializeDummyProtocolToThrift(
        self,
        data: DummyProtocol,
        baseException: Optional[dict] = None,
        readWith: Optional[str] = None,
    ):
        if baseException is None:
            baseException = {}

        # 2024/9/3: 刪除 use_thrift 的判定
        # 思路是能轉則轉, 並搭配 dummy thrift
        # 好處是可以檢測是否有fields未定義
        # 相對帶來性能消耗.
        a = None
        logger = self.__logger.overload("THRIFT")
        if readWith is not None:
            new1 = self.generateDummyProtocol2(data, 4, fixSuccessHeaders=True)
            try:
                a = eval(f"{readWith}_result")
                a = a()
            except AttributeError:
                a = None
            except NameError:
                a = None
            if a is not None:
                e = TMemoryBuffer(new1)
                f = tcProtocol(e)
                a = DummyThrift.wrap_thrift(self.client, a, not self.client.use_thrift)
                a.read(f)

        def _gen():
            return DummyThrift()

        def check_miss(refs):
            if isinstance(refs, DummyThrift):
                diff = refs.dd_diff()
                if diff:
                    logger.warn(
                        " ".join(
                            [
                                f"'{refs.__ins_name__}'",
                                "missing define fields:",
                                str(diff),
                            ]
                        )
                    )

                # check fields
                for f in refs.field_names:
                    check_miss(getattr(refs.thrift_ins, f))
            elif isinstance(refs, dict):
                for rk, rv in refs.items():
                    check_miss(rk)
                    check_miss(rv)
            elif type(refs) in [list, set]:
                for ref in refs:
                    check_miss(ref)

        def _genFunc(a: DummyProtocolData, b, f):
            def __gen(a: DummyProtocolData, b):
                c = _gen()
                for d in a.data:
                    b(d, c)
                return c

            def __cek(a: DummyProtocolData, f):
                if a.type == 12:
                    c = __gen(a, f)
                elif a.type == 13:
                    c = {}
                    d = a.data
                    for e in d:
                        g = d[e]
                        h = e
                        if isinstance(h, DummyProtocolData):
                            h = __cek(h, f)
                        if isinstance(g, DummyProtocolData):
                            g = __cek(g, f)
                        c[h] = g
                elif a.type in (14, 15):
                    c = []
                    for d in a.data:
                        e = d
                        if isinstance(d, DummyProtocolData):
                            e = __cek(d, f)
                        c.append(e)
                else:
                    c = a.data
                return c

            c = __cek(a, f)
            setattr(b, f"val_{a.id}", c)

        if a is None or not isinstance(a, DummyThrift):
            a = _gen()

        def b(c, refs):
            r = (
                _genFunc(c, refs, b)
                if type(c.data) in [list, dict]
                else setattr(refs, f"val_{c.id}", c)
            )
            return r

        if data.data is not None:
            b(data.data, a)
            check_miss(a)

        # 2024/9/3: 改為遍歷方式去判斷
        # 非 None 直接返回
        # 若為 Exception 則直接使用 raise
        for field_name in a.field_names:
            field = getattr(a.thrift_ins, field_name)
            if field is not None:
                if isinstance(field, DummyThrift) and isinstance(
                    field.thrift_ins, Exception
                ):
                    raise field.thrift_ins
                return field

        if self.client.checkAndGetValue(a, "val_0") is not None:
            return a.val_0
        _ecode = baseException.get("code", 1)
        _emsg = baseException.get("message", 2)
        _emeta = baseException.get("metadata", 3)
        if self.client.checkAndGetValue(a, "val_1") is not None:
            raise LineServiceException(
                {},
                self.client.checkAndGetValue(a.val_1, f"val_{_ecode}"),
                self.client.checkAndGetValue(a.val_1, f"val_{_emsg}"),
                self.client.checkAndGetValue(a.val_1, f"val_{_emeta}"),
                a.val_1,
            )
        # no vals
        # eg. noop()
        return None


def thrift2dummy(a):
    if type(a) == dict:
        b = {}
        for k, v in a.items():
            b[thrift2dummy(k)] = thrift2dummy(v)
        return b
    elif type(a) == list:
        return [thrift2dummy(a2) for a2 in a]
    elif isinstance(a, DummyProtocolData):
        b = None
        c = []
        if a.type in [2, 3, 4, 6, 8, 10, 11]:
            b = a.data
        elif a.type == 12:
            b = [thrift2dummy(a2) for a2 in a.data]
        elif a.type == 13:
            b = [a.subType[0], a.subType[1], thrift2dummy(a.data)]
        elif a.type in [14, 15]:
            b = [a.subType[0], thrift2dummy(a.data)]
        else:
            raise ValueError(f"Not supported type: {a.type}")
        if a.id is not None:
            return [a.type, a.id, b]
        return b
    else:
        raise ValueError(f"[thrift2dummy] not support `{type(a)}`: {a}")


def doLoopReq(
    req, data, currCount: int = 0, maxRetryCount: int = 5, retryTimeDelay: int = 8
):
    currCount += 1
    doRetry = False
    e: Any = None
    res = None
    try:
        res = req(**data)
    except httpx.ConnectTimeout as ex:
        doRetry = True
        e = ex
    except (httpx.ReadTimeout, requests.exceptions.ReadTimeout) as ex:
        currCount -= 1
        doRetry = True
        e = ex
    except httpx.ReadError as ex:
        doRetry = True
        e = ex
    except httpx.ConnectError or requests.exceptions.ConnectionError as ex:
        currCount -= 1
        retryTimeDelay += 1
        doRetry = True
        e = ex
    except httpx.RemoteProtocolError as ex:
        currCount -= 1
        doRetry = True
        e = ex
    if doRetry:
        if currCount > maxRetryCount:
            raise e
        time.sleep(retryTimeDelay)
        return doLoopReq(req, data, currCount, maxRetryCount, retryTimeDelay)
    if res is None:
        raise EOFError
    return res
