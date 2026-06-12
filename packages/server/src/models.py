from dataclasses import dataclass

from pls import Track


@dataclass
class ChannelModeEntry:
    username: str
    tracks: list[Track]


# Sourced from liquidsoap: `settings.encoder.metadata.export()` without `settings.encoder.metadata.cover()`
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
    cover: str | None = None
    user: str | None = None
    mode: str | None = None
    playcount: str | None = None


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
