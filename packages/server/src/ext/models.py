from dataclasses import dataclass


@dataclass
class LikedSong:
    name: str
    artists: str
    isrc: str
