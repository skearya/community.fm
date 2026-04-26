import random
from pathlib import Path

from modes.radio_mode import RadioMode

MUSIC_DIR = Path("/music")

# https://en.wikipedia.org/wiki/Audio_file_format
AUDIO_EXT = {
    ".3gp",
    ".aa",
    ".aac",
    ".aax",
    ".act",
    ".aiff",
    ".alac",
    ".amr",
    ".ape",
    ".au",
    ".awb",
    ".dss",
    ".dvf",
    ".flac",
    ".gsm",
    ".iklax",
    ".ivs",
    ".m4a",
    ".m4b",
    ".m4p",
    ".mmf",
    ".movpkg",
    ".mp1",
    ".mp2",
    ".mp3",
    ".mpc",
    ".msv",
    ".nmf",
    ".ogg",
    ".oga",
    ".mogg",
    ".opus",
    ".ra",
    ".rm",
    ".raw",
    ".rf64",
    ".sln",
    ".tta",
    ".voc",
    ".vox",
    ".wav",
    ".wma",
    ".wv",
    ".webm",
    ".8svx",
    ".cda",
}


class LocalSongs(RadioMode):
    def __init__(self):
        self.songs: list[Path] = []

    async def next(self) -> str:
        if len(self.songs) == 0:
            self.reload()

        song, *self.songs = self.songs

        return str(song)

    def reload(self):
        self.songs = [file for file in MUSIC_DIR.rglob("*") if file.suffix in AUDIO_EXT]

        if len(self.songs) == 0:
            raise Exception("`/music` should contain audio files")

        random.shuffle(self.songs)
