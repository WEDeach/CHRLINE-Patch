from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..TL import Timeline


class Discover:

    def __init__(self, instance: "Timeline"):
        self.instance = instance

    @property
    def headers(self):
        return self.instance.client.biz.headers_with_timeline

    def url(self, path: str):
        return self.instance.url("/discover/api/v1" + path)

    def get_recommend_feeds(
        self,
        *,
        sourcePostId: Optional[int] = None,
        sessionId: Optional[str] = None,
        nextScrollId: Optional[int] = None,
        includeSourcePost: bool = False,
        contents: List[str] = ["CP", "PI", "PV", "PL", "LL"],
    ):
        data = {"includeSourcePost": includeSourcePost, "contents": contents}
        if sourcePostId is not None:
            data["sourcePostId"] = sourcePostId
        if sessionId is not None:
            data["sessionId"] = sessionId
        if nextScrollId is not None:
            data["nextScrollId"] = nextScrollId
        r = self.instance.request(
            "POST",
            self.url("/recommendFeeds"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_lights_recommend_feeds(
        self,
        *,
        scrollId: str,
        seedPostId: str,
        sessionId: str,
        includeSourcePost: bool = False,
        contents: List[str] = ["LS", "AD"],
        adEnv: str = "",
    ):
        data = {
            "scrollId": scrollId,
            "seedPostId": seedPostId,
            "sessionId": sessionId,
            "includeSourcePost": includeSourcePost,
            "contents": contents,
        }
        hr = self.instance.client.server.additionalHeaders(
            self.headers, {"X-Ad-Environments", adEnv}
        )
        r = self.instance.request(
            "POST",
            self.url("/lights/recommendFeeds"),
            headers=hr,
            json=data,
        )
        return r.json()

    def fetch_theme_detail_feeds(
        self,
        *,
        themeId: str,
        nextScrollId: Optional[int] = None,
        contents: List[str] = ["LS", "PV"],
    ):
        data = {"themeId": themeId, "contents": contents}
        if nextScrollId is not None:
            data["nextScrollId"] = nextScrollId
        r = self.instance.request(
            "POST",
            self.url("/theme/detail/feeds"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def fetch_theme_feeds(
        self,
        *,
        themeId: str,
        sessionId: str,
        includeThemeBarP1: bool,
        nextScrollId: str,
        contents: List[str] = ["LS", "AD", "PV"],
        topFixedFeedId: Optional[str] = None,
        topFixedFeedType: str = "POST",
        adEnv: str = "",
        referrer: str = "",
    ):
        topFixedFeed = None
        if topFixedFeedId is not None:
            topFixedFeed = {"id": topFixedFeedId, "type": topFixedFeedType}
        data = {
            "themeId": themeId,
            "contents": contents,
            "sessionId": sessionId,
            "includeThemeBarP1": includeThemeBarP1,
            "nextScrollId": nextScrollId,
            "topFixedFeed": topFixedFeed,
        }
        hr = self.instance.client.server.additionalHeaders(
            self.headers, {"X-Timeline-Referrer", referrer, "X-Ad-Environments", adEnv}
        )
        r = self.instance.request(
            "POST",
            self.url("/theme/feeds"),
            headers=hr,
            json=data,
        )
        return r.json()

    def get_theme_replace_ad_posts(self, *, replaceIds: List[str], adEnv: str = ""):
        data = {"replaceIds": replaceIds}
        hr = self.instance.client.server.additionalHeaders(
            self.headers, {"X-Ad-Environments", adEnv}
        )
        r = self.instance.request(
            "POST",
            self.url("/theme/feeds/ads"),
            headers=hr,
            json=data,
        )
        return r.json()

    def fetch_lights_hot_feeds(
        self,
        *,
        seedPostId: str,
        seedThemeId: str,
        sessionId: str,
        contents: List[str] = ["LS", "PV"],
    ):
        data = {
            "seedPostId": seedPostId,
            "seedThemeId": seedThemeId,
            "sessionId": sessionId,
            "contents": contents,
        }
        r = self.instance.request(
            "POST",
            self.url("/theme/collection/hot30/detail-viewer/feeds"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def request_live_bottom_sheet_thumbnail(self, broadcasterMid: str):
        data = {"broadcasterMid": broadcasterMid}
        r = self.instance.request(
            "POST",
            self.url("/live/more-contents/lights/thumbnails"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def fetch_recommend_tab_feeds(
        self,
        *,
        sourcePostId: Optional[int] = None,
        sessionId: Optional[str] = None,
        nextScrollId: Optional[int] = None,
        surelyRecommendFeed: bool = False,
        contents: List[str] = ["PV", "LS", "AD", "LP"],
        topFixedFeedType: Optional[str] = None,
        topFixedFeedId: Optional[str] = None,
    ):
        data = {"surelyRecommendFeed": surelyRecommendFeed, "contents": contents}
        if topFixedFeedType is not None and topFixedFeedId is not None:
            data["topFixedFeed"] = {"type": topFixedFeedType, "id": topFixedFeedId}
        if sessionId is not None:
            data["sessionId"] = sessionId
        if nextScrollId is not None:
            data["nextScrollId"] = nextScrollId
        r = self.instance.request(
            "POST",
            self.url("/recommendTab/feeds"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_recommend_tab_replace_ad_post(
        self, *, nextScrollId: str, replaceIds: List[str], adEnv: str = ""
    ):
        data = {"nextScrollId": nextScrollId, "replaceIds": replaceIds}
        hr = self.instance.client.server.additionalHeaders(
            self.headers, {"X-Ad-Environments", adEnv}
        )
        r = self.instance.request(
            "POST",
            self.url("/recommendTab/feeds/ads"),
            headers=hr,
            json=data,
        )
        return r.json()

    def hide_encourage_recommended_accounts(self, *, hide: bool):
        data = {"hide": hide}
        r = self.instance.request(
            "PUT",
            self.url("/encourage/recommendAccounts/hide"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_encourage_recommend_accounts_by_bottom_sheet(self):
        r = self.instance.request(
            "GET",
            self.url("/encourage/recommendation-accounts/bottom-sheet"),
            headers=self.headers,
        )
        return r.json()

    def exclude_encourage_recommend_accounts(self, mid: str, *, exclude: bool):
        params = {"mid": mid, "exclude": exclude}
        r = self.instance.request(
            "GET",
            self.url("/encourage/recommendation-accounts/exclude"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_encourage_recommend_accounts(
        self,
        *,
        sessionId: Optional[str] = None,
        nextScrollId: Optional[int] = None,
        topFixedRecommendationAccount: Optional[str] = None,
    ):
        params = {}
        if topFixedRecommendationAccount is not None:
            params["topFixedRecommendationAccount"] = topFixedRecommendationAccount
        if sessionId is not None:
            params["sessionId"] = sessionId
        if nextScrollId is not None:
            params["nextScrollId"] = nextScrollId
        r = self.instance.request(
            "GET",
            self.url("/encourage/recommendation-accounts"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def unconcern_author(self, authorMid: str, *, unconcern: bool = True):
        params = {"authorMid": authorMid, "unconcern": unconcern}
        r = self.instance.request(
            "GET", self.url("/unconcern/author"), headers=self.headers, params=params
        )
        return r.json()

    def unconcern_recommend_post(self, postId: int, *, unconcern: bool = True):
        data = {"unConcern": unconcern}
        r = self.instance.request(
            "PUT",
            self.url(f"/posts/{postId}/recommends/unConcern"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def search_collage_entry(
        self,
        *,
        sessionId: Optional[str] = None,
        nextScrollId: Optional[str] = None,
        fixedSlotType: Optional[str] = None,
        fixedSlotId: Optional[str] = None,
        contents: List[str] = ["CP", "PI", "PV", "PL", "LS"],
    ):
        data: Dict[str, Any] = {"contents": contents}
        if sessionId is not None:
            data["sessionId"] = sessionId
        if sessionId is not None:
            data["nextScrollId"] = nextScrollId
        if fixedSlotType is not None and fixedSlotId is not None:
            data["fixedSlot"] = {"id": fixedSlotId, "type": fixedSlotType}
        r = self.instance.request(
            "GET", self.url("/collage/searchEntry"), headers=self.headers, json=data
        )
        return r.json()
