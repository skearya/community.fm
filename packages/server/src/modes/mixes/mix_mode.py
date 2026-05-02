from loguru import logger
from os import environ
from modes.mode import RadioMode
from modes.mixes.mix_pls import MixPls
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state import State

# queue: stores uris after downloading mixes
# push event when popped to start downloading next mix
# push event on init?
# call download on rip with youtube url to get mix


class MixMode(RadioMode):
    def __init__(self, state: State):
        self.state = state

    async def next(self) -> str:
        return "/etc/liquidsoap/assets/oops.mp3"

    async def setup(self) -> None:
        playlist_id = environ["YOUTUBE_PLAYLIST_ID"]
        pls = MixPls(playlist_id)

        logger.info(f"Getting YouTube mixes from playlist {playlist_id}...")
        ids = await pls.get_video_ids()
        self.state.mixes = ids
        logger.info(f"Got {len(ids)} YouTube mix(es).")

    def __str__(self) -> str:
        return "YouTube Mixes"
