from ext.models import LikedSong
from modes.liked_mode import LikedSongsMode
from modes.local_songs import LocalSongs
from modes.radio_mode import RadioMode


class State:
    def __init__(self):
        self.mode: RadioMode = LocalSongs()
        self.liked_songs: list[LikedSong] = []
