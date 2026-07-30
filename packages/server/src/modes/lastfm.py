import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, TypedDict

from db import User
from loguru import logger
from models import LiquidsoapMetadata, LiquidsoapUri
from modes.mode import RadioMode
from pls import Track
from utils import ConfigError

if TYPE_CHECKING:
    from state import State

DECAY_BASE = 0.99


@dataclass()
class LastFMItem:
    track: Track
    playcount: int


class LastFMOptions(TypedDict):
    period: Literal["overall", "7day", "1month", "3month", "6month", "12month"]


class LastFMMode(RadioMode):
    def options() -> type[Any]:
        return LastFMOptions

    def __init__(self, state: State, name: str, options: LastFMOptions):
        super().__init__(state, "Last.fm Top Songs", name)

        if not (lastfm := self.state.lastfm):
            raise ConfigError(
                "Cannot use Last.fm radio mode without `LASTFM_API_KEY` and `LASTFM_SECRET` environment variables."
            )

        self.lastfm = lastfm
        self.period = options["period"]
        self.top: dict[User, list[LastFMItem]] = {}
        self.avatars: dict[User, str | None] = {}

    async def setup(self) -> None:
        if not (users := await self.state.db.get_users()):
            logger.info("No Last.fm users exist in the database.")
            return

        logger.info(
            f"Getting Last.fm {self.period} top tracks for {len(users)} user(s)."
        )

        self.top = {user: await self.gettoptracks(user) for user in users}
        self.avatars = {user: await self.getinfo(user) for user in users}

        logger.info(f"Got Last.fm '{self.period}' top tracks.")

    async def reload(self) -> None:
        await self.setup()

    async def next(self) -> LiquidsoapUri | None:
        if not self.top:
            logger.info("No Last.fm top tracks have been fetched.")
            return None

        user = random.choice(list(self.top.keys()))

        if not (items := self.top[user]):
            logger.info("User has no songs in playlist?")
            return None

        weights = [DECAY_BASE**i for i in range(len(items))]
        item = random.choices(items, weights=weights)[0]

        logger.debug(f"Fetching Last.fm item: {item.track}")

        if dl := await self.state.pls.give(item.track):
            return LiquidsoapUri(
                dl.path,
                LiquidsoapMetadata(
                    user=user.lastfm_username,
                    playcount=str(item.playcount),
                    avatar=self.avatars[user],
                ),
            )

        logger.warning(f"Failed to download Last.fm item: {item.track}")

    async def gettoptracks(self, user: User) -> list[LastFMItem]:
        items: list[LastFMItem] = []
        page = 1

        while True:
            gettoptracks = await self.lastfm.api(
                {
                    "method": "user.gettoptracks",
                    "user": user.lastfm_username,
                    "period": self.period,
                    "limit": "1000",
                    "page": str(page),
                    "sk": user.lastfm_session,
                }
            )

            if not gettoptracks:
                logger.error(f"Failed getting last.fm top tracks for {user.id}")
                return items

            items.extend(
                [
                    LastFMItem(
                        track=Track(
                            id=None,
                            url=None,
                            isrc=None,
                            title=track["name"],
                            artist=track["artist"]["name"],
                        ),
                        playcount=int(track["playcount"]),
                    )
                    for track in gettoptracks["toptracks"]["track"]
                ]
            )

            if page >= int(gettoptracks["toptracks"]["@attr"]["totalPages"]):
                return items

            page += 1

    async def getinfo(self, user: User) -> str | None:
        getinfo = await self.lastfm.api(
            {
                "method": "user.getinfo",
                "user": user.lastfm_username,
                "sk": user.lastfm_session,
            }
        )

        if not getinfo:
            logger.error(f"Failed getting last.fm user info for {user.id}")
            return None

        return getinfo["user"]["image"][-1]["#text"] or None
