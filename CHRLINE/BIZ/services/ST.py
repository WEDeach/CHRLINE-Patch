from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from ..base import BaseBIZApi
from .internal.define_typed.Story import TStoryIndexWithGuildId, TStoryIndexWithUserMid

if TYPE_CHECKING:
    from ...client import CHRLINE


class Story(BaseBIZApi):

    def __init__(self, client: "CHRLINE", version: int):
        super().__init__(client, version=version, prefix="/st")

    @property
    def token(self):
        return self.client.biz.token_with_timeline

    @property
    def headers(self):
        return self.client.biz.headers_with_timeline

    def url(self, path: str):
        return super().url("/story" + path)

    def delete_content(self, contentId: str):
        data = {"contentId": contentId}
        r = self.request(
            "POST",
            self.url("/content/delete"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_challenge_contents(
        self,
        guideId: str,
        direction: str,
        *,
        popularContentIds: Optional[list] = None,
        lastContentSeq: Optional[int] = None,
        size: int = 10,
    ):
        data = {
            "guideId": guideId,
            "direction": direction,
            "size": size,
        }
        if lastContentSeq is not None:
            data["lastContentSeq"] = lastContentSeq
        if popularContentIds is not None:
            data["popularContentIds"] = popularContentIds
        r = self.request(
            "POST",
            self.url("/story/challenge/content/list"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_recent_storys(
        self,
        lastRequestTime: int,
        *,
        lastTimelineVisitTime: Optional[int] = None,
        oaList: Optional[list] = None,
    ):
        data: Dict[str, Any] = {"lastRequestTime": lastRequestTime}
        if lastTimelineVisitTime is not None:
            data["lastTimelineVisitTime"] = lastTimelineVisitTime
        if oaList is not None:
            data["oaList"] = oaList
        r = self.request(
            "POST",
            self.url("/recentstory/list"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_recommend_lights(self, *, scrollId: str = ""):
        data: Dict[str, Any] = {"scrollId": scrollId}
        r = self.request(
            "POST",
            self.url("/recommend-lights"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def share_story(
        self, contentId: str, *, shareGroupIds: List[str], shareType: str = "PUBLIC"
    ):
        shareInfo = {"shareType": shareType, "shareGroupIds": shareGroupIds}
        data: Dict[str, Any] = {"contentId": contentId, "shareInfo": shareInfo}
        r = self.request(
            "POST",
            self.url("/oa/share"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_story_likes(
        self,
        userMid: str,
        contentId: str,
        *,
        scrollId: Optional[str] = None,
        size: Optional[int] = None,
        include: Optional[str] = None,
        likeType: Optional[str] = None,
    ):
        opts = ["scrollId", "size", "include", "likeType"]
        data: Dict[str, Any] = {"userMid": userMid, "contentId": contentId}
        for opt in opts:
            if locals()[opt] is not None:
                data[opt] = locals()[opt]
        r = self.request(
            "POST",
            self.url("/content/like/list"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_recent_oa_story(self, *, lastRequestTime: int, oaList: List[str]):
        data: Dict[str, Any] = {"lastRequestTime": lastRequestTime, "oaList": oaList}
        r = self.request(
            "POST",
            self.url("/oa/recentstory/list"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_oa_content(self, contentId: str):
        data: Dict[str, Any] = {"contentId": contentId}
        r = self.request(
            "POST",
            self.url("/oa/content"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_guide(self, guideId: str):
        data: Dict[str, Any] = {"guideId": guideId}
        r = self.request(
            "POST",
            self.url("/guide"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_list(
        self,
        *,
        userInfos: Optional[
            List[Union[TStoryIndexWithUserMid, TStoryIndexWithGuildId]]
        ],
        guideInfos: Optional[
            List[Union[TStoryIndexWithUserMid, TStoryIndexWithGuildId]]
        ],
        recommendUserInfos: Optional[
            List[Union[TStoryIndexWithUserMid, TStoryIndexWithGuildId]]
        ],
        clickedGuideInfo: Optional[
            Union[TStoryIndexWithUserMid, TStoryIndexWithGuildId]
        ],
        clickedUserInfo: Optional[
            Union[TStoryIndexWithUserMid, TStoryIndexWithGuildId]
        ],
        clickedRecommendUserInfo: Optional[
            Union[TStoryIndexWithUserMid, TStoryIndexWithGuildId]
        ],
        includeRecommendLights: bool,
    ):
        data: Dict[str, Any] = {
            "userInfos": userInfos,
            "guideInfos": guideInfos,
            "recommendUserInfos": recommendUserInfos,
            "clickedUserInfo": clickedUserInfo,
            "clickedGuideInfo": clickedGuideInfo,
            "clickedRecommendUserInfo": clickedRecommendUserInfo,
            "includeRecommendLights": includeRecommendLights,
        }
        r = self.request(
            "POST",
            self.url("/list"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_new_story(
        self,
        *,
        newStoryTypes: List[
            Literal[
                "WRITE",
                "MY",
                "GUIDE",
                "CHALLENGE",
                "USER",
                "ARCHIVE",
                "LIVE",
                "INVALID",
                "RECOMMEND_LIGHTS",
                "OA",
                "OA_SHARE",
                "OA_RECOMMENDATION",
            ]
        ],
        lastTimelineVisitTime: int,
    ):
        data: Dict[str, Any] = {
            "newStoryTypes": newStoryTypes,
            "lastTimelineVisitTime": lastTimelineVisitTime,
        }
        r = self.request(
            "POST",
            self.url("/newstory"),
            headers=self.headers,
            json=data,
        )
        return r.json()
