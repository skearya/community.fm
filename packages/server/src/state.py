from models import LikedSong
from modes.liked_mode import LikedSongsMode
from modes.radio_mode import RadioMode


class State:
    def __init__(self):
        self.mode: RadioMode = LikedSongsMode(self)
        self.liked_songs: list[LikedSong] = []
