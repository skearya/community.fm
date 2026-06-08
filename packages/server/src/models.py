from dataclasses import dataclass, field

from pls import Track


@dataclass
class LikedSongEntry:
    username: str
    songs: list[Track]


@dataclass
class IcecastSource:
    audio_info: str | None = None
    bitrate: int | None = None
    channels: int | None = None
    genre: str | None = None
    listener_peak: int | None = None
    listeners: int | None = None
    listenurl: str | None = None
    samplerate: int | None = None
    server_description: str | None = None
    server_name: str | None = None
    server_type: str | None = None
    stream_start: str | None = None
    stream_start_iso8601: str | None = None
    title: str | None = None
    dummy: bool | None = None
    artist: str | None = None
    audio_bitrate: int | None = None
    audio_channels: int | None = None
    audio_samplerate: int | None = None
    ice_bitrate: int | None = None
    subtype: str | None = None


@dataclass
class IcecastStatus:
    admin: str | None = None
    host: str | None = None
    location: str | None = None
    server_id: str | None = None
    server_start: str | None = None
    server_start_iso8601: str | None = None
    source: list[IcecastSource] = field(default_factory=list)


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
