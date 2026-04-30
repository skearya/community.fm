from models import LikedSongEntry, LiquidsoapMetadata
from modes.liked_mode import LikedSongsMode
from modes.mode import RadioMode
from pls import Pls
from utils import Subscribable

DATABASE_FILEPATH = "/music/pls.db"
MUSIC_DIRECTORY = "/music"


class State:
    def __init__(self):
        self.mode: RadioMode = LikedSongsMode(self)
        self.pls = Pls(DATABASE_FILEPATH, MUSIC_DIRECTORY)
        self.metadata: Subscribable[LiquidsoapMetadata] = Subscribable()
        self.liked: dict[int, LikedSongEntry] = {}

    async def __aenter__(self) -> State:
        await self.pls.login()
        return self

    async def __aexit__(self, *_):
        await self.pls.logout()
