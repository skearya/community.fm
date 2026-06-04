from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Download:
    source: str
    path: str


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


# [Preference (low to high), Summary]
type SearchResult = tuple[int, Summary]
