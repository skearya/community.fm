import asyncio
from collections.abc import Iterator

from deezer.errors import DataException
from loguru import logger
from pls.models import (
    Album,
    Download,
    Media,
    MediaType,
    Playlist,
    Summary,
    Track,
)
from streamrip.client import (
    Client,
    DeezerClient,
    QobuzClient,
    SoundcloudClient,
    TidalClient,
)
from streamrip.config import DEFAULT_CONFIG_PATH, Config
from streamrip.db import Database, Dummy
from streamrip.media import (
    PendingAlbum,
    PendingPlaylist,
    PendingSingle,
    PendingTrack,
)
from streamrip.metadata import AlbumMetadata as RipAlbumMetadata
from streamrip.metadata import AlbumSummary as RipAlbumSummary
from streamrip.metadata import PlaylistMetadata as RipPlaylistMetadata
from streamrip.metadata import PlaylistSummary as RipPlaylistSummary
from streamrip.metadata import SearchResults as RipSearchResults
from streamrip.metadata import TrackMetadata as RipTrackMetadata
from streamrip.metadata import TrackSummary as RipTrackSummary
from streamrip.rip.parse_url import parse_url

PREFERRED = "deezer"


class StreamripPls:
    def __init__(self, downloads_folder: str):
        self.config = Config(DEFAULT_CONFIG_PATH)

        self.config.session.downloads.folder = downloads_folder
        self.config.session.artwork.save_artwork = False
        self.config.session.cli.text_output = False
        self.config.session.cli.progress_bars = False

        self.db = Database(downloads=Dummy(), failed=Dummy())

        self.clients = {
            "qobuz": QobuzClient(self.config),
            "tidal": TidalClient(self.config),
            "deezer": DeezerClient(self.config),
            "soundcloud": SoundcloudClient(self.config),
        }

    def name(self) -> str:
        return "streamrip"

    async def login(self) -> StreamripPls:
        for source, client in self.clients.items():
            try:
                await client.login()
                logger.success(f"{source} successfully logged in")
            except Exception:
                logger.error(f"{source} failed to login!")

        return self

    async def logout(self):
        for client in self.clients.values():
            if hasattr(client, "session"):
                await client.session.close()

    def services(self) -> list[str]:
        return [client.source for client in self.active_clients()]

    async def url(self, url: str) -> Media | None:
        parsed = parse_url(url)

        if parsed is None:
            return None

        client = self.client(parsed.source)

        if client is None:
            return None

        pending = await parsed.into_pending(client, self.config, self.db)

        if isinstance(pending, PendingSingle | PendingTrack):
            type = "track"
        elif isinstance(pending, PendingAlbum):
            type = "album"
        elif isinstance(pending, PendingPlaylist):
            type = "playlist"
        else:
            return None

        return await self.info(client.source, pending.id, type)

    async def search(
        self,
        query: str,
        type: MediaType,
        services: list[str] | None,
    ) -> list[Summary]:
        services = services or [
            next(
                (c.source for c in self.active_clients() if c.source == PREFERRED),
                next(c.source for c in self.active_clients()),
            )
        ]

        async def searcher(client: Client) -> list[Summary]:
            service_type = (
                "playlist"
                if client.source == "soundcloud" and type == "album"
                else type
            )

            pages = await client.search(service_type, query)
            search = RipSearchResults.from_pages(client.source, service_type, pages)

            return streamrip_search_summaries(search, client.source)[:100]

        tasks = await asyncio.gather(
            *[
                searcher(client)
                for client in self.active_clients()
                if client.source in services
            ],
            return_exceptions=True,
        )

        results: list[Summary] = []

        for summaries in tasks:
            if isinstance(summaries, BaseException):
                logger.error(f"Streamrip search: {summaries}")
                continue

            results.extend(summaries)

        return results

    async def info(self, source: str, id: str, type: MediaType) -> Media | None:
        client = self.client(source)

        if client is None:
            return None

        if type == "track" and (
            (resp := await client.get_metadata(id, "track"))
            and (album := RipAlbumMetadata.from_track_resp(resp, client.source))
            and (meta := RipTrackMetadata.from_resp(album, client.source, resp))
        ):
            return Track(
                id=(client.source, id),
                url=None,
                isrc=meta.isrc,
                title=meta.title,
                artist=meta.artist,
            )
        elif type == "album" and (
            (resp := await client.get_metadata(id, "album"))
            and (album := RipAlbumMetadata.from_album_resp(resp, client.source))
        ):
            # HACK: Streamrip doesn't have a standardized way to read the tracks
            # in an album or playlist, so we have to try normalizing that ourselves.
            items = streamrip_album_or_playlist_tracks(resp, client.source)

            try:
                cover = album.covers.largest()[1]
            except Exception:
                cover = None

            return Album(
                title=album.album, artist=album.albumartist, cover=cover, items=items
            )
        elif type == "playlist" and (
            (resp := await client.get_metadata(id, "playlist"))
            and (playlist := RipPlaylistMetadata.from_resp(resp, client.source))
        ):
            items = streamrip_album_or_playlist_tracks(resp, client.source)

            return Playlist(title=playlist.name, items=items)

        return None

    async def id(self, source: str, id: str, type: MediaType) -> Download | None:
        client = self.client(source)

        if client is None:
            return None

        if type == "track":
            pending = PendingSingle(id, client, self.config, self.db)
        else:
            return None

        return await self.resolve(pending)

    async def isrc(self, isrc: str) -> Download | None:
        async def fetch(client: Client) -> Download | None:
            if isinstance(client, QobuzClient):
                pages = await client.search("track", isrc)
                search = RipSearchResults.from_pages("qobuz", "track", pages)

                if not search.results:
                    return None

                idd = search.results[0].id
            elif isinstance(client, TidalClient):
                result = await client._api_request(
                    "/tracks", {"filter[isrc]": isrc}, "https://openapi.tidal.com/v2"
                )

                if not result["data"]:
                    return None

                idd = result["data"][0]["id"]
            elif isinstance(client, DeezerClient):
                try:
                    result = client.client.api.get_track_by_ISRC(isrc)
                except DataException:
                    return None

                idd = result["id"]
            elif isinstance(client, SoundcloudClient):
                return None

            return await self.resolve(PendingSingle(idd, client, self.config, self.db))

        for client in self.active_clients():
            try:
                if dl := await fetch(client):
                    return dl

                logger.debug(f"{client.source} missing ISRC, checking next")
            except Exception:
                logger.exception(f"{client.source} exception")

        return None

    async def resolve(self, item: PendingSingle | PendingTrack) -> Download:
        track = await item.resolve()
        assert track

        await track.rip()

        return Download(item.client.source, track.download_path)

    def active_clients(self) -> Iterator[Client]:
        return (c for c in self.clients.values() if c.logged_in)

    def client(self, source: str) -> Client | None:
        return next((c for c in self.active_clients() if c.source == source), None)


