from models import LikedSong
from modes.liked_mode import LikedSongsMode
from modes.mode import RadioMode
from pls import Pls

MUSIC_DIRECTORY = "/music"


class State:
    def __init__(self):
        self.mode: RadioMode = LikedSongsMode(self)
        self.liked: list[LikedSong] = []
        self.pls = Pls(MUSIC_DIRECTORY)

    async def __aenter__(self) -> State:
        await self.pls.login()
        return self

    async def __aexit__(self, *_):
        await self.pls.logout()
