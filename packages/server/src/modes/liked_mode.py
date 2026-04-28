import random
from typing import TYPE_CHECKING

from loguru import logger
from models import NO_NEXT
from modes.mode import RadioMode

if TYPE_CHECKING:
    from state import State


class LikedSongsMode(RadioMode):
    def __init__(self, state: State):
        self.state = state

    async def next(self) -> str:
        if not self.state.liked:
            logger.info("No liked songs have been loaded.")
            return NO_NEXT

        user_id = random.choice(list(self.state.liked.keys()))
        song = random.choice(self.state.liked[user_id])

        if dl := await self.state.pls.give(song):
            logger.info(f"Serving liked song: {dl.path}")
            return f'annotate:user="{user_id}":{dl.path}'
        else:
            logger.info(f"Failed to download liked song: {song}")
            return NO_NEXT
