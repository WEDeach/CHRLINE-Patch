# -*- coding: utf-8 -*-
import hashlib
import json
import time
import uuid
from base64 import b64encode
from typing import Any, List, Optional, Union
from urllib import parse

import httpx

from .BIZ.services.internal.define_typed.Album import (
    ResourceTypeMap,
    TAlbumPhoto,
    TAlbumResourceType,
)
from .helper import ChrHelperProtocol

MediaNextTypeSets = {
    "image": ("emi", 1),
    "video": ("emv", 2),
    "audio": ("ema", 3),
    "file": ("emf", 14),
    "gif": ("emi", 1),
}


def file_decoder(func):
    def wrapper(*args, **kwargs):
        pathOrBytes = None
        raw_data = None
        if len(args) > 1:
            pathOrBytes = args[1]
        elif "pathOrBytes" in kwargs:
            pathOrBytes = kwargs["pathOrBytes"]
        if isinstance(pathOrBytes, str):
            if pathOrBytes.startswith("http"):
                # URL
                with httpx.Client() as hc:
                    raw_data = hc.get(pathOrBytes).content
            else:
                # FILE
                with open(pathOrBytes, "rb") as f:
                    raw_data = f.read()
        else:
            # BYTES
            raw_data = pathOrBytes
        if "pathOrBytes" in kwargs:
            kwargs["pathOrBytes"] = raw_data
        else:
            args_list = list(args)
            args_list[1] = raw_data
            args = tuple(args_list)
        return func(*args, **kwargs)

    return wrapper


def media_type_check(func):
    def wrapper(*args, **kwargs):
        oType = None
        if len(args) > 2:
            oType = args[2]
        elif "oType" in kwargs:
            oType = kwargs["oType"]
        if oType not in ["image", "gif", "video", "audio", "file"]:
            raise TypeError(f"Invalid oType: {oType}")
        return func(*args, **kwargs)

    return wrapper


