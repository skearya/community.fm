import asyncio
import random
from typing import TYPE_CHECKING

from loguru import logger
from models import LiquidsoapUri
from modes.mode import RadioMode
from pls import Track
from yt_dlp import YoutubeDL

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
        ids = await get_video_ids(self.playlist_id)
        logger.info(f"Got {len(ids)} YouTube video(s).")

        self.playlist = [
            Track(id=None, url=id, isrc=None, title=None, artist=None) for id in ids
        ]

    async def next(self) -> LiquidsoapUri | None:
        if not self.playlist:
            return None

        if not self.order:
            self.order = self.playlist.copy()
            random.shuffle(self.order)

        track = self.order.pop()
        logger.debug(f"Fetching video: {track.url}")

        if dl := await self.state.pls.give(track):
            return LiquidsoapUri(dl.path, {}, True)

        logger.warning(f"Failed to download video: {track.url}")


async def get_video_ids(playlist_id: str) -> list[str]:
    def run() -> list[str]:
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_id, download=False)

                if "entries" in info:
                    return [e["id"] for e in info["entries"]]

                raise ValueError("Key 'entries' not found")
        except Exception:
            logger.exception("Failed to get playlist")
            return []

    return await asyncio.to_thread(run)


ydl_opts = {
    "quiet": True,
    "ignoreerrors": True,
    "extract_flat": "in_playlist",
}
