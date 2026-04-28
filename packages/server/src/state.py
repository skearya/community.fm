from modes.liked_mode import LikedSongsMode
from modes.mode import RadioMode
from models import LikedSongEntry
from pls import Pls

DATABASE_FILEPATH = "/music/pls.db"
MUSIC_DIRECTORY = "/music"


class State:
    def __init__(self):
        self.mode: RadioMode = LikedSongsMode(self)
        self.liked: dict[int, LikedSongEntry] = {}
        self.pls = Pls(DATABASE_FILEPATH, MUSIC_DIRECTORY)

    async def __aenter__(self) -> State:
        await self.pls.login()
        return self

    async def __aexit__(self, *_):
        await self.pls.logout()
