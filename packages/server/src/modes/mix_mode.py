import asyncio
import random
from asyncio.tasks import Task
from typing import TYPE_CHECKING

from loguru import logger
from models import NO_NEXT
from modes.mode import RadioMode
from pls import Request
from yt_dlp import YoutubeDL

if TYPE_CHECKING:
    from state import State


class MixMode(RadioMode):
    def __init__(self, state: State, playlist_id: str):
        self.state = state
        self.playlist: list[Request] = []
        self.playlist_id = playlist_id
        self.order: list[Request] = []
        self.task: Task[str] | None = None

    async def setup(self) -> None:
        logger.info(f"Getting YouTube mixes from playlist {self.playlist_id}...")
        ids = await get_video_ids(self.playlist_id)

        self.playlist = [Request(url=i, isrc=None, name=None, artist=None) for i in ids]
        logger.info(f"Got {len(ids)} YouTube mix(es).")

        self.task = asyncio.create_task(self.fetch())

    async def next(self) -> str:
        match self.task:
            case Task() if self.task.done():
                dl, self.task = self.task.result(), None
                return dl
            case Task():
                return NO_NEXT
            case None:
                self.task = asyncio.create_task(self.fetch())
                return NO_NEXT

    async def fetch(self) -> str:
        while True:
            if not self.playlist:
                return NO_NEXT

            if not self.order:
                self.order = self.playlist.copy()
                random.shuffle(self.order)

            request = self.order.pop()
            logger.info(f"Fetching mix: {request.url}")

            if dl := await self.state.pls.give(request):
                logger.info(f"Queued mix: {request.url}")
                return dl.path
            else:
                logger.warning(f"Failed to download mix: {request.name}")

    def __str__(self) -> str:
        return "YouTube Mixes"


ydl_opts = {
    "quiet": True,
    "ignoreerrors": True,
    "extract_flat": "in_playlist",
}


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
