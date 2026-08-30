import random
from typing import TYPE_CHECKING, Any, TypedDict

from loguru import logger
from models import ChannelModeEntry, LiquidsoapMetadata, LiquidsoapUri
from modes.mode import RadioMode
from utils import ConfigError

if TYPE_CHECKING:
    from state import State


class ChannelOptions(TypedDict):
    channel_name: str


class ChannelMode(RadioMode):
    def options() -> type[Any]:
        return ChannelOptions

    def __init__(self, state: State, name: str, options: ChannelOptions):
        super().__init__(state, "Channel Songs", name)

        if not state.config.DISCORD_BOT_TOKEN:
            raise ConfigError(
                "Cannot use Discord Channel radio mode without the `DISCORD_BOT_TOKEN` environment variable."
            )

        self.channel_name = options["channel_name"]
        self.entries: dict[int, ChannelModeEntry] = {}
        self.order: list[int] = []

    async def setup(self) -> None:
        pass

    async def reload(self) -> None:
        pass

    async def next(self) -> LiquidsoapUri | None:
        if not self.entries:
            logger.info("No channel songs have been loaded yet.")
            return None

        if not self.order:
            self.order = [id for id, entry in self.entries.items() if entry.tracks]

            if not self.order:
                logger.info("All users have no songs in their playlist?")
                return None

            random.shuffle(self.order)

        entry = self.entries[self.order.pop()]
        track = random.choice(entry.tracks)

        logger.debug(f"Fetching channel song: {track}")

        if dl := await self.state.pls.give(track):
            return LiquidsoapUri(
                dl.path,
                LiquidsoapMetadata(user=entry.username, avatar=entry.avatar_url),
            )

        logger.warning(f"Failed to download channel song: {track}")
