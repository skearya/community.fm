from modes.liked_mode import LikedSongsMode
from modes.local_songs import LocalSongs
from modes.radio_mode import RadioMode


class State:
    mode: RadioMode
    liked_songs: list[dict[str, str]]

    def __init__(self):
        self.mode = LocalSongs()
        self.liked_songs = []
