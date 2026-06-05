from dataclasses import dataclass
from typing import Literal

type Media = Track | Album | Playlist
type MediaType = Literal["track", "album", "playlist"]


@dataclass()
class Track:
    id: tuple[str, str] | None
    url: str | None
    isrc: str | None
    title: str | None
    artist: str | None


@dataclass
class Album:
    title: str
    artist: str
    cover: str | None
    items: list[Track]


@dataclass
class Playlist:
    title: str
    items: list[Track]


@dataclass
class Summary:
    id: tuple[str, str]
    type: MediaType
    title: str
    artist: str


@dataclass()
class Download:
    source: str
    path: str


# [artist, name] | query
type SearchQuery = tuple[str, str] | str

# [Preference (low to high), Summary]
type SearchResult = tuple[int, Summary]
