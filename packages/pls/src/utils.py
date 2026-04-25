from rapidfuzz import fuzz
from dataclasses import dataclass


@dataclass
class Request:
    url: str
    isrc: str
    name: str
    artist: str

    def __str__(self):
        return f"{self.name} - {self.artist} [{self.isrc}]"


@dataclass
class Download:
    source: str
    path: str


def similarity(name0: str, name1: str, artist0: str, artist1: str) -> float:
    name_similarity = fuzz.token_set_ratio(name0, name1)
    artist_similarity = fuzz.token_set_ratio(artist0, artist1)

    return name_similarity * 0.3 + artist_similarity * 0.7
