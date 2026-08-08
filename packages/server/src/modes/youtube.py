import random
from typing import TYPE_CHECKING, Any, TypedDict

from loguru import logger
from models import LiquidsoapMetadata, LiquidsoapUri
from modes.mode import RadioMode
from pls import Album, Playlist, Track

if TYPE_CHECKING:
    from state import State


class YoutubeOptions(TypedDict):
    playlist_id: str


class YoutubeMode(RadioMode):
    def options() -> type[Any]:
        return YoutubeOptions

    def __init__(self, state: State, name: str, options: YoutubeOptions):
        super().__init__(state, "YouTube Playlist", name)

        self.playlist_id = options["playlist_id"]
        self.playlist: list[Track] = []
        self.order: list[Track] = []

    async def setup(self) -> None:
        logger.info(f"Getting YouTube videos from playlist {self.playlist_id}...")

        media = await self.state.pls.info("youtube", self.playlist_id, "playlist")

        if isinstance(media, Track):
            self.playlist = [media]
        elif isinstance(media, Album | Playlist):
            self.playlist = media.items

        logger.info(f"Got {len(self.playlist)} YouTube video(s).")

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
            return LiquidsoapUri(dl.path, LiquidsoapMetadata())

        logger.warning(f"Failed to download video: {track.url}")
