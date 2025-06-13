from typing import TYPE_CHECKING, List, Literal, Optional

from ..base import BaseBIZApi
from .internal.define_typed.Album import TAlbumPhoto

if TYPE_CHECKING:
    from ...client import CHRLINE


class Album(BaseBIZApi):

    def __init__(self, client: "CHRLINE", version: int):
        super().__init__(client, version=version, prefix="/ext/album")

    @property
    def token(self):
        return self.client.biz.token_with_timeline

    @property
    def headers(self):
        return self.client.biz.headers_with_timeline

    def ext_headers(self, *, chatId: Optional[str] = None):
        hr = {}
        if chatId is not None:
            hr["x-line-chat-id"] = chatId
        else:
            hr["x-line-album-referrer"] = "MOA"
        return self.client.server.additionalHeaders(self.headers, hr)

    def url(self, path: str, *, version: Optional[int] = None, prefix: str = "albums"):
        if version is not None:
            return super().url_with_prefix(f"/api/v{version}/{prefix}" + path)
        return super().url(f"/{prefix}" + path)

    def url_with_moa(self, path: str):
        return super().url_with_prefix("/moa/v2" + path)

    def get_hidden_chats(self):
        r = self.request(
            "GET", self.url_with_moa("/users/hiddenChats"), headers=self.headers
        )
        return r.json()

    def hide_chat(self, chatId: str):
        data = {"chatId": chatId}
        r = self.request(
            "POST",
            self.url_with_moa("/users/hiddenChats/create"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def delete_hidden_chat(self, chatId: str):
        data = {"chatId": chatId}
        r = self.request(
            "POST",
            self.url_with_moa("/users/hiddenChats/delete"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_moa_albums(
        self,
        *,
        cursor: str,
        orderBy: Literal["createTimeDesc", "updateTimeDesc"],
        include: str,
    ):
        params = {"cursor": cursor, "orderBy": orderBy, "include": include}
        r = self.request(
            "GET",
            self.url_with_moa("/albums"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_moa_photos(
        self,
        *,
        cursor: str,
        include: str,
    ):
        params = {"cursor": cursor, "include": include}
        r = self.request(
            "GET",
            self.url_with_moa("/photos"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def get_album(self, chatId: str, *, albumId: int, syncRevision: int):
        params = {"syncRevision": syncRevision}
        hr = self.ext_headers(chatId=chatId)
        r = self.request(
            "GET",
            self.url(f"/{albumId}"),
            headers=hr,
            params=params,
        )
        return r.json()

    def share_to_chat(self, chatId: str, *, albumId: int):
        # method: POST
        hr = self.ext_headers(chatId=chatId)
        r = self.request("POST", self.url(f"/{albumId}/share"), headers=hr)
        return r.json()

    def get_album_photos(
        self,
        chatId: str,
        *,
        albumId: int,
        cursor: str,
        pageSize: int,
        orderBy: Literal["createTimeDesc", "shotTimeDesc"],
        include: str,
        filterType: str,
        targetUserMid: Optional[str] = None,
    ):
        # version: v6
        params = {
            "cursor": cursor,
            "pageSize": pageSize,
            "orderBy": orderBy,
            "include": include,
            "filterType": filterType,
            "targetUser": targetUserMid,
        }
        hr = self.ext_headers(chatId=chatId)
        r = self.request(
            "GET", self.url(f"/{albumId}/photos", version=6), headers=hr, params=params
        )
        return r.json()

    def fetch_albums(self, chatId: str, *, syncRevision: str, markReading: bool):
        # version: v5
        # path: /albums
        params = {"syncRevision": syncRevision, "markReading": markReading}
        hr = self.ext_headers(chatId=chatId)
        r = self.request("GET", self.url(""), headers=hr, params=params)
        return r.json()

    def fetch_albums_v6(self, chatId: str, *, cursor: str, pageSize: int):
        # version: v6
        # path: /albums
        params = {"cursor": cursor, "pageSize": pageSize}
        hr = self.ext_headers(chatId=chatId)
        r = self.request("GET", self.url("", version=6), headers=hr, params=params)
        return r.json()

    def get_preview_albums(
        self,
        chatId: str,
        *,
        cursor: str,
        pageSize: int,
        viewType: Literal["chatMenu", "selectAlbum"],
        thumbnailCount: int = 1,
    ):
        # version: v6
        # path: /albums
        params = {
            "cursor": cursor,
            "pageSize": pageSize,
            "thumbnailCount": thumbnailCount,
            "viewType": viewType,
        }
        hr = self.ext_headers(chatId=chatId)
        r = self.request(
            "GET", self.url("/preview", version=6), headers=hr, params=params
        )
        return r.json()

    def get_album_promotion_item(
        self,
        *,
        country: str,
        language: int,
        isPremium: bool,
        os: str = "Android",
    ):
        params = {
            "country": country,
            "language": language,
            "isPremium": isPremium,
            "os": os,
        }
        r = self.request(
            "GET",
            self.url_with_prefix("/support/v1/promotion"),
            headers=self.headers,
            params=params,
        )
        return r.json()

    def agree_terms(self, *, version: int):
        data = {"version": version}
        r = self.request(
            "POST",
            self.url("/lypPremium/terms/agree", prefix="user"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_agreement_status(self):
        r = self.request(
            "GET",
            self.url("/lypPremium/latestTerms", prefix="user"),
            headers=self.headers,
        )
        return r.json()

    def get_album_id(self, chatId: str, *, legacyAlbumId: int):
        params = {"legacyAlbumId": legacyAlbumId}
        hr = self.ext_headers(chatId=chatId)
        r = self.request("GET", self.url("/id"), headers=hr, params=params)
        return r.json()

    def add_photos(self, chatId: str, *, albumId: int, photos: List[TAlbumPhoto]):
        data = {"photos": photos}
        hr = self.ext_headers(chatId=chatId)
        r = self.request(
            "POST", self.url(f"{albumId}/photos/create"), headers=hr, json=data
        )
        return r.json()

    def create_album(self, chatId: str, *, title: str, modifyDuplicateTitle: bool):
        params = {"modifyDuplicateTitle": modifyDuplicateTitle}
        data = {"title": title}
        hr = self.ext_headers(chatId=chatId)
        r = self.request(
            "POST", self.url("/create"), headers=hr, params=params, json=data
        )
        return r.json()

    def delete_album(self, chatId: str, *, albumId: int):
        # method: POST
        hr = self.ext_headers(chatId=chatId)
        r = self.request("POST", self.url(f"/{albumId}/delete"), headers=hr)
        return r.json()

    def delete_photos(self, chatId: str, *, albumId: int, photoIds: List[int]):
        data = {"photoIds": photoIds}
        hr = self.ext_headers(chatId=chatId)
        r = self.request(
            "POST", self.url(f"/{albumId}/photos/delete"), headers=hr, json=data
        )
        return r.json()

    def update_album(self, chatId: str, *, albumId: int, title: str):
        data = {"title": title}
        hr = self.ext_headers(chatId=chatId)
        r = self.request("POST", self.url(f"/{albumId}/update"), headers=hr, json=data)
        return r.json()
