from asyncio.tasks import Task
import random
import asyncio
from pls import Request
from loguru import logger
from os import environ
from modes.mode import RadioMode
from modes.mixes.mix_pls import MixPls
from typing import TYPE_CHECKING
from models import NO_NEXT

if TYPE_CHECKING:
    from state import State

# queue: stores uris after downloading mixes
# push event when popped to start downloading next mix
# push event on init?
# call download on rip with youtube url to get mix


class MixMode(RadioMode):
    def __init__(self, state: State, playlist_id: str):
        self.state = state
        self.mixes: list[Request] = []
        self.playlist_id = playlist_id

        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self.tasks: set[asyncio.Task] = set()
        self.task: Task | None = None
        self.event = asyncio.Event()

    async def next(self) -> str:
        if self.queue.qsize() == 0:
            return NO_NEXT
        url = self.queue.get_nowait()
        logger.info(f"Serving mix: {url}")
        self.event.set()
        return url

    async def refill(self) -> None:
        while True:
            if self.queue.qsize() == 0:
                request = random.choice(self.mixes)
                logger.info(f"Fetching mix: {request.url}")
                if dl := await self.state.pls.give(request):
                    logger.info(f"Queued mix: {request.url}")
                    await self.queue.put(dl.path)
                else:
                    logger.warning(f"Failed to download mix: {request.name}")
            else:
                self.event.clear()
                await self.event.wait()

    async def setup(self) -> None:
        pls = MixPls(self.playlist_id)
        
        logger.info(f"Getting YouTube mixes from playlist {self.playlist_id}...")
        ids = await pls.get_video_ids()
        self.mixes = [Request(url=i, isrc=None, name=None, artist=None) for i in ids]
        logger.info(f"Got {len(ids)} YouTube mix(es).")

        self.task = asyncio.create_task(self.refill())

    def __str__(self) -> str:
        return "YouTube Mixes"
