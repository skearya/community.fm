import random
from typing import TYPE_CHECKING

from loguru import logger
from models import LiquidsoapUri
from modes.mode import RadioMode

if TYPE_CHECKING:
    from state import State


class LikedSongsMode(RadioMode):
    def __init__(self, state: State):
        super().__init__("Liked Songs", state)

    async def setup(self) -> None:
        pass

    async def next(self) -> LiquidsoapUri | None:
        if not self.state.liked:
            logger.info("No liked songs have been loaded.")
            return None

        user_id = random.choice(list(self.state.liked.keys()))
        entry = self.state.liked[user_id]
        song = random.choice(entry.songs)

        logger.debug(f"Fetching liked song: {song}")

        if dl := await self.state.pls.give(song):
            return LiquidsoapUri(dl.path, {"user": entry.username}, True)

        logger.warning(f"Failed to download liked song: {song}")
