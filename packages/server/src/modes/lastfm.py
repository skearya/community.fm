import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

from db import User
from loguru import logger
from models import LiquidsoapUri
from modes.mode import RadioMode
from pls import Track

if TYPE_CHECKING:
    from state import State


@dataclass
class LastFMItem:
    playcount: int
    track: Track


DECAY_BASE = 0.99


class LastFMMode(RadioMode):
    def __init__(self, state: State):
        super().__init__("Last.fm Weekly Top Songs", state)

        self.top: dict[int, list[LastFMItem]] = {}

    async def setup(self) -> None:
        pass

    async def next(self) -> LiquidsoapUri | None:
        db = self.state.db

        users = await db.get_users()

        if not users:
            logger.info("No last.fm users exist in the database.")
            return None

        user = random.choice(users)

        if user.id not in self.top:
            if items := await self.fetch_user(user):
                self.top[user.id] = items
            else:
                return None

        if not (songs := self.top[user.id]):
            return None

        weights = [DECAY_BASE**i for i in range(len(songs))]
        item = random.choices(songs, weights=weights, k=1)[0]

        logger.debug(f"Fetching Last.fm item: {item.track}")

        if dl := await self.state.pls.give(item.track):
            return LiquidsoapUri(
                dl.path,
                {"user": user.lastfm_username, "playcount": str(item.playcount)},
                True,
            )

        logger.warning(f"Failed to download Last.fm item: {item}")

    async def fetch_user(self, user: User) -> list[LastFMItem] | None:
        lastfm = self.state.lastfm

        gettoptracks = await lastfm.api(
            {
                "method": "user.gettoptracks",
                "user": user.lastfm_username,
                "period": "7day",
                "sk": user.lastfm_session,
            }
        )

        if not gettoptracks:
            return None

        return [
            LastFMItem(
                playcount=track["playcount"],
                track=Track(
                    id=None,
                    url=None,
                    isrc=None,
                    title=track["name"],
                    artist=track["artist"]["name"],
                ),
            )
            for track in gettoptracks["toptracks"]["track"]
        ]
