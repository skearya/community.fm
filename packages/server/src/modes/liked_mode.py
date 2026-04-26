from pls import StreamripPls, YoutubePls
from pls.utils import Request
import random
from modes.radio_mode import RadioMode
from typing import TYPE_CHECKING
from loguru import logger
from models import NO_NEXT

if TYPE_CHECKING:
    from state import State


class LikedSongsMode(RadioMode):
    def __init__(self, state: State):
        self.state = state

    async def next(self) -> str:
        if not self.state.liked_songs:
            logger.info("No liked songs have been loaded.")
            return NO_NEXT

        async with StreamripPls() as streamrip, YoutubePls() as youtube:
            song = random.choice(self.state.liked_songs)
            request = Request("?", song.isrc, song.name, song.artists)
            song_logger = logger.bind(item=str(request))

            dl = await streamrip.isrc(request, song_logger) or await youtube.rip(
                request, song_logger
            )
            if dl is not None:
                logger.info(f"Serving liked song: {dl.path}")
                return dl.path
            else:
                logger.info(f"Failed to download liked song: {song.name}")
                return NO_NEXT
