from typing import TYPE_CHECKING, Union

from .base import BaseBIZ
from .internal import InternalBiz
from .services.AB import Album
from .services.DS import Translation
from .services.EG import SocialNotification
from .services.HM import MyHomeRenewal
from .services.MA import HomeApi
from .services.MH import MyHome
from .services.NT import Note
from .services.SN import SquareNote
from .services.ST import Story
from .services.TL import Timeline
from .services.TLGW import TimelineGateway
from .timeline import TimelineBiz

if TYPE_CHECKING:
    from ..client import CHRLINE


class BizManager(BaseBIZ):

    def __init__(self, client: "CHRLINE"):
        super().__init__(client)

        self.common = InternalBiz(self.client)
        self.timeline_biz = TimelineBiz(self.client)

        self.myhome = MyHome(self.client, 57)
        self.myhome_renewal = MyHomeRenewal(self.client, 1)
        self.timeline = Timeline(self.client, 57)
        self.timeline_gw = TimelineGateway(self.client, 1)
        self.note = Note(self.client, 57)
        self.home_api = HomeApi(self.client, 1)
        self.note_square = SquareNote(self.client, 57)
        self.album = Album(self.client, 5)
        self.story = Story(self.client, 12)
        self.social_notification = SocialNotification(self.client, 5)
        self.translation = Translation(self.client, -1)

        self.__t_timeline: Union[str, None] = None
        self.__t_album: Union[str, None] = None
        self.__t_cms: Union[str, None] = None

    @property
    def token_with_timeline(self):
        """Get token for TIMELINE or MYHOME."""
        if self.__t_timeline is None:
            TIMELINE_CHANNEL_ID = "1341209950"
            if self.client.APP_TYPE in ["CHROMEOS"]:
                TIMELINE_CHANNEL_ID = "1341209850"
            self.__t_timeline = self.issue_access_token_for_channel(TIMELINE_CHANNEL_ID)
            if not isinstance(self.__t_timeline, str):
                raise ValueError(
                    f"can't use Timeline, the token return `{self.__t_timeline}`"
                )
        return self.__t_timeline

    @property
    def token_with_album(self):
        """Get token for Album."""
        if self.__t_album is None:
            self.__t_album = self.issue_access_token_for_channel("1375220249")
            if not isinstance(self.__t_album, str):
                raise ValueError(
                    f"can't use Album, the token return `{self.__t_album}`"
                )
        return self.__t_album

    @property
    def token_with_cms(self):
        if self.__t_cms is None:
            TIMELINE_BIZ_LIFF_ID = "1654109201-MgN2z4Nd"
            self.__t_cms = self.client.checkAndGetValue(
                self.client.issueLiffView(None, TIMELINE_BIZ_LIFF_ID), 7, "val_7"
            )
            if not isinstance(self.__t_cms, str):
                raise ValueError(
                    f"can't use TimelineBiz, the token return `{self.__t_cms}`"
                )
        return self.__t_cms

    @property
    def headers_with_timeline(self):
        """Get headers for TIMELINE or MYHOME."""
        return {
            "x-line-application": self.client.server.Headers["x-line-application"],
            "User-Agent": self.client.server.Headers["User-Agent"],
            "X-Line-Mid": self.client.mid,
            "X-Line-Access": self.client.authToken,
            "X-Line-ChannelToken": self.token_with_timeline,
            "x-lal": self.client.LINE_LANGUAGE,
            "X-LAP": "5",
            "X-LPV": "1",
            "X-LSR": self.client.LINE_SERVICE_REGION,
            "Content-Type": "application/json; charset=UTF-8",
            # "X-Line-PostShare": "true"
            # "X-Line-StoryShare": "true"
        }

    def issue_access_token_for_channel(self, channelId: str):
        return self.client.checkAndGetValue(
            self.client.approveChannelAndIssueChannelToken(channelId),
            "channelAccessToken",
            5,
        )

    def renew_tokens(self):
        self.__t_timeline = None
        self.__t_cms = None
