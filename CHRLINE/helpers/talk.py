# -*- coding: utf-8 -*-
import json
import time
from typing import Any, Dict, List, Optional

import qrcode
from qrcode.constants import ERROR_CORRECT_L

from .base import BaseHelper


class TalkHelper(BaseHelper):
    def __init__(self):
        pass

    def getProfileCoverObjIdAndUrl(self, mid: str):
        url = None
        pic_oid = None
        video_oid = None
        video_url = None
        detail = self.client.getProfileCoverDetail(mid)["result"]
        coverObsInfo = self.client.checkAndGetValue(
            detail, "coverObsInfo"
        )  # detail['coverObsInfo']
        videoCoverObsInfo = self.client.checkAndGetValue(
            detail, "videoCoverObsInfo"
        )  # detail['videoCoverObsInfo']
        if coverObsInfo is not None:
            pic_oid = coverObsInfo["objectId"]
            url = (
                self.client.LINE_OBS_DOMAIN
                + f'/r/{coverObsInfo["serviceName"]}/{coverObsInfo["obsNamespace"]}/{pic_oid}'
            )
        if videoCoverObsInfo is not None:
            video_oid = videoCoverObsInfo["objectId"]
            video_url = (
                self.client.LINE_OBS_DOMAIN
                + f'/r/{videoCoverObsInfo["serviceName"]}/{videoCoverObsInfo["obsNamespace"]}/{videoCoverObsInfo["objectId"]}'
            )
        return url, video_url, pic_oid, video_oid

    def getProfilePictureObjIdAndUrl(self, mid: str):
        url = None
        url_video = None
        objectId = mid
        objectId_video = None
        serviceName = "talk"
        obsNamespace = None
        midType = self.client.getToType(mid)
        if midType == 0:
            obsNamespace = "p"
            objectId_video = f"{mid}/vp"
            # vp.sjpg, vp.small
        elif midType in [1, 2]:
            obsNamespace = "g"
        elif midType in [3, 4, 5]:
            serviceName = "g2"
            obsNamespace = "group"
            if midType == 5:
                obsNamespace = "member"
        else:
            raise ValueError(f"Not support midType: {midType}")
        url = (
            self.client.LINE_OBS_DOMAIN + f"/r/{serviceName}/{obsNamespace}/{objectId}"
        )
        if objectId_video is not None:
            url_video = (
                self.client.LINE_OBS_DOMAIN
                + f"/r/{serviceName}/{obsNamespace}/{objectId_video}"
            )
        return url, url_video, objectId, objectId_video

    def genQrcodeImageAndPrint(
        self,
        url: str,
        filename: Optional[str] = None,
        output_char: Optional[List[str]] = None,
    ):
        if output_char is None:
            output_char = ["　", "■"]
        if filename is None:
            filename = str(time.time())
        savePath = self.client.getSavePath(".images")
        savePath = savePath + f"/qr_{filename}.png"
        qr = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_L,
        )
        qr.add_data(url)
        qr.make()

        def win_qr_make(x, c: List[str]):
            return print(
                "".join([c[1]] + [c[0] if y is True else c[1] for y in x] + [c[1]])
            )

        # 如果你問我問啥要加這段, 我可以告訴你fk u line >:( 你可以看到qr外面有一圈, 這是讓line讀到的必要條件(啊明明就可以不用 line的判定有夠爛)
        if qr.modules:
            fixed_bored = [False for _b in range(len(qr.modules[0]))]
            for qr_module in [fixed_bored] + qr.modules + [fixed_bored]:
                win_qr_make(qr_module, output_char)
        img = qr.make_image()
        img.save(savePath)
        return savePath

    def sendMention(self, to, text="", mids=[], prefix=True):
        if not isinstance(mids, list):
            mids = [mids]
        tag = "@chrline"
        str_tag = "@!"
        arr_data = []
        if mids == []:
            raise ValueError(f"Invalid mids: {mids}")
        if str_tag not in text:
            message = text if prefix else ""
            for mid in mids:
                slen = len(message)
                elen = len(message) + len(tag)
                arr = {"S": str(slen), "E": str(elen), "M": mid}
                arr_data.append(arr)
                message += tag
            if not prefix:
                message += text
        else:
            if text.count(str_tag) != len(mids):
                raise ValueError(
                    f"Invalid tag length: {text.count(str_tag)}/{len(mids)}"
                )
            text_data = text.split(str_tag)
            message = ""
            for mid in mids:
                message += str(text_data[mids.index(mid)])
                slen = len(message)
                elen = len(message) + len(tag)
                arr = {"S": str(slen), "E": str(elen), "M": mid}
                arr_data.append(arr)
                message += tag
            message += text_data[-1]
        return self.client.sendMessage(
            to,
            message,
            contentMetadata={
                "MENTION": str('{"MENTIONEES":' + json.dumps(arr_data) + "}")
            },
        )

    def getMentioneesByMsgData(self, msg: dict):
        a = []
        b = self.client.checkAndGetValue(msg, "contentMetadata", 18)
        if b is not None:
            if "MENTION" in b:
                c = json.loads(b["MENTION"])
                print(c)
                for _m in c["MENTIONEES"]:
                    print(_m["M"])
                    a.append(_m["M"])
        return a

    def genMentionData(self, mentions: List[Dict[str, Any]]):
        """
        - mentions:
            - S: index
            - L: len
            - M: mid
            - A: ALL
        """
        if mentions is None or len(mentions) == 0:
            return None
        a = []
        for b in mentions:
            c = {}
            d = False
            if "A" in b:
                d = True
            c["S"] = str(b["S"])
            c["E"] = str(b["S"] + b["L"])
            if d:
                c["A"] = str(1)
            else:
                c["M"] = str(b["M"])
            a.append(c)
        a = {"MENTIONEES": a}
        return {"MENTION": json.dumps(a)}
