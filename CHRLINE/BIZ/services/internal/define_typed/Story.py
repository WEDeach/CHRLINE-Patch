

from typing import TypedDict


class TStoryIndex(TypedDict):
    tsId: str

class TStoryIndexWithUserMid(TStoryIndex):
    userMid: str

class TStoryIndexWithGuildId(TStoryIndex):
    guideId: str