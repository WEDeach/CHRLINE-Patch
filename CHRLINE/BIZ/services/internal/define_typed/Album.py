from typing import Literal, TypedDict

TAlbumResourceType = Literal["IMAGE", "IMAGE_ORIGINAL", "VIDEO"]
ResourceTypeMap = {
    "IMAGE": "a",
    "IMAGE_ORIGINAL": "o",
    "VIDEO": "v",
}


class TAlbumObsResourceId(TypedDict):
    svc: str
    sid: str
    oid: str


class TAlbumPhoto(TypedDict):
    obsResourceId: TAlbumObsResourceId
    resourceType: TAlbumResourceType
    height: int
    width: int
    shotTime: int
    durationMillis: int
