import random
from typing import TYPE_CHECKING

from loguru import logger
from models import NO_NEXT
from modes.mode import RadioMode
from pls import Request

if TYPE_CHECKING:
    from state import State


class LikedSongsMode(RadioMode):
    def __init__(self, state: State):
        self.state = state

    async def next(self) -> str:
        if not self.state.liked:
            logger.info("No liked songs have been loaded.")
            return NO_NEXT

        song = random.choice(self.state.liked)
        request = Request(None, song.isrc, song.name, song.artists)

        if dl := await self.state.pls.give(request):
            logger.info(f"Serving liked song: {dl.path}")
            return dl.path
        else:
            logger.info(f"Failed to download liked song: {request}")
            return NO_NEXT
