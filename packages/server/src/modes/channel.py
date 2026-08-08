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

    async def setup(self) -> None:
        pass

    async def reload(self) -> None:
        pass

    async def next(self) -> LiquidsoapUri | None:
        if not self.entries:
            logger.info("No channel songs have been loaded yet.")
            return None

        choices = [entry for entry in self.entries.values() if entry.tracks]

        if not choices:
            logger.info("All users have no songs in their playlist?")
            return None

        entry = random.choice(choices)
        song = random.choice(entry.tracks)

        logger.debug(f"Fetching channel song: {song}")

        if dl := await self.state.pls.give(song):
            return LiquidsoapUri(
                dl.path,
                LiquidsoapMetadata(user=entry.username, avatar=entry.avatar_url),
            )

        logger.warning(f"Failed to download channel song: {song}")
