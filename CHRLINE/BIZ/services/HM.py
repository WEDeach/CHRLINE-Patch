from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from ..base import BaseBIZApi
from .internal.SocialProfile import SocialProfile

if TYPE_CHECKING:
    from ...client import CHRLINE


class MyHomeRenewal(BaseBIZApi):

    def __init__(self, client: "CHRLINE", version: int):
        super().__init__(client, version=version, prefix="/hm")

        self.socialprofile = SocialProfile(self)

    @property
    def token(self):
        return self.client.biz.token_with_timeline

    @property
    def headers(self):
        return self.client.biz.headers_with_timeline

    def url(self, path: str):
        return super().url("/home" + path)

    def get_user_profile(
        self,
        mid: str,
        *,
        profileId: Optional[str] = None,
        styleMediaVersion: str = "v3",
        storyVersion: str = "v7",
        timelineVersion: str = "v57",
        profileBannerRevision: int = 0,
        getPostCount: bool = False,
        clientCacheObsCoverId: Optional[str] = None,
        clientCachePutTime: Optional[int] = None,
        clientReferer: Optional[str] = "my_home",
    ):
        params = {
            "homeId": mid,
            "styleMediaVersion": styleMediaVersion,
            "storyVersion": storyVersion,
            "timelineVersion": timelineVersion,
            "profileBannerRevision": profileBannerRevision,
            "getPostCount": getPostCount,
        }
        if profileId is not None:
            params["profileId"] = profileId
        if (
            clientCacheObsCoverId is not None
            and clientCachePutTime is not None
            and clientReferer is not None
        ):
            params["clientCacheObsCoverId"] = clientCacheObsCoverId
            params["clientCachePutTime"] = clientCachePutTime
            params["clientReferer"] = clientReferer
        r = self.request(
            "GET", self.url("/profile.json"), headers=self.headers, params=params
        )
        return r.json()

    def update_user_profile(
        self,
        mid: str,
        displayName: str,
        *,
        profileId: Optional[str] = None,
        imageObjectId: Optional[str] = None,
        imageIsVideo: bool = False,
        coverSourceType: Optional[Literal["PROFILE", "PROFILE_DECO", "MUSIC"]] = None,
        coverImageObsNamespace: Optional[str] = None,
        coverImageServiceName: Optional[str] = None,
        coverImageObjectId: Optional[str] = None,
        coverImageHash: Optional[str] = None,
        coverVideoObsNamespace: Optional[str] = None,
        coverVideoServiceName: Optional[str] = None,
        coverVideoObjectId: Optional[str] = None,
        coverVideoHash: Optional[str] = None,
        styleMediaVersion: str = "v3",
        timelineVersion: str = "v57",
        storyShare: bool = False,
        getPostCount: bool = False,
    ):
        # TODO: the fuking many data structs
        profile: Dict[str, Any] = {"displayName": displayName}
        cover: Optional[Dict[str, Any]] = None
        if imageObjectId is not None:
            profile["image"] = {
                "serviceName": "talk",
                "obsNamespace": "p",
                "objectId": imageObjectId,
                "video": imageIsVideo,
            }
        if coverSourceType is not None:
            cover = {
                "coverSourceType": coverSourceType,
            }
            if coverImageObsNamespace is not None:
                cover["image"] = {
                    "serviceName": coverImageServiceName,
                    "obsNamespace": coverImageObsNamespace,
                    "objectId": coverImageObjectId,
                    "hash": coverImageHash,
                }
            if coverVideoObsNamespace is not None:
                cover["video"] = {
                    "serviceName": coverVideoServiceName,
                    "obsNamespace": coverVideoObsNamespace,
                    "objectId": coverVideoObjectId,
                    "hash": coverVideoHash,
                }
        data = {
            "homeId": mid,
            "styleMediaVersion": styleMediaVersion,
            "timelineVersion": timelineVersion,
            "userStyleMedia": {
                "profile": profile,
            },
            "cover": cover,
            "getPostCount": getPostCount,
            "storyShare": storyShare,
        }
        if profileId is not None:
            data["profileId"] = profileId
        r = self.request("POST", self.url("/profile"), headers=self.headers, json=data)
        return r.json()

    def get_default_cover(self):
        r = self.request("GET", self.url("/defaultcover"), headers=self.headers)
        return r.json()

    def get_group_profile_image(
        self,
        homeId: str,
        clientCacheObsCoverId: Optional[str] = None,
        clientCachePutTime: Optional[int] = None,
        clientReferer: Optional[str] = "my_home",
    ):
        params: Dict[str, Any] = {"homeId": homeId}
        if (
            clientCacheObsCoverId is not None
            and clientCachePutTime is not None
            and clientReferer is not None
        ):
            params["clientCacheObsCoverId"] = clientCacheObsCoverId
            params["clientCachePutTime"] = clientCachePutTime
            params["clientReferer"] = clientReferer
        r = self.request(
            "GET", self.url("/groupprofile.json"), headers=self.headers, params=params
        )
        return r.json()

    def get_group_profile_image_list_for_home_renewal(self):
        r = self.request(
            "GET", self.url("/groupprofile/defaultimages.json"), headers=self.headers
        )
        return r.json()

    def get_cover_renewal(
        self,
        mid: str,
        *,
        profileId: Optional[str] = None,
        clientCacheObsCoverId: Optional[str] = None,
        clientCachePutTime: Optional[int] = None,
        clientReferer: Optional[str] = "my_home",
    ):
        params: Dict[str, Any] = {"homeId": mid}
        if profileId is not None:
            params["profileId"] = profileId
        if (
            clientCacheObsCoverId is not None
            and clientCachePutTime is not None
            and clientReferer is not None
        ):
            params["clientCacheObsCoverId"] = clientCacheObsCoverId
            params["clientCachePutTime"] = clientCachePutTime
            params["clientReferer"] = clientReferer
        r = self.request(
            "GET", self.url("/cover.json"), headers=self.headers, params=params
        )
        return r.json()

    def update_cover_renewal(
        self,
        mid: str,
        *,
        profileId: Optional[str] = None,
        coverObjectId: Optional[str] = None,
        videoCoverObjectId: Optional[str] = None,
    ):
        data = {"homeId": mid}
        if profileId is not None:
            data["profileId"] = profileId
        if coverObjectId:
            data["coverObjectId"] = coverObjectId
        if videoCoverObjectId:
            data["videoCoverObjectId"] = videoCoverObjectId
        r = self.request(
            "POST", self.url("/cover.json"), headers=self.headers, json=data
        )
        return r.json()

    def delete_cover(self, mid: str, *, profileId: Optional[str] = None):
        data = {"homeId": mid}
        if profileId is not None:
            data["profileId"] = profileId
        r = self.request("DELETE", self.url("/cover"), headers=self.headers, json=data)
        return r.json()

    def send_profile(
        self,
        homeId: str,
        *,
        targetMids: List[str],
        shareType: str = "FLEX_OA_HOME_PROFILE_SHARING",
    ):
        data = {
            "homeId": homeId,
            "shareType": shareType,
            "targetMids": targetMids,
        }
        r = self.request(
            "POST", self.url("/profile/share"), headers=self.headers, json=data
        )
        return r.json()

    def get_profile_deco_menu_list(
        self,
        homeId: str,
        *,
        revision: int,
        _type: str,
        styleMediaVersion: str = "v3",
        service: str = "profile",
    ):
        data = {
            "homeId": homeId,
            "styleMediaVersion": styleMediaVersion,
            "service": service,
            "revision": revision,
            "type": _type,
        }
        r = self.request(
            "POST",
            self.url("/profile/decoration/menu"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_apng_effect_resource(
        self, *, effectId: int, categoryId: str, styleMediaVersion: str = "v3"
    ):
        params = {
            "effectId": effectId,
            "categoryId": categoryId,
            "styleMediaVersion": styleMediaVersion,
        }
        r = self.request(
            "GET",
            self.url("/profile/decoration/effect"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_fonts(self):
        r = self.request("GET", self.url("/fonts"), headers=self.headers)
        return r.json()

    def get_birthday_board_id(self, homeId: str):
        params = {"homeId": homeId}
        headers = self.client.server.additionalHeaders(
            self.headers, {"X-Line-BDBTemplateVersion": "v1"}
        )
        r = self.request(
            "GET", self.url("/getBirthdayBoardId.json"), headers=headers, params=params
        )
        return r.json()

    def get_social_profile_media_post(
        self,
        homeId: str,
        *,
        postId: Optional[str] = None,
        updatedTime: Optional[int] = None,
        postLimit: Optional[int] = None,
    ):
        params: Dict[str, Any] = {"homeId": homeId}
        if postId is not None and updatedTime is not None:
            params["postId"] = postId
            params["updatedTime"] = updatedTime
        if postLimit is not None:
            params["postLimit"] = postLimit
        r = self.request(
            "GET",
            self.url_with_prefix(
                "/api/v2/home/socialprofile/more-videopost"
            ),  # IDK why it uses v2.
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_recent_story_content(self, homeId: str, *, storyVersion: str = "v12"):
        params = {"homeId": homeId, "storyVersion": storyVersion}
        r = self.request(
            "GET",
            self.url("/story/recentcontent.json"),
            headers=self.headers,
            params=params,
        )
        return r.json()
