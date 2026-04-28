from typing import List
from pls import Request
from dataclasses import dataclass

NO_NEXT = "NO_NEXT"


@dataclass
class LikedSongEntry:
    username: str
    songs: List[Request]
