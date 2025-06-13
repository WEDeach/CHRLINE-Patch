from typing import Dict, List, Literal, Optional, TypedDict, Union

TMediaType = Literal["PHOTO", "VIDEO", "SNAP", "COVER", "ANIGIF", "UNKNOWN"]
TPostReportReasonCode = Literal["R0014", "R0003", "R0011", "R0019", "R0020"]


class TPostInfoReadPermission(TypedDict):
    type: Literal["ALL", "FRIEND", "GROUP", "EVENT", "NONE"]
    gids: List[int]


class TPostInfo(TypedDict):
    postId: Optional[str]
    readPermission: TPostInfoReadPermission
    editableContents: Optional[List[Literal["ALL", "TEXT", "NONE"]]]


class TPostTextStyle(TypedDict):
    textSizeMode: Literal["NORMAL", "AUTO"]
    backgroundColor: str
    textAnimation: Literal["NONE", "SLIDE", "ZOOM", "BUZZ", "BOUNCE", "BLINK"]


class TPostStickerStyle(TypedDict):
    backgroundColor: str


class TPostMediaStyle(TypedDict):
    displayType: Literal[
        "GRID_1_A",
        "GRID_2_A",
        "GRID_2_B",
        "GRID_2_C",
        "GRID_3_A",
        "GRID_3_B",
        "GRID_3_C",
        "GRID_3_D",
        "GRID_3_E",
        "GRID_4_A",
        "GRID_4_B",
        "GRID_4_C",
        "GRID_5_A",
        "GRID_5_B",
        "GRID_5_C",
        "GRID_6_A",
        "SLIDE",
        "UNKNOWN",
    ]


class TPostStyleContent(TypedDict):
    textStyle: Optional[TPostTextStyle]
    stickerStyle: Optional[TPostStickerStyle]
    mediaStyle: Optional[TPostMediaStyle]


class TPostTextMetaContent(TypedDict):
    start: int
    end: int
    mid: Optional[str]
    displayText: Optional[str]
    type: Optional[Literal["RECALL", "HASHTAG", "LINK", "HYPERTEXT", "NONE"]]
    user: Optional[Dict[Literal["actorId"], str]]
    link: Optional[str]


class TPostStickerContent(TypedDict):
    id: int
    packageId: int
    packageVersion: int
    hasAnimation: bool
    hasSound: bool
    stickerResourceType: Literal[
        "STATIC",
        "ANIMATION",
        "SOUND",
        "ANIMATION_SOUND",
        "POPUP",
        "POPUP_SOUND",
        "NAME_TEXT",
        "PER_STICKER_TEXT",
    ]
    stickerImageText: Optional[str]
    stickerMessage: Optional[str]


class TPostLocationPoiInfo(TypedDict):
    placeName: str
    provider: str
    category: str


class TPostLocationContent(TypedDict):
    latitude: float
    longitude: float
    name: str
    poiInfo: Optional[TPostLocationPoiInfo]


class TPostMediaCoordinates(TypedDict):
    x1: int
    y1: int
    x2: int
    y2: int


class TPostMediaContent(TypedDict):
    objectId: str
    serviceName: str
    obsNamespace: str
    type: TMediaType
    width: int
    height: int
    size: Optional[int]
    obsFace: Optional[str]
    faceCoordinates: Optional[List[TPostMediaCoordinates]]


class TPostSticonMetaContent(TypedDict):
    start: int
    end: int
    productId: str
    ticonId: str
    version: int
    resourceType: str


class TPostContents(TypedDict):
    text: Optional[str]
    contentsStyle: Optional[TPostStyleContent]
    textMeta: Optional[List[TPostTextMetaContent]]
    stickers: Optional[List[TPostStickerContent]]
    locations: Optional[List[TPostLocationContent]]
    media: List[TPostMediaContent]
    sticonMetas: List[TPostSticonMetaContent]


class TPostMusicContent(TypedDict):
    id: str
    type: str
    regions: List[str]


class TPostAdditionalAppUrlContent(TypedDict):
    type: Literal["APP"]
    androidTargetUrl: Optional[str]
    iPhoneTargetUrl: Optional[str]


class TPostAdditionalWebUrlContent(TypedDict):
    type: Literal["WEB"]
    targetUrl: Optional[str]


class TPostObsThumbnailContent(TypedDict):
    objectId: str
    serviceName: str
    obsNamespace: str
    type: TMediaType
    width: int
    height: int


class TPostAdditionalContents(TypedDict):
    music: TPostMusicContent
    url: Union[TPostAdditionalAppUrlContent, TPostAdditionalWebUrlContent]
    title: Optional[str]
    main: Optional[str]
    sub: Optional[str]
    thumbnail: Optional[Dict[Literal["url"], str]]
    obsthumbnail: Optional[TPostObsThumbnailContent]


class TPostLightsMediaContent(TypedDict):
    type: str
    obsNamespace: str
    objectId: str
    serviceName: str
    hash: str
    width: int
    height: int


class TPostLightsTrackContent(TypedDict):
    type: Literal["MUSIC", "ORIGINAL"]
    trackId: int


class TPostLightsContents(TypedDict):
    media: Dict[Literal["original"], TPostLightsMediaContent]
    effects: List[Dict[Literal["id"], int]]
    tracks: List[TPostLightsTrackContent]


class TPost(TypedDict):
    postInfo: TPostInfo
    contents: TPostContents
    originInfo: Optional[Dict[Literal["originAppSn"], str]]
    additionalContents: Optional[TPostAdditionalContents]
