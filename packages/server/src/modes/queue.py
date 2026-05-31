from collections import deque
from typing import TYPE_CHECKING

import pls
from loguru import logger
from models import LiquidsoapUri
from modes.mode import RadioMode

if TYPE_CHECKING:
    from state import State


class RequestQueueMode(RadioMode):
    def __init__(self, state: State):
        super().__init__("Request Queue", state)

        self.items: deque[pls.Request] = deque()

    async def setup(self) -> None:
        pass

    async def next(self) -> LiquidsoapUri | None:
        if not self.items:
            return None

        request = self.last = self.items.popleft()

        logger.debug(f"Fetching queued request: {request}")

        if dl := await self.state.pls.give(request):
            return LiquidsoapUri(dl.path, {}, True)

        logger.warning(f"Failed to download request: {request}")
