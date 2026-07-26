import asyncio
from collections import deque
from typing import Self

import aiohttp
from clients.lastfm import LastFM
from config import Config
from db import Db
from manager import ModeManager
from models import LiquidsoapEntry, LiquidsoapMetadata
from pls import Pls
from tasks import icecast_poller, mode_reloader
from utils import Subscribable

MAX_METADATA_HISTORY = 64


class State:
    def __init__(self):
        self.config = Config()
        self.db = Db(self)

        self.pls = Pls(self.config.PLS_DOWNLOAD_DIRECTORY)
        self.session = aiohttp.ClientSession()
        self.lastfm = (
            LastFM(self, self.config.LASTFM_API_KEY, self.config.LASTFM_SECRET)
            if self.config.LASTFM_API_KEY and self.config.LASTFM_SECRET
            else None
        )

        self.manager = ModeManager(self)

        self.icecast: Subscribable[object] = Subscribable({})
        self.liquidsoap: Subscribable[LiquidsoapEntry] = Subscribable(
            LiquidsoapEntry(
                LiquidsoapMetadata(
                    title="Initializing", artist="community.fm", mode="Initializing"
                ),
                None,
            )
        )

        self.history: deque[LiquidsoapEntry] = deque(maxlen=MAX_METADATA_HISTORY)

        self.tasks = [
            asyncio.create_task(icecast_poller(self)),
            asyncio.create_task(mode_reloader(self)),
        ]

    async def __aenter__(self) -> Self:
        await self.db.connect()
        await self.pls.login()
        await self.manager.setup()

        return self

    async def __aexit__(self, *_):
        await self.session.close()
        await self.pls.logout()
        await self.db.close()
