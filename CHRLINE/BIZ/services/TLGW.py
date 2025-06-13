from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from ..base import BaseBIZApi
from .internal.define_typed.Post import TPostContents, TPostInfo, TPostLightsContents

if TYPE_CHECKING:
    from ...client import CHRLINE


class TimelineGateway(BaseBIZApi):

    def __init__(self, client: "CHRLINE", version: int):
        super().__init__(client, version=version, prefix="/ext/timeline/tlgw")

    @property
    def token(self):
        return self.client.biz.token_with_timeline

    @property
    def headers(self):
        return self.client.biz.headers_with_timeline

    def url(self, path: str):
        return f"{self.prefix}" + path

    def get_live_scheduler_data(self, topFixedBroadcastId: str, *, testParam: str = ""):
        params = {"testParam": testParam, "topFixedBroadcastId": topFixedBroadcastId}
        r = self.request(
            "GET",
            self.url("/live/api/v1/schedules"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def close_live_pr_banner(self, broadcastId: str):
        data = {"broadcastId": broadcastId}
        r = self.request(
            "POST",
            self.url("/live/api/v1/pr-banner/close"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_relation_type(self, broadcastId: str, *, inflowType: str):
        params = {"broadcastId": broadcastId, "inflowType": inflowType}
        r = self.request(
            "GET",
            self.url("/live/api/v1/player"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def consent_live(self):
        r = self.request("POST", self.url("/live/api/v1/consent"), headers=self.headers)
        return r.json()

    def get_live_link_banner(self, broadcastId: str):
        params = {"broadcastId": broadcastId}
        r = self.request(
            "GET",
            self.url("/live/api/v1/link-banner"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_broadcaster_profile(self, broadcastId: str):
        params = {"broadcastId": broadcastId}
        r = self.request(
            "GET",
            self.url("/live/api/v1/broadcaster/profile"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_live_gnb_on_air_state(self, *, gnbTarget: str = "REGION"):
        params = {"gnbTarget": gnbTarget}
        r = self.request(
            "GET",
            self.url("/live/api/v1/global/on-air/state"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def fetch_favorite_musics(self, scrollId: int, size: int):
        params = {"scrollId": scrollId, "size": size}
        r = self.request(
            "GET",
            self.url("/sfv/api/v1/music/favorite/list"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def check_music_available(self):
        r = self.request(
            "GET", self.url("/sfv/api/v1/music/activation/check"), headers=self.headers
        )
        return r.json()

    def check_deco_validate(
        self,
        *,
        effectIds: list,
        stickerIds: list,
        sticonIds: list,
        templateIds: list,
        trackIds: list,
    ):
        data = {
            "effectIds": effectIds,
            "stickerIds": stickerIds,
            "sticonIds": sticonIds,
            "templateIds": templateIds,
            "trackIds": trackIds,
        }
        r = self.request(
            "POST",
            self.url("/sfv/api/v1/deco/validity/check"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def share_effect_to_chat(self, receiveMids: List[str], effectId: int):
        data = {"receiveMids": receiveMids, "effectId": effectId}
        r = self.request(
            "POST",
            self.url("/ccs/api/v1/share/chatroom/effect"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def share_music_to_chat(self, receiveMids: List[str], trackId: str):
        data = {"receiveMids": receiveMids, "trackId": trackId}
        r = self.request(
            "POST",
            self.url("/ccs/api/v1/share/chatroom/music"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_catalog_effect_list(self, effectId: int, scrollId: str):
        params = {"effectId": effectId, "scrollId": scrollId}
        r = self.request(
            "GET",
            self.url("/ccs/api/v1/catalog/list/effect"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_catalog_music_list(self, trackId: str, scrollId: str):
        params = {"trackId": trackId, "scrollId": scrollId}
        r = self.request(
            "GET",
            self.url("/ccs/api/v1/catalog/list/music"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def add_favorite_music(self, trackIds: List[str]):
        data = {"trackIds": trackIds}
        r = self.request(
            "POST",
            self.url("/sfv/api/v1/music/favorite/add"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def delete_favorite_music(self, trackIds: List[str]):
        data = {"trackIds": trackIds}
        r = self.request(
            "POST",
            self.url("/sfv/api/v1/music/favorite/delete"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_music_track_download_url(self, trackId: str):
        params = {"trackId": trackId}
        r = self.request(
            "GET",
            self.url("/sfv/api/v1/music/track/downloadUrl"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_music_category_list(self, moduleId: str):
        params = {"moduleId": moduleId}
        r = self.request(
            "GET",
            self.url("/sfv/api/v1/music/module/category"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_music_category_list_without_module_id(self):
        r = self.request(
            "GET", self.url("/sfv/api/v1/music/category/list"), headers=self.headers
        )
        return r.json()

    def get_music_list_components(self):
        r = self.request(
            "GET", self.url("/sfv/api/v1/music/main"), headers=self.headers
        )
        return r.json()

    def get_music_tracks(self, trackId: str):
        params = {"trackId": trackId}
        r = self.request(
            "GET",
            self.url("/sfv/api/v1/music/track"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_music_category_track_list(self, categoryId: int, scrollId: int, size: int):
        params = {"categoryId": categoryId, "scrollId": scrollId, "size": size}
        r = self.request(
            "GET",
            self.url("/sfv/api/v1/music/category/track/list"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_lights_with_write(
        self,
        *,
        effectIds: list,
        stickerIds: list,
        sticonIds: list,
        templateIds: list,
        trackIds: list,
        shopStickers: Optional[list],
    ):
        data = {
            "effectIds": effectIds,
            "stickerIds": stickerIds,
            "sticonIds": sticonIds,
            "templateIds": templateIds,
            "trackIds": trackIds,
        }
        if shopStickers is not None:
            data["shopStickers"] = shopStickers
        r = self.request(
            "POST",
            self.url("/sfv/api/v1/lights/writePage"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_lights_content_download_url(self, lightsId: str):
        params = {"lightsId": lightsId}
        hr = self.client.server.additionalHeaders(
            self.headers, {"X-Line-Caller-Platform": "APP"}
        )
        r = self.request(
            "POST",
            self.url("/sfv/api/v1/lights/download/hash"),
            headers=hr,
            params=params,
        )
        return r.json()

    def update_lights_post(
        self,
        homeId: str,
        *,
        postInfo: TPostInfo,
        contents: TPostContents,
        lightsId: str,
        allowDownload: Literal["ALLOW", "DISALLOW", "NOT_SUPPORTED"],
    ):
        data = {
            "homeId": homeId,
            "postInfo": postInfo,
            "contents": contents,
            "lightsId": lightsId,
            "allowDownload": allowDownload,
        }
        r = self.request(
            "POST",
            self.url("/sfv/api/v1/lights/update"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def create_lights_post(
        self,
        homeId: str,
        *,
        ruid: str,
        postInfo: TPostInfo,
        contents: TPostContents,
        lightsContents: TPostLightsContents,
        publishType: Literal["CAMERA", "PICKER", "CAMERA_PICKER"],
        allowDownload: Literal["ALLOW", "DISALLOW", "NOT_SUPPORTED"],
        templateId: int,
        postOrigin: str = "",
    ):
        params = {"ruid": ruid}
        data = {
            "homeId": homeId,
            "postInfo": postInfo,
            "contents": contents,
            "lightsContents": lightsContents,
            "publishType": publishType,
            "allowDownload": allowDownload,
            "templateId": templateId,
        }
        hr = self.client.server.additionalHeaders(
            self.headers, {"X-Voom-Post-Origin": postOrigin}
        )
        r = self.request(
            "POST",
            self.url("/sfv/api/v1/lights/create"),
            headers=hr,
            params=params,
        )
        return r.json()

    def agree_to_edit_privacy(self, mid: str):
        data = {"mid": mid}
        r = self.request(
            "POST",
            self.url("/sana/front/v1/user/privacy/agreement/add"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_edit_privacy_agreement(self, mid: str):
        data = {"mid": mid}
        r = self.request(
            "POST",
            self.url("/sana/front/v1/user/privacy/agreement/get"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_remote_user_mention_suggestion_list(self, mid: str):
        data = {"mid": mid}
        r = self.request(
            "POST",
            self.url("/um/api/v1/mention/suggestion/users"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def delete_remote_recent_mention_user(self, actor: str, receiver: str):
        data = {"actor": actor, "receiver": receiver}
        r = self.request(
            "POST",
            self.url("/um/api/v1/mention/history/delete"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def request_mention_build_cache(self, actor: str):
        data = {"actor": actor}
        r = self.request(
            "POST",
            self.url("/um/api/v1/mention/cache/build"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_remote_user_mention_suggestion_list_by_keyword(
        self, mid: str, *, keyword: str, contactList: List[str] = []
    ):
        data = {"mid": mid, "keyword": keyword, "contactList": contactList}
        r = self.request(
            "POST",
            self.url("/um/api/v1/mention/suggestion/keyword/users"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def add_voom_block(self, toMid: str):
        data = {"toMid": toMid}
        r = self.request(
            "POST",
            self.url("/vf/api/v1/voom-block/add"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def delete_voom_block(self, toMid: str):
        data = {"toMid": toMid}
        r = self.request(
            "POST",
            self.url("/vf/api/v1/voom-block/delete"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_voom_block_profiles(self, cursor: Optional[str] = None):
        data = {}
        if cursor is not None:
            data["cursor"] = cursor
        r = self.request(
            "POST",
            self.url("/vf/api/v1/voom-block/profiles"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_follow_settings(self):
        data = {}
        r = self.request(
            "POST",
            self.url("/vf/api/v1/follow/setting"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def update_follow_setting(
        self,
        *,
        enableAllowFollow: Optional[bool] = None,
        enableShowFollow: Optional[bool] = None,
    ):
        data = {}
        if enableAllowFollow is None and enableShowFollow is None:
            raise ValueError("enableAllowFollow, enableShowFollow are null")
        if enableAllowFollow is not None:
            data["enableAllowFollow"] = enableAllowFollow
        if enableShowFollow is not None:
            data["enableShowFollow"] = enableShowFollow
        r = self.request(
            "POST",
            self.url("/vf/api/v1/follow/setting/update"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def add_follow(self, *, toMid: Optional[str] = None, toEmid: Optional[str] = None):
        data = {}
        if toMid is None and toEmid is None:
            raise ValueError("toMid, toEmid are null")
        if toMid is not None:
            data["toMid"] = toMid
        if toEmid is not None:
            data["toEmid"] = toEmid
        r = self.request(
            "POST",
            self.url("/vf/api/v1/user/follow/add"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def delete_follow(
        self, *, toMid: Optional[str] = None, toEmid: Optional[str] = None
    ):
        data = {}
        if toMid is None and toEmid is None:
            raise ValueError("toMid, toEmid are null")
        if toMid is not None:
            data["toMid"] = toMid
        if toEmid is not None:
            data["toEmid"] = toEmid
        r = self.request(
            "POST",
            self.url("/vf/api/v1/user/follow/delete"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def delete_follower(
        self, *, toMid: Optional[str] = None, toEmid: Optional[str] = None
    ):
        data = {}
        if toMid is None and toEmid is None:
            raise ValueError("toMid, toEmid are null")
        if toMid is not None:
            data["toMid"] = toMid
        if toEmid is not None:
            data["toEmid"] = toEmid
        r = self.request(
            "POST",
            self.url("/vf/api/v1/user/follower/delete"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_following_profiles(self, cursor: Optional[str] = None):
        data = {}
        if cursor is not None:
            data["cursor"] = cursor
        r = self.request(
            "POST",
            self.url("/vf/api/v1/user/following/profiles"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_follower_profiles(self, cursor: Optional[str] = None):
        data = {}
        if cursor is not None:
            data["cursor"] = cursor
        r = self.request(
            "POST",
            self.url("/vf/api/v1/user/follower/profiles"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def update_share_list(
        self,
        ownerMid: str,
        sid: str,
        name: str,
        *,
        addMembers: Optional[List[str]] = None,
        delMembers: Optional[List[str]] = None,
    ):
        data: dict[str, Any] = {"ownerMid": ownerMid, "sid": sid, "name": name}
        if addMembers is not None:
            data["addMembers"] = addMembers
        if delMembers is not None:
            data["delMembers"] = delMembers
        r = self.request(
            "POST",
            self.url("/sl/api/v2/sharelist/update"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def create_share_list(self, ownerMid: str, name: str, *, members: List[str]):
        data: dict[str, Any] = {"ownerMid": ownerMid, "members": members, "name": name}
        r = self.request(
            "POST",
            self.url("/sl/api/v2/sharelist/create"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def sync_share_list(self, ownerMid: str, *, lastUpdated: int):
        data: dict[str, Any] = {"ownerMid": ownerMid, "lastUpdated": lastUpdated}
        r = self.request(
            "POST",
            self.url("/sl/api/v2/sharelist/sync"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def sync_share_list_member(self, ownerMid: str, *, sids: List[str]):
        sparams = []
        for sid in sids:
            sparams.append({"sid": sid, "memberUpdated": "0"})
        data: dict[str, Any] = {"ownerMid": ownerMid, "sparams": sparams}
        r = self.request(
            "POST",
            self.url("/sl/api/v2/sharelist/syncMember"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_share_list_member(self, ownerMid: str, *, sid: str):
        params = {"ownerMid": ownerMid, "sid": sid}
        r = self.request(
            "GET",
            self.url("/sl/api/v2/sharelist/members"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def delete_share_list(self, ownerMid: str, *, sid: str):
        data = {"ownerMid": ownerMid, "sid": sid}
        r = self.request(
            "POST",
            self.url("/sl/api/v2/sharelist/delete"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_initial_comments(
        self,
        contentId: str,
        *,
        includes: List[Dict[Literal["type", "limit"], Union[str, int]]] = [],
    ):
        data = {"contentId": contentId, "includes": includes}
        r = self.request(
            "POST",
            self.url("/res/external/api/v1/reactions/get"),
            headers=self.headers,
            json=data,
        )
        return r.json()