class Object(ChrHelperProtocol):
    def __init__(self):
        self.Hraders4Obs = {
            "User-Agent": self.client.server.Headers["User-Agent"],
            "X-Line-Access": self.client.authToken,
            "X-Line-Application": self.client.server.Headers["x-line-application"],
            "X-Line-Mid": self.client.mid,
            "x-lal": self.client.LINE_LANGUAGE,
        }
        if self.client.DEVICE_TYPE != "CHROMEOS":
            e_token = self.client.acquireEncryptedAccessToken()
            if not isinstance(e_token, str):
                raise ValueError(f"EncryptedAccessToken  should be str: {e_token}")
            self.Hraders4Obs["X-Line-Access"] = e_token.split("\x1e")[1]
        self.obsConn = httpx.Client(http2=True, timeout=None)
        self.__logger = self.client.get_logger("OBS")
        self._flows = {}

    """

    TimelineObs
    Source: https://github.com/DeachSword/LINE-DemoS-Bot/blob/master/api/obs/obs.py

    """

    def sendImage(self, to, path, oType="image"):
        return self.uploadObjTalk(pathOrBytes=path, oType=oType, to=to)

    def sendGIF(self, to, path, oType="gif"):
        return self.uploadObjTalk(pathOrBytes=path, oType=oType, to=to)

    def sendVideo(self, to, path, oType="video"):
        return self.uploadObjTalk(pathOrBytes=path, oType=oType, to=to)

    def sendAudio(self, to, path, oType="audio"):
        return self.uploadObjTalk(pathOrBytes=path, oType=oType, to=to)

    def sendFile(self, to, path, oType="file"):
        return self.uploadObjTalk(pathOrBytes=path, oType=oType, to=to)

    def sendObjHomeToTalk(self, to, oid, returnHeaders=False, **kwargs):
        data = {
            "oid": "reqseq",
            "tomid": to,
            "reqseq": self.client.getCurrReqId(),
            "ver": "1.0",
        }
        if (
            "issueToken4ChannelId" not in kwargs
        ):  # If you don't want this value, please set it to None.
            kwargs["issueToken4ChannelId"] = "1341209850"
        kwargs["copyFromService"] = "myhome"
        kwargs["copyFromSid"] = "h"
        kwargs["copyFromObjId"] = oid
        kwargs["copy2Service"] = "talk"
        kwargs["copy2Sid"] = "m"
        kwargs["copy2ObjId"] = "reqseq"
        obsObjId, obsHash, respHeaders = self.forwardObjectForService(data, **kwargs)
        if returnHeaders:
            return respHeaders
        return obsObjId

    def updateProfileImage(
        self, path, storyShare=False, type="p", mid: Optional[str] = None
    ):
        """
        Update profile image.

        use `mid` for square member.
        """
        if mid is None:
            mid = self.client.mid
        midType = self.client.getToType(mid)
        if midType == 0:
            obsPath = f"talk/p/{mid}"
        elif midType == 5:
            obsPath = f"g2/member/{mid}"
        else:
            raise ValueError(f"Invalid midType: {midType}")
        oType = "IMAGE"
        params = {}
        is_video = self.client.checkIsVideo(path)
        hstr = "DearSakura_%s" % int(time.time() * 1000)
        hstr = hashlib.md5(hstr.encode()).hexdigest()
        filename = "profile.jpg"
        metaData = {"profileContext": {"storyShare": storyShare}}
        if type == "vp":
            params["cat"] = "vp.mp4"  # let server know u have vp.mp4
        is_video = self.client.checkIsVideo(path)
        if is_video:
            obsPath = f"talk/vp/{mid}"
            oType = "VIDEO"
            filename = f"{hstr}.mp4"
            params = {
                "cat": "vp.mp4",
            }
        talkMeta = b64encode(json.dumps(metaData).encode("utf-8")).decode("utf-8")
        try:
            objId, objHash, respHeaders = self.uploadObjectForService(
                path, oType, obsPath, "1341209850", params, talkMeta, filename
            )
        except Exception as e:
            raise e
        return True

    def updateProfileCover(self, path, storyShare=False):
        hstr = "DearSakura_%s" % int(time.time() * 1000)
        objId = hashlib.md5(hstr.encode()).hexdigest()
        obsPath = f"myhome/c/{objId}"
        oType = "IMAGE"
        filename = f"{objId}.jpg"
        params = None
        is_video = self.client.checkIsVideo(path)
        if is_video:
            obsPath = f"myhome/vc/{objId}"
            oType = "VIDEO"
            filename = f"{objId}.mp4"
            params = {}
        try:
            objId, objHash, respHeaders = self.uploadObjectForService(
                path, oType, obsPath, "1341209850", params, filename=filename
            )
            print(respHeaders)
        except Exception as e:
            raise Exception(e)
        if is_video:
            _url, _vc_url, _objId, _vc_objId = self.client.getProfileCoverObjIdAndUrl(
                self.client.mid
            )
            home = self.client.biz.myhome_renewal.update_cover_renewal(
                self.client.mid, coverObjectId=_objId, videoCoverObjectId=f"{objId}/vp"
            )
        else:
            home = self.client.biz.myhome_renewal.update_cover_renewal(
                self.client.mid, coverObjectId=objId
            )
        return home

    def updateChatProfileImage(self, groupId: str, path: str, oType: str = "IMAGE"):
        midType = self.client.getToType(groupId)
        if midType in [1, 2]:
            obsPath = f"talk/g/{groupId}"
        elif midType == 3:
            obsPath = f"g2/group/{groupId}"
        elif midType == 4:
            obsPath = f"g2/chat/{groupId}"
        else:
            raise ValueError(f"Invalid midType: {midType}")
        params = {"cat": "original"}
        try:
            objId, objHash, respHeaders = self.uploadObjectForService(
                path, oType, obsPath, "1341209850", params, filename="profile.jpg"
            )
        except Exception as e:
            raise Exception(f"updateChatProfileImage failure: {e}")
        return True

    def updateImageToAlbum(
        self,
        homeId: str,
        albumId: int,
        pathOrBytes: Union[str, bytes, List[Union[str, bytes]]],
        oType: TAlbumResourceType = "IMAGE",
        updateAlbum: bool = True,
    ):
        """
        Upload Object to Album Obs.

        will use `updateAlbum` to update the album, if content uploads success.
        ---------------
        Return `OBS_OID` and `OBS_HASH`
        """
        if oType not in ResourceTypeMap.keys():
            raise TypeError(f"Not support resource type: {oType}")
        resourceType = ResourceTypeMap[oType]
        oids = []
        photos: List[TAlbumPhoto] = []
        additionalHeaders = {
            "X-Line-Album": str(albumId),
            "X-Line-Mid": homeId,
        }
        if not isinstance(pathOrBytes, list):
            pathOrBytes = [pathOrBytes]
        for _uploadData in pathOrBytes:
            oid = f"{uuid.uuid1().hex}.20{time.strftime('%m%d')}08"
            params = {"oid": oid}
            obsObjId, obsHash, respHeaders = self.uploadObjectForService(
                _uploadData,
                oType,
                f"album/{resourceType}/{oid}",
                issueToken4ChannelId="1341209850",
                params=params,
                additionalHeaders=additionalHeaders,
            )
            oids.append(obsObjId)
            photos.append(
                {
                    "obsResourceId": {"svc": "album", "sid": resourceType, "oid": oid},
                    "resourceType": oType,
                    "height": 0,
                    "width": 0,
                    "shotTime": 0,
                    "durationMillis": 0,
                }
            )
        if updateAlbum:
            self.client.biz.album.add_photos(homeId, albumId=albumId, photos=photos)
        return photos

    def uploadObjHome(self, path, type="image", objId=None):
        if type == "image":
            contentType = "image/jpeg"
        elif type == "video":
            contentType = "video/mp4"
        elif type == "audio":
            contentType = "audio/mp3"
        else:
            raise Exception("Invalid type value")
        if not objId:
            hstr = "DearSakura_%s" % int(time.time() * 1000)
            objId = hashlib.md5(hstr.encode()).hexdigest()
        file = open(path, "rb").read()
        params = {
            "name": f"{objId}.mp4",
            "oid": "%s" % str(objId),
            "type": type,
            "ver": "2.0",  # 2.0 :p
        }
        hr = self.client.server.additionalHeaders(
            self.client.server.timelineHeaders,
            {
                "Content-Type": contentType,
                "Content-Length": str(len(file)),
                "x-obs-params": self.client.genOBSParams(
                    params, "b64"
                ),  # base64 encode
            },
        )
        r = self.client.server.postContent(
            self.client.LINE_OBS_DOMAIN + "/myhome/h/upload.nhn", headers=hr, data=file
        )
        if r.status_code != 201:
            raise Exception(
                f"Upload object home failure. Receive statue code: {r.status_code}"
            )
        return objId

    def uploadMultipleImageToTalk(
        self,
        pathOrObjids: list,
        to: str,
        mtype: str = "image",
        oTypes: Optional[list] = None,
    ):
        """
        Args:
            pathOrObjids: multiple image paths or multiple objids according to the type
            to: send chat id
            mtype: image or objids
            oTypes: image
        """

        def createTalkMeta(hmap):
            sqrd_base = [13, 0, 18, 11, 11]
            sqrd = sqrd_base + self.client.getIntBytes(len(hmap.keys()))
            for hm in hmap.keys():
                sqrd += self.client.getStringBytes(hm)
                sqrd += self.client.getStringBytes(hmap[hm])
            sqrd += [0]
            data = bytes(sqrd)
            msg = json.dumps({"message": b64encode(data).decode("utf-8")})
            return b64encode(msg.encode("utf-8")).decode("utf-8")

        if mtype.lower() == "image":
            mtype = "image"
        elif mtype.lower() == "objids":
            mtype = "objids"
        else:
            raise Exception("Type must be image or object")

        if not isinstance(pathOrObjids, list):
            raise Exception("pathOrObjids must be list")

        res = {}
        oType = []
        hashmap = {"GID": "0", "GSEQ": "1", "GTOTAL": str(len(pathOrObjids))}
        talkMeta = createTalkMeta(hashmap)
        if mtype == "image":
            if oTypes is None:
                oTypes = ["image" for _ in range(len(pathOrObjids))]
            oType = iter(oTypes)
            res = self.uploadObjTalk(
                pathOrObjids[0],
                next(oType),
                to=to,
                talkMeta=talkMeta,
                returnHeaders=True,
            )
        elif mtype == "objids":
            res: Any = self.uploadObjTalk(
                to, pathOrObjids[0], talkMeta=talkMeta, returnHeaders=True
            )

        gid, msgIds = res["x-line-message-gid"], [res["x-obs-oid"]]

        if len(pathOrObjids) > 1:
            hashmap["GID"] = gid
            nc = 2
            for poo in pathOrObjids[1:]:
                self.client.log(f"Upload image-{nc} with GID-{gid}...", True)
                hashmap["GSEQ"] = str(nc)
                talkMeta = createTalkMeta(hashmap)
                if oTypes is None:
                    oTypes = ["image" for _ in range(len(pathOrObjids))]
                oType = iter(oTypes)
                if mtype == "image":
                    res = self.uploadObjTalk(
                        poo, next(oType), to=to, talkMeta=talkMeta, returnHeaders=True
                    )
                elif mtype == "objids":
                    res = self.uploadObjTalk(
                        to, poo, talkMeta=talkMeta, returnHeaders=True
                    )
                msgIds.append(res["x-obs-oid"])
                nc += 1

        return gid, msgIds

    def uploadObjTalk(
        self,
        pathOrBytes,
        oType="image",
        objId=None,
        to=None,
        talkMeta=None,
        returnHeaders=False,
        filename: Optional[str] = None,
        isOriginal: bool = False,
    ):
        if oType.lower() not in ["image", "gif", "video", "audio", "file"]:
            raise Exception("Invalid type value")
        # url = self.client.LINE_OBS_DOMAIN + '/talk/m/upload.nhn' #if reqseq not working
        # url = self.client.LINE_OBS_DOMAIN + '/r/talk/m/reqseq'
        serviceName = "talk"
        obsNamespace = "m"
        params = {}
        if oType.lower() == "gif":
            params["cat"] = "original"
            oType = "IMAGE"
        if isOriginal:
            params["cat"] = "original"
        if to is not None:
            params.update(
                {
                    "oid": "reqseq",
                    "reqseq": str(self.client.getCurrReqId()),
                    "tomid": to,
                }
            )
            objId = "reqseq"
            if self.client.getToType(to) in [0, 1, 2]:
                flows = []
                d = None
                if to in self._flows:
                    flows, d2 = self._flows[to]
                    if d2 > time.time():
                        d = self._flows[to]
                if d is None:
                    _d: Any = self.client.determineMediaMessageFlow(to)
                    d = _d[1], time.time() + _d[2] / 1000
                    flows, _ = d
                    self._flows[to] = d
                    self.__logger.info(f"Cache Medai Next state for {to}: {flows}")
                _, d3 = MediaNextTypeSets[oType]
                if flows[d3] == 2:
                    return self.uploadMediaByE2EE(pathOrBytes, oType, to)
            elif self.client.getToType(to) == 4:
                serviceName = "g2"
        else:
            if objId is not None:
                params["oid"] = objId
        obsObjId, obsHash, respHeaders = self.uploadObjectForService(
            pathOrBytes,
            oType,
            f"{serviceName}/{obsNamespace}/{objId}",
            params=params,
            talkMeta=talkMeta,
            filename=filename,
        )
        if returnHeaders:
            return respHeaders
        objId = obsObjId
        objHash = obsHash  # for view on cdn
        return objId

    def uploadStoryObject(self, pathOrBytes: Union[str, bytes], oType="IMAGE"):
        """
        Upload Object to Story Obs.

        ---------------
        Return `OBS_OID` and `OBS_HASH`
        """
        oid = f"{uuid.uuid1().hex}tffffffff"
        params = {"oid": oid}
        obsObjId, obsHash, respHeaders = self.uploadObjectForService(
            pathOrBytes,
            oType,
            f"story/st/{oid}",
            issueToken4ChannelId="1341209850",
            params=params,
        )
        return obsObjId, obsHash

    def forwardObjectMsg(self, to: str, msgId: str, _from: str = "u", **kwargs):
        """
        Forward object to Talk

        use `_from` to specify the source mid of the messageid
        """
        copyFromService = "talk"
        copyFromSid = "m"
        copy2Service = "talk"
        copy2Sid = "m"
        data = {
            "oid": "reqseq",
            "tomid": to,
            "reqseq": self.client.getCurrReqId(),
            "ver": "1.0",
        }
        toType = self.client.getToType(to)
        if toType in [0, 1, 2]:
            pass
        elif toType == 4:
            copy2Service = "g2"
        else:
            raise ValueError(f"Invalid `to` midType: {toType}")
        toType = self.client.getToType(_from)
        if toType in [0, 1, 2]:
            pass
        elif toType == 4:
            copyFromService = "g2"
        else:
            raise ValueError(f"Invalid `_from` midType: {toType}")
        kwargs["copyFromService"] = copyFromService
        kwargs["copyFromSid"] = copyFromSid
        kwargs["copyFromObjId"] = msgId
        kwargs["copy2Service"] = copy2Service
        kwargs["copy2Sid"] = copy2Sid
        kwargs["copy2ObjId"] = "reqseq"
        return self.forwardObjectForService(data, **kwargs)

    def forwardKeepObjectMsg(self, to, oid, contentId, contentType="image"):
        # SHARE KEEP CONTENTS V1
        data = {
            "copyFrom": f"/keep/p/{oid}",
            "tomid": to,
            "reqseq": self.client.getCurrReqId(),
            "type": contentType,
            "contentId": contentId,
            "size": "-1",
        }
        if contentType == "image":
            data["cat"] = "original"
        elif contentType in ["audio", "video"]:
            data["duration"] = "3000"
        print(self.client.server.timelineHeaders)
        r = self.client.server.postContent(
            self.client.LINE_HOST_DOMAIN + "/oa/r/talk/m/reqseq/copy.nhn",
            data=data,
            headers=self.client.server.timelineHeaders,
        )
        if not self.client.checkRespIsSuccessWithLpv(r):
            raise Exception(f"Forward object failure: {r.status_code}")
        return r.headers["X-Obs-Oid"]

    def forwardKeepContent2Mid(self, to: str, oid: str, contentId: str, **kwargs):
        # SHARE KEEP CONTENTS V2
        data = {
            "tomid": to,
            "reqseq": self.client.getCurrReqId(),
        }
        kwargs["copyFromService"] = "keep"
        kwargs["copyFromSid"] = "p"
        kwargs["copyFromObjId"] = oid
        kwargs["contentId"] = contentId
        return self.forwardObjectForService(data, **kwargs)

    def trainingImage(self, msgId):
        data = {
            "useAsTrainingData": False,
            "input": "obs://talk/m/%s" % msgId,
            "filters": {"OCR": {"params": {"useColorPicker": "true"}}},
        }

        hr = self.client.server.additionalHeaders(
            self.client.server.timelineHeaders,
            {
                "x-client-channel": "chat_viewer",
                "x-lal": "zh-Hant_TW",
                "x-recognition-input-type": "obs",
                "Content-Type": "application/json",
            },
        )
        r = self.client.server.postContent(
            self.client.LINE_OBS_DOMAIN + "/px/talk/m/%s/recognition.obs" % msgId,
            data=json.dumps(data),
            headers=hr,
        )
        if not self.client.checkRespIsSuccessWithLpv(r):
            raise Exception(f"Training image failure: {r.status_code}")
        return r.json()

    def downloadObjectMsg(
        self, objId: str, path: Optional[str] = None, objFrom: str = "c"
    ):
        obs_path = f'{"g2" if self.client.getToType(objFrom) == 4 else "talk"}/m'
        return self.downloadObjectForService(objId, path, obs_path)

    def downloadAlbumImage(self, oid: str, path: str):
        """Download album image."""
        obs_path = f"/album/a/download.nhn?ver=1.0&oid={oid}"
        r = self.client.server.getContent(
            self.client.LINE_OBS_DOMAIN + obs_path,
            headers=self.client.server.timelineHeaders,
        )
        with open(path, "wb") as f:
            f.write(r.content)
        return r.content

    def downloadAlbumImageV2(
        self, _from: str, albumId: str, oid: str, savePath: Optional[str] = None
    ):
        """Download album image v2."""
        ext = {"X-Line-Album": str(albumId), "X-Line-Mid": _from}
        return self.downloadObjectForService(
            oid,
            savePath,
            "album/a",
            issueToken4ChannelId="1375220249",
            additionalHeaders=ext,
        )

    def downloadProfileImage(self, mid: str, base_path: str, video: bool = False):
        url = self.client.LINE_OBS_DOMAIN + f"/r/talk/p/{mid}"
        savePath = f"{base_path}/{mid}.jpg"
        if video:
            url += "/vp"
            savePath = f"{base_path}/{mid}.mp4"
        r = self.client.server.getContent(
            url, headers=self.client.server.timelineHeaders
        )
        with open(savePath, "wb") as f:
            f.write(r.content)
        return savePath

    def downloadProfileCover(self, mid: str, base_path: str, video: bool = False):
        url, vc_url, objId, vc_objId = self.client.getProfileCoverObjIdAndUrl(mid)
        savePath = f"{base_path}/{mid}.jpg"
        r = self.client.server.getContent(
            url, headers=self.client.server.timelineHeaders
        )
        with open(savePath, "wb") as f:
            f.write(r.content)
        return savePath

    def downloadObjectMyhome(self, objId, path, objFrom="h"):
        return self.downloadObjectForService(
            objId, path, obsPathPrefix=f"myhome/{objFrom}"
        )

    def downloadImageWithURL(self, url: str, path=None):
        # TEST
        savePath = path
        if savePath is None:
            savePath = f"./.image/{time.time()}.jpg"
        r = self.client.server.getContent(url)
        if r.status_code != 200:
            raise Exception(f"Not a picture with URL. code: {r.status_code}")
        with open(savePath, "wb") as f:
            f.write(r.raw)
        return savePath

    def downloadObjectForService(
        self,
        objId,
        savePath,
        obsPathPrefix="myhome/h",
        size=None,
        suffix=None,
        issueToken4ChannelId: Optional[str] = None,
        params: Optional[dict] = None,
        additionalHeaders: Optional[dict] = None,
    ):
        obs_path = f"/oa/r/{obsPathPrefix}/{objId}"
        if params is None:
            params = {}
        if size is not None:
            # eg. size = "m800x1200" or "L800x1200"or "w800"
            # must be an existing size :p
            obs_path += f"/{size}"
        if suffix is not None:
            # eg. suffix = "mp4"
            obs_path += f"/{suffix}"
        hr = self.Hraders4Obs
        hr = self.client.server.additionalHeaders(
            hr,
            {
                "X-LHM": "GET",
                "X-LPV": "1",
            },
        )
        if issueToken4ChannelId is not None:
            hr = self.client.server.additionalHeaders(
                hr,
                {
                    "X-Line-ChannelToken": self.client.checkAndGetValue(
                        self.client.approveChannelAndIssueChannelToken(
                            issueToken4ChannelId
                        ),
                        "channelAccessToken",
                        5,
                    ),
                },
            )
        if additionalHeaders is not None:
            hr.update(additionalHeaders)
        isDebugOnly = True
        log = self.__logger.debug if isDebugOnly else self.__logger.info
        log("Starting downloadObjectForService...")
        log(f"obsPath: {obs_path}")
        log(f"params: {params}")
        log(f"hr: {hr}")
        try:
            r: Any = self.client.postPackDataAndGetUnpackRespData(
                obs_path, b"", 0, 0, headers=hr, conn=self.obsConn
            )
        except Exception as e:
            print("downloadObjectForService: ", e)
            raise Exception(
                f"[downloadObjectForService] Download failed! path={obs_path}, err=`{e}`."
            )
        if r.status_code != 200:
            raise Exception(
                f"[downloadObjectForService] Download failed! Resp status expected `200`, got `{r.status_code}`."
            )
        if savePath is not None:
            with open(savePath, "wb") as f:
                f.write(r.content)
        log("Ended downloadObjectForService!")
        return r.content

    def uploadObjectForService(
        self,
        pathOrBytes: Union[str, bytes],
        oType: str = "image",
        obsPath: str = "myhome/h",
        issueToken4ChannelId: Optional[str] = None,
        params: Optional[dict] = None,
        talkMeta: Optional[str] = None,
        filename: Optional[str] = None,
        additionalHeaders: Optional[dict] = None,
    ):
        obs_path = f"/r/{obsPath}"
        hr = self.Hraders4Obs
        data = None
        files = None
        oType = oType.lower()
        isDebugOnly = True
        if isinstance(pathOrBytes, str):
            if pathOrBytes.startswith("http"):
                # URL
                with httpx.Client() as hc:
                    data = hc.get(pathOrBytes).content
            else:
                # FILE
                files = {"file": open(pathOrBytes, "rb")}
                filename = files["file"].name if filename is None else filename
                filename = filename.split("\\")[-1]
                with open(pathOrBytes, "rb") as f:
                    data = f.read()
        else:
            # BYTES
            data = pathOrBytes
        filename = str(uuid.uuid1()) if filename is None else filename
        base_params = {
            "type": oType,
            "ver": "2.0",
            "name": filename,
        }
        if params:
            base_params.update(params)
        params = base_params
        if files is not None:
            # FORM DATA
            data = {"params": json.dumps(params)}
            params = None
        else:
            # POST DATA
            files = None
            if len(data) == 0:
                raise ValueError("No data to send: %s" % data)
            hr = self.client.server.additionalHeaders(
                hr,
                {
                    "Content-Type": "application/octet-stream",  # but...
                    "Content-Length": str(len(data)),
                    "X-Obs-Params": self.client.genOBSParams(params, "b64"),
                },
            )
        if issueToken4ChannelId is not None:
            hr = self.client.server.additionalHeaders(
                hr,
                {
                    "X-Line-ChannelToken": self.client.checkAndGetValue(
                        self.client.approveChannelAndIssueChannelToken(
                            issueToken4ChannelId
                        ),
                        "channelAccessToken",
                        5,
                    ),
                },
            )
        if params is not None:
            obs_params = self.client.genOBSParams(params, "b64")
            if isinstance(obs_params, bytes):
                obs_params = obs_params.decode()
            hr = self.client.server.additionalHeaders(
                hr,
                {
                    "X-Obs-Params": obs_params,
                },
            )
        if talkMeta is not None:
            hr = self.client.server.additionalHeaders(hr, {"X-Talk-Meta": talkMeta})
        if additionalHeaders is not None:
            hr.update(additionalHeaders)
        log = self.__logger.debug if isDebugOnly else self.__logger.info
        log("Starting uploadObjectForService...")
        log(f"data: {str(data)[:200]}")
        log(f"files: {files}")
        log(f"obsPath: {obs_path}")
        log(f"params: {params}")
        log(f"files: {files}")
        log(f"hr: {hr}")
        r: Any = self.client.postPackDataAndGetUnpackRespData(
            f"/oa{obs_path}",
            data,
            0,
            0,
            headers=hr,
            expectedRespCode=[200, 201],
            conn=self.obsConn,
            files=files,
        )
        # expectedRespCode:
        # - 200: image cache on obs server
        # - 201: image created success
        objId = r.headers["x-obs-oid"]
        objHash = r.headers["x-obs-hash"]  # for view on cdn
        log("Ended uploadObjectForService!")
        return objId, objHash, r.headers

    def forwardObjectForService(
        self,
        data: dict,
        contentType: str = "image",
        copyFromService: str = "talk",
        copyFromSid: str = "m",
        copyFromObjId: Optional[str] = None,
        copyFrom: Optional[str] = None,
        copy2Service: Optional[str] = "talk",
        copy2Sid: str = "m",
        copy2ObjId: Optional[str] = None,
        copy2: Optional[str] = None,
        contentId: Optional[str] = None,
        original: bool = False,
        duration: Optional[int] = None,
        issueToken4ChannelId: Optional[str] = None,
        talkMeta: Optional[str] = None,
        additionalHeaders: Optional[dict] = None,
    ):
        if contentType.lower() not in ["image", "video", "audio", "file"]:
            raise Exception("Type not valid.")
        if copyFrom is None:
            copyFrom = f"/{copyFromService}/{copyFromSid}"
            if copyFromObjId is not None:
                copyFrom += f"/{copyFromObjId}"
        if copy2 is None:
            copy2 = f"{copy2Service}/{copy2Sid}"
            if copy2ObjId is not None:
                copy2 += f"/{copy2ObjId}"
        base_data = {
            "copyFrom": copyFrom,
            "type": contentType,
            "ver": "1.0",
        }
        if contentId is not None:
            base_data["contentId"] = contentId
        if original:
            base_data["cat"] = "original"
        if duration is not None:
            base_data["duration"] = str(duration)
        base_data.update(data)
        data = base_data
        hr = self.Hraders4Obs
        if issueToken4ChannelId is not None:
            hr = self.client.server.additionalHeaders(
                hr,
                {
                    "X-Line-ChannelToken": self.client.checkAndGetValue(
                        self.client.approveChannelAndIssueChannelToken(
                            issueToken4ChannelId
                        ),
                        "channelAccessToken",
                        5,
                    ),
                },
            )
        if talkMeta is not None:  # Support Multiple Image
            hr = self.client.server.additionalHeaders(hr, {"X-Talk-Meta": talkMeta})
        if additionalHeaders is not None:
            hr.update(additionalHeaders)
        data2 = list(parse.urlencode(data).encode())
        r: Any = self.client.postPackDataAndGetUnpackRespData(
            f"/oa/r/{copy2}/copy.nhn", data2, 0, 0, headers=hr, conn=self.obsConn
        )
        objId = r.headers["x-obs-oid"]
        objHash = r.headers["x-obs-hash"]
        return objId, objHash, r.headers

    def getObjPlayback(self, oid: int, type: str = "VIDEO"):
        url = self.client.LINE_HOST_DOMAIN + "/oa/talk/m/playback.obs?p=sg-1"
        data = {
            "networkType": "Cell",
            "oid": oid,
            "type": type,
            "ver": "1.0",
            "modelName": "ios",
            "lang": "zh",
        }
        hr = self.client.server.additionalHeaders(
            self.client.server.timelineHeaders,
            {
                "x-obs-channeltype": "legy",
            },
        )
        r = self.client.server.postContent(url, data=data, headers=hr)
        if not self.client.checkRespIsSuccessWithLpv(r):
            raise Exception(f"GetObjPlayback failure: {r.status_code}")
        return r.json()

    def downloadKeepContentByOidAndContentId(
        self, oid: str, contentId: str, save_path: Optional[str] = None, sid: str = "p"
    ):
        return self.downloadObjectForService(
            oid,
            save_path,
            obsPathPrefix=f"keep/{sid}",
            issueToken4ChannelId="1433572998",
            params={"contentId": contentId},
        )

    def copyTalkObject4Keep(self, messageId: str, service="talk"):
        url = self.client.LINE_HOST_DOMAIN + "/oa/keep/p/copy.nhn"
        hstr = "DearSakura_%s_%s" % (int(time.time() * 1000), int(messageId))
        file_name = hashlib.md5(hstr.encode()).hexdigest()
        keep_oid = f"linekeep_{file_name}_tffffffff"
        data = {"oid": keep_oid, "copyFrom": f"/{service}/m/{messageId}"}
        hr = self.client.server.additionalHeaders(
            self.Hraders4Obs,
            {
                "x-obs-channeltype": "legy",
            },
        )
        r = self.client.server.postContent(url, data=data, headers=hr)
        if not self.client.checkRespIsSuccessWithLpv(r):
            raise Exception(f"saveTalkObject2Keep failure: {r.status_code}")
        return r.json()

    @file_decoder
    @media_type_check
    def uploadMediaByE2EE(
        self,
        pathOrBytes,
        oType="image",
        to=None,
    ):
        subresource = {
            "preview": "ud-preview",
            "hash": "ud-hash",
        }
        serviceName = "talk"
        obsNamespace, contentType = MediaNextTypeSets[oType]
        params = {"type": "file"}  # bin file
        if oType == "gif":
            params["cat"] = "original"
        if to is not None:
            if self.client.getToType(to) == 4:
                raise NotImplementedError("Not support for Open Chat.")
            ekm, efile = self.client.encryptByKeyMaterial(pathOrBytes)
            tempId = "reqid-" + str(uuid.uuid4())
            obsObjId, obsHash, respHeaders = self.uploadObjectForService(
                efile,
                "file",
                f"{serviceName}/{obsNamespace}/{tempId}",
                params=params,
            )
            obsObjId2, _, _ = self.uploadObjectForService(
                efile,
                "file",
                f"{serviceName}/{obsNamespace}/{obsObjId}__" + subresource["preview"],
                params={},
            )  # upload preview img
            assert obsObjId == obsObjId2
            chunks = self.client.encryptE2EEMessage(
                to, {"keyMaterial": ekm}, contentType=1
            )
            msg = self.client.sendMessage(
                to,
                None,
                contentType,
                {
                    "SID": obsNamespace,
                    "OID": obsObjId,
                    "e2eeVersion": "2",
                    "MEDIA_CONTENT_INFO": json.dumps(
                        {
                            "category": "original",
                            "fileSize": len(efile),
                            "extension": "jpg",
                            "animated": oType == "gif",
                        }
                    ),
                },
                chunk=chunks,
            )
        else:
            raise ValueError("`to` is required.")
