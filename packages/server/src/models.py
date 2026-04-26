from dataclasses import dataclass

NO_NEXT = "NO_NEXT"


@dataclass
class LikedSong:
    name: str
    artists: str
    isrc: str
