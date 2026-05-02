from dataclasses import dataclass

from rapidfuzz import fuzz


@dataclass(frozen=True)
class Request:
    url: str | None
    isrc: str | None
    name: str | None
    artist: str | None


@dataclass(frozen=True)
class Download:
    source: str
    path: str


def similarity(name0: str, name1: str, artist0: str, artist1: str) -> float:
    name_similarity = fuzz.token_set_ratio(name0, name1)
    artist_similarity = fuzz.token_set_ratio(artist0, artist1)

    return name_similarity * 0.4 + artist_similarity * 0.6
