import base64
import re
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Literal, TypedDict

from pls import Track


class LiquidsoapEntry:
    id: uuid.UUID
    time: float
    metadata: LiquidsoapMetadata
    cover: tuple[str, bytes] | None

    def __init__(self, metadata: LiquidsoapMetadata, cover: str | None):
        self.id = uuid.uuid4()
        self.time = time.time()
        self.metadata = metadata
        self.cover = None

        if cover:
            match cover.split(",", 1):
                case [header, data] if search := re.search("data:(.*);", header):
                    mime = search.group(1)
                    decoded = base64.b64decode(data)

                    self.cover = (mime, decoded)

    def serializable(entry: LiquidsoapEntry) -> SerializableLiquidsoapEntry:
        return {
            "id": str(entry.id),
            "time": entry.time,
            "metadata": {k: v for k, v in asdict(entry.metadata).items() if v},
        }


# Sourced from liquidsoap: `settings.encoder.metadata.export()` without `settings.encoder.metadata.cover()` and without `cover` (covers get handled seperately from metadata)
# `metadata.json.stringify()` implementation: https://github.com/savonet/liquidsoap/blob/main/src/libs/metadata.liq
@dataclass
class LiquidsoapMetadata:
    artist: str | None = None
    title: str | None = None
    album: str | None = None
    genre: str | None = None
    date: str | None = None
    tracknumber: str | None = None
    comment: str | None = None
    track: str | None = None
    year: str | None = None
    dj: str | None = None
    next: str | None = None
    metadata_url: str | None = None
    coverart: str | None = None
    user: str | None = None
    avatar: str | None = None
    mode: str | None = None
    playcount: str | None = None


class SerializableLiquidsoapEntry(TypedDict):
    id: str
    time: float
    metadata: dict[str, Any]


class InfoMessage(TypedDict):
    type: Literal["info"]
    stream: str
    modes: list[str]
    icecast: object
    liquidsoap: SerializableLiquidsoapEntry
    history: list[SerializableLiquidsoapEntry]


class IcecastMessage(TypedDict):
    type: Literal["icecast"]
    data: object


class LiquidsoapMessage(TypedDict):
    type: Literal["liquidsoap"]
    data: SerializableLiquidsoapEntry


@dataclass
class LiquidsoapUri:
    file: str
    metadata: dict[str, str]
    deletable: bool

    def __str__(self) -> str:
        return (
            f"annotate:{','.join(f'{k}="{v}"' for k, v in self.metadata.items())}:{self.file}"
            if self.metadata
            else self.file
        )


@dataclass
class ChannelModeEntry:
    username: str
    avatar_url: str
    tracks: list[Track]


@dataclass
class RequestQueueModeEntry:
    username: str
    avatar_url: str
    track: Track
