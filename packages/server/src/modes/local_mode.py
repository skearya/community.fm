import random
from pathlib import Path

from modes.mode import RadioMode

MUSIC_DIR = Path("/music")
AUDIO_EXT = {".3gp", ".aa", ".aac", ".aax", ".act", ".aiff", ".alac", ".amr", ".ape", ".au", ".awb", ".dss", ".dvf", ".flac", ".gsm", ".iklax", ".ivs", ".m4a", ".m4b", ".m4p", ".mmf", ".movpkg", ".mp1", ".mp2", ".mp3", ".mpc", ".msv", ".nmf", ".ogg", ".oga", ".mogg", ".opus", ".ra", ".rm", ".raw", ".rf64", ".sln", ".tta", ".voc", ".vox", ".wav", ".wma", ".wv", ".webm", ".8svx", ".cda"}  # fmt: skip


class LocalSongsMode(RadioMode):
    def name(self) -> str:
        return "Local Songs"

    def __init__(self):
        self.songs: list[Path] = []

    async def setup(self) -> None:
        return

    async def next(self) -> str:
        if not self.songs:
            self.reload()

        return str(self.songs.pop())

    def reload(self):
        self.songs = [file for file in MUSIC_DIR.rglob("*") if file.suffix in AUDIO_EXT]

        if not self.songs:
            raise Exception("/music should contain audio files")

        random.shuffle(self.songs)
