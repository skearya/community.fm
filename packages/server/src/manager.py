import asyncio
import random
from typing import TYPE_CHECKING

from loguru import logger
from modes.liked import LikedSongsMode
from modes.local import LocalSongsMode
from modes.mode import RadioMode
from modes.youtube import YoutubeMode

if TYPE_CHECKING:
    from state import State

RETRIES_BEFORE_MODE_SWITCH = 3


class Request:
    def __init__(self, mode: RadioMode):
        self.mode = mode
        self.task = asyncio.create_task(mode.next())
        self.retries = 0

    def retry(self):
        logger.debug(
            f"Retrying request for mode {self.mode.name} ({self.retries + 1}/{RETRIES_BEFORE_MODE_SWITCH})"
        )

        self.task = asyncio.create_task(self.mode.next())
        self.retries += 1


class ModeManager:
    def __init__(self, state: State):
        self.state = state

        self.modes: list[RadioMode] = [
            LocalSongsMode(state),
            LikedSongsMode(state),
        ]

        if state.config.YOUTUBE_PLAYLIST_ID:
            self.modes.append(YoutubeMode(state, state.config.YOUTUBE_PLAYLIST_ID))
        else:
            logger.warning(
                "YOUTUBE_PLAYLIST_ID environment variable unset, disabling YouTube mix mode"
            )

        self.mode = random.choice(self.modes)
        self.request: Request | None = None

    async def setup(self) -> None:
        for mode in self.modes:
            await mode.setup()

    async def switch(self, name: str) -> bool:
        match = next((mode for mode in self.modes if mode.name == name), None)

        if match is None:
            return False

        logger.info(f"Mode manually switched from '{self.mode.name}' to '{match.name}'")
        self.mode = match

        if self.request is not None:
            self.request.task.cancel()

            try:
                await self.request.task
            except asyncio.CancelledError:
                pass

            self.request = Request(self.mode)

        return True

    def next(self) -> str:
        match self.request:
            case Request() if self.request.task.done():
                dl = self.request.task.result()

                if dl is not None:
                    logger.info(f"Serving {dl.file} from '{self.request.mode.name}'")

                    dl.metadata["mode"] = self.request.mode.name
                    self.request = None

                    return str(dl)

                if self.request.retries + 1 >= RETRIES_BEFORE_MODE_SWITCH:
                    mode = random.choice(
                        [m for m in self.modes if m is not self.request.mode]
                    )

                    logger.warning(
                        f"Mode '{self.request.mode.name}' consistently failed, trying {mode.name}"
                    )

                    self.mode = mode
                    self.request = Request(self.mode)
                else:
                    self.request.retry()

                return "LOADING"
            case Request():
                return "LOADING"
            case None:
                self.request = Request(self.mode)

                return "LOADING"
