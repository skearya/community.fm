import asyncio
import random
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger
from models import LiquidsoapUri
from modes.lastfm import LastFMMode
from modes.liked import LikedSongsMode
from modes.local import LocalSongsMode
from modes.mode import RadioMode
from modes.queue import RequestQueueMode
from modes.youtube import YoutubeMode

if TYPE_CHECKING:
    from state import State

RETRIES_BEFORE_MODE_SWITCH = 3
DOWNLOADS_BEFORE_DELETION = 3


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
        self.queue = RequestQueueMode(state)
        self.modes: list[RadioMode] = [
            LocalSongsMode(state),
            LikedSongsMode(state),
            LastFMMode(state),
            self.queue,
        ]

        if state.config.YOUTUBE_PLAYLIST_ID:
            self.modes.append(YoutubeMode(state, state.config.YOUTUBE_PLAYLIST_ID))
        else:
            logger.warning(
                "YOUTUBE_PLAYLIST_ID environment variable unset, disabling YouTube mix mode"
            )

        self.mode = random.choice([m for m in self.modes if m is not self.queue])
        self.request: Request | None = None
        self.history: deque[LiquidsoapUri] = deque()

    async def setup(self) -> None:
        for mode in self.modes:
            await mode.setup()

    async def switch(self, name: str) -> bool:
        match = next((m for m in self.modes if m.name == name), None)

        if match is None:
            return False

        old, self.mode = self.mode, match
        logger.info(f"Mode switched from '{old.name}' to '{match.name}'")

        if self.request is not None:
            self.request.task.cancel()

            try:
                await self.request.task
            except asyncio.CancelledError:
                pass

            self.request = Request(self.mode)

        async with self.state.session.post(
            f"{self.state.config.LIQUIDSOAP_BASE_URL}/clear"
        ) as response:
            response.raise_for_status()

        return True

    def next(self) -> str:
        match self.request:
            case Request() if self.request.task.done():
                if (
                    not self.request.task.cancelled()
                    and self.request.task.exception() is None
                    and (dl := self.request.task.result())
                ):
                    logger.info(f"Serving {dl.file} from '{self.request.mode.name}'")

                    dl.metadata["mode"] = self.request.mode.name
                    self.request = None

                    self.history.append(dl)

                    if len(self.history) > DOWNLOADS_BEFORE_DELETION:
                        old = self.history.popleft()

                        if old.deletable:
                            Path(old.file).unlink(missing_ok=True)

                    return str(dl)

                if self.request.retries + 1 >= RETRIES_BEFORE_MODE_SWITCH:
                    mode = random.choice(
                        [m for m in self.modes if m is not self.request.mode]
                    )

                    logger.warning(
                        f"Mode '{self.request.mode.name}' consistently failed, trying '{mode.name}'"
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
