from os import environ
import asyncio
from typing import List
import aiohttp
from models import LikedSongEntry, LiquidsoapMetadata
from modes.liked_mode import LikedSongsMode
from modes.mode import RadioMode
from modes.local_mode import LocalSongsMode
from modes.mixes.mix_mode import MixMode
from pls import Pls
from utils import Subscribable

LIQUIDSOAP_BASE_URL = "http://liquidsoap:8002"
DATABASE_FILEPATH = "/music/pls.db"
MUSIC_DIRECTORY = "/music"


class State:
    def __init__(self):
        self.modes: List[RadioMode] = [
            LikedSongsMode(self),
            LocalSongsMode(),
            MixMode(self, environ["YOUTUBE_PLAYLIST_ID"]),
        ]
        self.mode: RadioMode = self.modes[2]

        self.session = aiohttp.ClientSession(base_url=LIQUIDSOAP_BASE_URL)
        self.pls = Pls(DATABASE_FILEPATH, MUSIC_DIRECTORY)

        self.liked: dict[int, LikedSongEntry] = {}
        self.metadata: Subscribable[LiquidsoapMetadata] = Subscribable()

    async def setup_modes(self) -> None:
        for mode in self.modes:
            await mode.setup()

    async def __aenter__(self) -> State:
        asyncio.gather(self.pls.login(), self.setup_modes())
        return self

    async def __aexit__(self, *_):
        await self.session.close()
        await self.pls.logout()
