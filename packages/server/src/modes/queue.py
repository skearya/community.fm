from collections import deque
from typing import TYPE_CHECKING

from loguru import logger
from models import LiquidsoapUri
from modes.mode import RadioMode
from pls import Track

if TYPE_CHECKING:
    from state import State


class RequestQueueMode(RadioMode):
    def __init__(self, state: State):
        super().__init__("Request Queue", state)

        self.items: deque[tuple[str, Track]] = deque()

    async def setup(self) -> None:
        pass

    async def next(self) -> LiquidsoapUri | None:
        if not self.items:
            return None

        username, track = self.items.popleft()

        logger.debug(f"Fetching queued track from {username}: {track}")

        if dl := await self.state.pls.give(track):
            return LiquidsoapUri(dl.path, {"user": username}, True)

        logger.warning(f"Failed to download queued track: {track}")
