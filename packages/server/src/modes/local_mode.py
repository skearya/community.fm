import random
from pathlib import Path
from typing import TYPE_CHECKING

from models import LiquidsoapUri
from modes.mode import RadioMode

if TYPE_CHECKING:
    from state import State

AUDIO_EXT = {".3gp", ".aa", ".aac", ".aax", ".act", ".aiff", ".alac", ".amr", ".ape", ".au", ".awb", ".dss", ".dvf", ".flac", ".gsm", ".iklax", ".ivs", ".m4a", ".m4b", ".m4p", ".mmf", ".movpkg", ".mp1", ".mp2", ".mp3", ".mpc", ".msv", ".nmf", ".ogg", ".oga", ".mogg", ".opus", ".ra", ".rm", ".raw", ".rf64", ".sln", ".tta", ".voc", ".vox", ".wav", ".wma", ".wv", ".webm", ".8svx", ".cda"}  # fmt: skip


class LocalSongsMode(RadioMode):
    def __init__(self, state: State):
        super().__init__("Local Songs", state)

        self.songs: list[Path] = []

    async def setup(self) -> None:
        return

    async def next(self) -> LiquidsoapUri:
        if not self.songs:
            self.reload()

        return LiquidsoapUri(str(self.songs.pop()), {"mode": self.name})

    def reload(self):
        music = Path(self.state.config.LOCAL_MUSIC_DIRECTORY)

        self.songs = [file for file in music.rglob("*") if file.suffix in AUDIO_EXT]

        if not self.songs:
            raise Exception("/music should contain audio files")

        random.shuffle(self.songs)
