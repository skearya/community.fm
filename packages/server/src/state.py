from modes.radio_mode import RadioMode
from modes.liked_mode import LikedSongsMode


class State:
    def __init__(self):
        self.mode: RadioMode = LikedSongsMode(self)
        self.liked_songs: list[dict[str, str]] = []
