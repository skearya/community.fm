import random

import aiohttp
from config import Config
from loguru import logger
from models import LikedSongEntry, LiquidsoapMetadata
from modes.liked_mode import LikedSongsMode
from modes.local_mode import LocalSongsMode
from modes.mix_mode import MixMode
from modes.mode import RadioMode
from pls import Pls
from utils import Subscribable


class State:
    def __init__(self):
        self.config = Config()

        self.modes: list[RadioMode] = [
            LocalSongsMode(self),
            LikedSongsMode(self),
        ]

        if self.config.YOUTUBE_PLAYLIST_ID:
            self.modes.append(MixMode(self, self.config.YOUTUBE_PLAYLIST_ID))
        else:
            logger.warning(
                "YOUTUBE_PLAYLIST_ID environment variable unset, disabling YouTube mix mode"
            )

        self.mode = random.choice(self.modes)
        self.session = aiohttp.ClientSession(base_url=self.config.LIQUIDSOAP_BASE_URL)
        self.pls = Pls(
            self.config.PLS_DATABASE_FILEPATH, self.config.PLS_DOWNLOAD_DIRECTORY
        )

        self.liked: dict[int, LikedSongEntry] = {}
        self.metadata: Subscribable[LiquidsoapMetadata] = Subscribable()

    async def setup_modes(self) -> None:
        for mode in self.modes:
            await mode.setup()

    async def __aenter__(self) -> State:
        await self.pls.login()
        await self.setup_modes()
        return self

    async def __aexit__(self, *_):
        await self.session.close()
        await self.pls.logout()
