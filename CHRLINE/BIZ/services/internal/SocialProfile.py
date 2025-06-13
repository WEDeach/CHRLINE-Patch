from typing import TYPE_CHECKING, Any, Dict, Literal, Optional

from .define_typed.Post import TPostReportReasonCode

if TYPE_CHECKING:
    from ..HM import MyHomeRenewal


class SocialProfile:

    def __init__(self, instance: "MyHomeRenewal"):
        self.instance = instance

    @property
    def headers(self):
        return self.instance.client.biz.headers_with_timeline

    def url(self, path: str):
        return self.instance.url("/socialprofile" + path)

    def get_post(
        self,
        mid,
        *,
        withSocialHomeInfo=True,
        postLimit=10,
        likeLimit=6,
        commentLimit=10,
        storyVersion: str = "v12",
        timelineVersion: str = "v57",
        postId=None,
        updatedTime=None,
    ):
        params = {
            "homeId": mid,
            "withSocialHomeInfo": withSocialHomeInfo,
            "postLimit": postLimit,
            "likeLimit": likeLimit,
            "commentLimit": commentLimit,
            "storyVersion": storyVersion,
            "timelineVersion": timelineVersion,
        }
        if postId is not None:
            # post offset
            params["postId"] = postId
            params["updatedTime"] = updatedTime
        r = self.instance.request(
            "GET", self.url("/post.json"), headers=self.headers, params=params
        )
        return r.json()

    def get_mediapost(
        self,
        mid,
        *,
        withSocialHomeInfo=True,
        postLimit=10,
        likeLimit=6,
        commentLimit=10,
        storyVersion: str = "v12",
        timelineVersion: str = "v57",
        postId=None,
        updatedTime=None,
    ):
        params = {
            "homeId": mid,
            "withSocialHomeInfo": withSocialHomeInfo,
            "postLimit": postLimit,
            "likeLimit": likeLimit,
            "commentLimit": commentLimit,
            "storyVersion": storyVersion,
            "timelineVersion": timelineVersion,
        }
        if postId is not None:
            # post offset
            params["postId"] = postId
            params["updatedTime"] = updatedTime
        r = self.instance.request(
            "GET", self.url("/mediapost.json"), headers=self.headers, params=params
        )
        return r.json()

    def send_oa_profile(
        self,
        homeId: str,
        *,
        targetMids: list,
        shareType: str = "FLEX_OA_HOME_PROFILE_SHARING",
    ):
        data = {
            "homeId": homeId,
            "shareType": shareType,
            "targetMids": targetMids,
        }
        r = self.instance.request(
            "POST", self.url("/share"), headers=self.headers, json=data
        )
        return r.json()

    def get_more_post_list(
        self,
        homeId: str,
        *,
        nextScrollId: str,
        withSocialHomeInfo: bool = False,
        postId: Optional[str] = None,
        updatedTime: Optional[int] = None,
        storyVersion: str = "v12",
        timelineVersion: str = "v57",
        adEnv: str = "",
    ):
        params: Dict[str, Any] = {
            "homeId": homeId,
            "withSocialHomeInfo": withSocialHomeInfo,
            "nextScrollId": nextScrollId,
            "storyVersion": storyVersion,
            "timelineVersion": timelineVersion,
        }
        if postId is not None and updatedTime is not None:
            params["postId"] = postId
            params["updatedTime"] = updatedTime
        hr = self.instance.client.server.additionalHeaders(
            self.headers, {"X-Ad-Environments", adEnv}
        )
        r = self.instance.request(
            "GET",
            self.url("/postWithAd.json"),
            headers=hr,
            params=params,
        )
        return r.json()

    def report_profile(
        self,
        homeId: str,
        *,
        reason: TPostReportReasonCode,
        accountType: Literal["OFFICIAL_ACCOUNT", "USER"],
    ):
        params: Dict[str, Any] = {
            "homeId": homeId,
            "reason": reason,
            "accountType": accountType,
        }
        r = self.instance.request(
            "GET", self.url("/report"), headers=self.headers, params=params
        )
        return r.json()
