from collections import deque
from typing import TYPE_CHECKING, Any, TypedDict

from loguru import logger
from models import LiquidsoapMetadata, LiquidsoapUri, RequestQueueModeEntry
from modes.mode import RadioMode

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
        self.items: deque[RequestQueueModeEntry] = deque()

    async def setup(self) -> None:
        pass

    async def reload(self) -> None:
        pass

    async def next(self) -> LiquidsoapUri | None:
        if not self.items:
            return None

        entry = self.items.popleft()

        logger.debug(f"Fetching queued track from {entry.username}: {entry.track}")

        if dl := await self.state.pls.give(entry.track):
            return LiquidsoapUri(
                dl.path,
                LiquidsoapMetadata(user=entry.username, avatar=entry.avatar_url),
            )

        logger.warning(f"Failed to download queued track: {entry.track}")
