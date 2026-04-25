from modes.radio_mode import RadioMode
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state import State


class LikedSongsMode(RadioMode):
    def __init__(self, state: State):
        self.state = state

    def next(self) -> str:
        if not self.state.liked_songs:
            return "/etc/liquidsoap/assets/oops.mp3"

        return "/etc/liquidsoap/assets/stream-intro.mp3"
