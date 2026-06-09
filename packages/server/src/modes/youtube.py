import random
from typing import TYPE_CHECKING

from loguru import logger
from models import LiquidsoapUri
from modes.mode import RadioMode
from pls import Playlist, Track

if TYPE_CHECKING:
    from state import State


class YoutubeMode(RadioMode):
    def __init__(self, state: State, playlist_id: str):
        super().__init__("YouTube Playlist", state)

        self.playlist_id = playlist_id
        self.playlist: list[Track] = []
        self.order: list[Track] = []

    async def setup(self) -> None:
        logger.info(f"Getting YouTube videos from playlist {self.playlist_id}...")

        media = await self.state.pls.info("youtube", self.playlist_id, "playlist")

        if not isinstance(media, Playlist):
            logger.error(f"YouTube 'playlist' {self.playlist_id} is not a playlist")
            return

        logger.info(f"Got {len(media.items)} YouTube video(s).")

        self.playlist = media.items

    async def reload(self) -> None:
        await self.setup()

    async def next(self) -> LiquidsoapUri | None:
        if not self.playlist:
            logger.info("No playlist items have been loaded yet or playlist is empty.")
            return None

        if not self.order:
            self.order = self.playlist.copy()
            random.shuffle(self.order)

        track = self.order.pop()
        logger.debug(f"Fetching video: {track.url}")

        if dl := await self.state.pls.give(track):
            return LiquidsoapUri(dl.path, {}, True)

        logger.warning(f"Failed to download video: {track.url}")
