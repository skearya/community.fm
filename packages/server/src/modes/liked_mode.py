import asyncio
from asyncio import Task
import random
from typing import TYPE_CHECKING

from loguru import logger
from models import NO_NEXT
from modes.mode import RadioMode

if TYPE_CHECKING:
    from state import State


class LikedSongsMode(RadioMode):
    def name(self) -> str:
        return "Liked Songs"

    def __init__(self, state: State):
        self.state = state
        self.task: Task[str] | None = None

    async def setup(self) -> None:
        return

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
            if not self.state.liked:
                logger.info("No liked songs have been loaded.")
                return NO_NEXT

            user_id = random.choice(list(self.state.liked.keys()))
            entry = self.state.liked[user_id]
            song = random.choice(entry.songs)

            if dl := await self.state.pls.give(song):
                logger.info(f"Serving liked song from {entry.username}: {dl.path}")
                return f'annotate:user="{entry.username}":{dl.path}'

            logger.info(f"Failed to download liked song: {song}")
