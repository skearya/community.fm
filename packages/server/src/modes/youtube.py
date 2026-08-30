import random
from typing import TYPE_CHECKING, Any, TypedDict

from loguru import logger
from models import LiquidsoapMetadata, LiquidsoapUri
from modes.mode import RadioMode
from pls import Track

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
        self.order: list[int] = []

    async def setup(self) -> None:
        logger.info(f"Getting YouTube video(s) from '{self.playlist_id}'...")

        if not (
            media := await self.state.pls.info("youtube", self.playlist_id, "playlist")
        ):
            logger.error(f"Failed getting YouTube video(s) from '{self.playlist_id}'!")
            return

        self.playlist = [media] if isinstance(media, Track) else media.items
        self.order = []

        logger.info(f"Got {len(self.playlist)} YouTube video(s).")

    async def reload(self) -> None:
        await self.setup()

    async def next(self) -> LiquidsoapUri | None:
        if not self.playlist:
            logger.info("No playlist items have been loaded yet or playlist is empty.")
            return None

        if not self.order:
            self.order = list(range(len(self.playlist)))
            random.shuffle(self.order)

        track = self.playlist[self.order.pop()]

        logger.debug(f"Fetching video: {track.url}")

        if dl := await self.state.pls.give(track):
            return LiquidsoapUri(dl.path, LiquidsoapMetadata())

        logger.warning(f"Failed to download video: {track.url}")
