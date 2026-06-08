import random
from typing import TYPE_CHECKING

from db import User
from loguru import logger
from models import LiquidsoapUri
from modes.mode import RadioMode
from pls import Track

if TYPE_CHECKING:
    from state import State


class LastFMMode(RadioMode):
    def __init__(self, state: State):
        super().__init__("Last.fm Weekly Top Songs", state)

        self.top: dict[int, list[Track]] = {}

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
            if tracks := await self.fetch_user(user):
                self.top[user.id] = tracks
            else:
                return None

        if not (songs := self.top[user.id]):
            return None

        song = random.choice(songs)

        logger.debug(f"Fetching Last.fm song: {song}")

        if dl := await self.state.pls.give(song):
            return LiquidsoapUri(dl.path, {"user": user.lastfm_username}, True)

        logger.warning(f"Failed to download Last.fm song: {song}")

    async def fetch_user(self, user: User) -> list[Track] | None:
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
            Track(
                id=None,
                url=None,
                isrc=None,
                title=track["name"],
                artist=track["artist"]["name"],
            )
            for track in gettoptracks["toptracks"]["track"]
        ]
