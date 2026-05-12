import asyncio
from asyncio import Task
import random
from typing import TYPE_CHECKING

from loguru import logger
from models import LiquidsoapUri
from modes.mode import RadioMode

if TYPE_CHECKING:
    from state import State


class LikedSongsMode(RadioMode):
    def __init__(self, state: State):
        super().__init__("Liked Songs", state)

        self.task: Task[LiquidsoapUri | None] | None = None

    async def setup(self) -> None:
        return

    async def next(self) -> LiquidsoapUri | None:
        match self.task:
            case Task() if self.task.done():
                dl, self.task = self.task.result(), None
                return dl
            case Task():
                return None
            case None:
                self.task = asyncio.create_task(self.fetch())
                return None

    async def fetch(self) -> LiquidsoapUri | None:
        if not self.state.liked:
            logger.info("No liked songs have been loaded.")
            return None

        for entry in self.state.liked.values():
            if entry.username == "nyakkin":
                song = random.choice(entry.songs)

                if dl := await self.state.pls.give(song):
                    logger.info(f"Serving liked song from {entry.username}: {dl.path}")

                    return LiquidsoapUri(
                        dl.path, {"user": entry.username, "mode": self.name}
                    )

                logger.info(f"Failed to download liked song: {song}")

        return None
