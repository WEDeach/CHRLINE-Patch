from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from ..MH import MyHome
    from ..NT import Note


class Hashtag:

    def __init__(self, instance: Union["MyHome", "Note"]):
        self.instance = instance

    @property
    def headers(self):
        return self.instance.client.biz.headers_with_timeline

    def url(self, path: str):
        return self.instance.url("/hashtag" + path)

    def fetch_netacard_integrated_posts_full_period(
        self,
        visitorId: str,
        *,
        onlyIncluded: bool,
        query: str,
        postLimit: int,
        fullPeriodPostsSearchType: str,
        scrollId: Optional[str] = None,
    ):
        param = {"visitorId": visitorId}
        data = {
            "onlyIncluded": onlyIncluded,
            "query": query,
            "postLimit": postLimit,
            "fullPeriodPostsSearchType": fullPeriodPostsSearchType,
        }
        if scrollId is not None:
            data["scrollId"] = scrollId

        r = self.instance.request(
            "POST",
            self.url("/netacard/integrated/fullPeriod/posts.json"),
            headers=self.headers,
            params=param,
            json=data,
        )
        return r.json()

    def fetch_integrated_posts_full_period(
        self,
        visitorId: str,
        *,
        query: str,
        postLimit: int,
        fullPeriodPostsSearchType: str,
        scrollId: Optional[str] = None,
    ):
        param = {"visitorId": visitorId}
        data = {
            "query": query,
            "postLimit": postLimit,
            "fullPeriodPostsSearchType": fullPeriodPostsSearchType,
        }
        if scrollId is not None:
            data["scrollId"] = scrollId

        r = self.instance.request(
            "POST",
            self.url("/integrated/fullPeriod/posts.json"),
            headers=self.headers,
            params=param,
            json=data,
        )
        return r.json()

    def get_suggest_popular(
        self,
        *,
        query: str,
        limit: int,
    ):
        data = {"query": query, "limit": limit}
        r = self.instance.request(
            "POST",
            self.url("/suggest/popular.json"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_hash_tag_post_list(
        self, homeId: str, *, query: str, scrollId: str, postLimit: int, _range: list
    ):
        data = {"homeId": homeId, "query": query, "scrollId": scrollId, "range": _range}
        if postLimit > 0:
            data["postLimit"] = postLimit
        r = self.instance.request(
            "POST",
            self.url("/posts.json"),
            headers=self.headers,
            json=data,
        )
        return r.json()

    def get_hash_tag_search_list(self, homeId: str, *, query: str, scrollId: str):
        data = {"homeId": homeId, "query": query, "scrollId": scrollId}
        r = self.instance.request(
            "POST",
            self.url("/search.json"),
            headers=self.headers,
            json=data,
        )
        return r.json()