def streamrip_search_summaries(search: RipSearchResults, source: str) -> list[Summary]:
    normalized: list[Summary] = []

    for item in search.results:
        id = (source, item.id)

        if isinstance(item, RipTrackSummary):
            summary = Summary(id=id, type="track", title=item.name, artist=item.artist)
        elif isinstance(item, RipAlbumSummary):
            summary = Summary(id=id, type="album", title=item.name, artist=item.artist)
        elif isinstance(item, RipPlaylistSummary):
            summary = Summary(
                id=id, type="playlist", title=item.name, artist=item.creator
            )
        else:
            raise NotImplementedError

        normalized.append(summary)

    return normalized


def streamrip_album_or_playlist_tracks(resp: dict, source: str) -> list[Track]:
    tracklist = resp["tracks"]["items"] if source == "qobuz" else resp["tracks"]

    normalized: list[Track] = []

    for track in tracklist:
        if source == "qobuz":
            artist = (track.get("performer") or track.get("composer"))["name"]
        elif source == "deezer" or source == "tidal":
            artist = track["artist"]["name"]
        elif source == "soundcloud":
            artist = track["user"]["username"]
        else:
            raise NotImplementedError

        normalized.append(
            Track(
                id=(source, track["id"]),
                url=None,
                isrc=track.get("isrc"),
                title=track["title"],
                artist=artist,
            )
        )

    return normalized
