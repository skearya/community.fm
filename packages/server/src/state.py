import aiohttp
from models import LikedSongEntry, LiquidsoapMetadata
from modes.liked_mode import LikedSongsMode
from modes.mode import RadioMode
from pls import Pls
from utils import Subscribable

LIQUIDSOAP_BASE_URL = "http://liquidsoap:8002"
DATABASE_FILEPATH = "/music/pls.db"
MUSIC_DIRECTORY = "/music"


class State:
    def __init__(self):
        self.mode: RadioMode = LikedSongsMode(self)
        self.session = aiohttp.ClientSession(base_url=LIQUIDSOAP_BASE_URL)
        self.pls = Pls(DATABASE_FILEPATH, MUSIC_DIRECTORY)

        self.liked: dict[int, LikedSongEntry] = {}
        self.metadata: Subscribable[LiquidsoapMetadata] = Subscribable()

    async def __aenter__(self) -> State:
        await self.pls.login()
        return self

    async def __aexit__(self, *_):
        await self.session.close()
        await self.pls.logout()
