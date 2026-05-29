import asyncio
from collections import deque

import aiohttp
from config import Config
from icecast import poll_icecast
from manager import ModeManager
from models import IcecastStatus, LikedSongEntry, LiquidsoapMetadata
from pls import Pls
from utils import Subscribable

MAX_METADATA_HISTORY = 64


class State:
    def __init__(self):
        self.config = Config()
        self.manager = ModeManager(self)
        self.session = aiohttp.ClientSession()
        self.pls = Pls(self.config.PLS_DOWNLOAD_DIRECTORY)

        self.liked: dict[int, LikedSongEntry] = {}
        self.status: Subscribable[IcecastStatus] = Subscribable()
        self.metadata: Subscribable[LiquidsoapMetadata] = Subscribable()
        self.metadata_history: deque[tuple[LiquidsoapMetadata, int | float]] = deque(
            maxlen=MAX_METADATA_HISTORY
        )

        self.tasks: set[asyncio.Task] = {asyncio.create_task(poll_icecast(self))}

    async def __aenter__(self) -> State:
        await self.pls.login()
        await self.manager.setup()
        return self

    async def __aexit__(self, *_):
        await self.session.close()
        await self.pls.logout()
