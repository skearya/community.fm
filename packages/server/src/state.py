from modes.radio_mode import RadioMode
from modes.local_songs import LocalSongs


class State:
    mode: RadioMode = LocalSongs()
