from collections import deque
from typing import TYPE_CHECKING, Any, TypedDict

from loguru import logger
from models import LiquidsoapUri
from modes.mode import RadioMode
from pls import Track

if TYPE_CHECKING:
    from state import State


class RequestQueueOptions(TypedDict):
    autoswitch: bool


class RequestQueueMode(RadioMode):
    def options() -> type[Any]:
        return RequestQueueOptions

    def __init__(self, state: State, name: str, options: RequestQueueOptions):
        super().__init__(state, "Request Queue", name)

        self.autoswitch = options["autoswitch"]
        self.items: deque[tuple[str, Track]] = deque()

    async def setup(self) -> None:
        pass

    async def reload(self) -> None:
        pass

    async def next(self) -> LiquidsoapUri | None:
        if not self.items:
            return None

        username, track = self.items.popleft()

        logger.debug(f"Fetching queued track from {username}: {track}")

        if dl := await self.state.pls.give(track):
            return LiquidsoapUri(dl.path, {"user": username}, True)

        logger.warning(f"Failed to download queued track: {track}")
