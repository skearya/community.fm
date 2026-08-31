import random
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

from loguru import logger
from models import LiquidsoapMetadata, LiquidsoapUri
from modes.mode import RadioMode

if TYPE_CHECKING:
    from state import State

AUDIO_EXT = {".3gp", ".aa", ".aac", ".aax", ".act", ".aiff", ".alac", ".amr", ".ape", ".au", ".awb", ".dss", ".dvf", ".flac", ".gsm", ".iklax", ".ivs", ".m4a", ".m4b", ".m4p", ".mmf", ".movpkg", ".mp1", ".mp2", ".mp3", ".mpc", ".msv", ".nmf", ".ogg", ".oga", ".mogg", ".opus", ".ra", ".rm", ".raw", ".rf64", ".sln", ".tta", ".voc", ".vox", ".wav", ".wma", ".wv", ".webm", ".8svx", ".cda"}  # fmt: skip


class LocalSongsOptions(TypedDict):
    directory: str


class LocalSongsMode(RadioMode):
    def options() -> type[Any]:
        return LocalSongsOptions

    def __init__(self, state: State, name: str, options: LocalSongsOptions):
        super().__init__(state, "Local Songs", name)

        self.directory = options["directory"]
        self.songs: list[Path] = []
        self.order: list[int] = []

    async def setup(self) -> None:
        self.songs = [
            file
            for file in Path(self.directory).rglob("*")
            if file.is_file() and file.suffix in AUDIO_EXT
        ]
        self.order = []

    async def reload(self) -> None:
        await self.setup()

    async def next(self) -> LiquidsoapUri | None:
        if not self.songs:
            logger.error(f"{self.directory} empty")
            return None

        if not self.order:
            self.order = list(range(len(self.songs)))
            random.shuffle(self.order)

        song = self.songs[self.order.pop()]

        return LiquidsoapUri(str(song), LiquidsoapMetadata(), deletable=False)
