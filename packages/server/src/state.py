from typing import Optional, Any
from asyncio import Queue
import asyncio
from modes.liked_mode import LikedSongsMode
from modes.mode import RadioMode
from models import LikedSongEntry
from pls import Pls

DATABASE_FILEPATH = "/music/pls.db"
MUSIC_DIRECTORY = "/music"


class State:
    def __init__(self):
        self.mode: RadioMode = LikedSongsMode(self)
        self.pls = Pls(DATABASE_FILEPATH, MUSIC_DIRECTORY)

        self.metadata: Optional[dict] = None
        self.metadata_updates: Queue[dict[str, str]] = asyncio.Queue()

        self.liked: dict[int, LikedSongEntry] = {}

    async def __aenter__(self) -> State:
        await self.pls.login()
        return self

    async def __aexit__(self, *_):
        await self.pls.logout()
