import asyncio
import random
from typing import TYPE_CHECKING

from loguru import logger
from models import LiquidsoapUri
from modes.mode import RadioMode
from pls import Request
from yt_dlp import YoutubeDL

if TYPE_CHECKING:
    from state import State


class YoutubeMode(RadioMode):
    def __init__(self, state: State, playlist_id: str):
        super().__init__("YouTube Playlist", state)

        self.playlist_id = playlist_id
        self.playlist: list[Request] = []
        self.order: list[Request] = []

    async def setup(self) -> None:
        logger.info(f"Getting YouTube videos from playlist {self.playlist_id}...")
        ids = await get_video_ids(self.playlist_id)

        self.playlist = [Request(url=i, isrc=None, name=None, artist=None) for i in ids]
        logger.info(f"Got {len(ids)} YouTube video(s).")

    async def next(self) -> LiquidsoapUri | None:
        if not self.playlist:
            return None

        if not self.order:
            self.order = self.playlist.copy()
            random.shuffle(self.order)

        request = self.order.pop()
        logger.debug(f"Fetching video: {request.url}")

        if dl := await self.state.pls.give(request):
            return LiquidsoapUri(dl.path, {})

        logger.warning(f"Failed to download video: {request.name}")


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
