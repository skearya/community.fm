from os import environ
from typing import TYPE_CHECKING, Iterator

from deezer.errors import DataException
from loguru import logger
from pls.utils import Download, Request, similarity
from streamrip.client import (
    Client,
    DeezerClient,
    QobuzClient,
    SoundcloudClient,
    TidalClient,
)
from streamrip.config import DEFAULT_CONFIG_PATH, Config
from streamrip.db import Database, Dummy
from streamrip.media import PendingSingle
from streamrip.metadata import SearchResults, TrackSummary

if TYPE_CHECKING:
    from loguru import Logger


class StreamripPls:
    config: Config
    db: Database
    clients: dict[str, Client]

    def __init__(self):
        self.config = Config(DEFAULT_CONFIG_PATH)

        self.config.session.downloads.folder = "/music"
        self.config.session.cli.text_output = False
        self.config.session.cli.progress_bars = False

        self.db = Database(
            downloads=Dummy(),
            failed=Dummy(),
        )

        self.clients = {
            "Qobuz": QobuzClient(self.config),
            "Tidal": TidalClient(self.config),
            "Deezer": DeezerClient(self.config),
            "SoundCloud": SoundcloudClient(self.config),
        }

    async def __aenter__(self) -> StreamripPls:
        for source, client in self.clients.items():
            try:
                await client.login()
            except Exception:
                logger.error(f"{source} failed to login!")

        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        for client in self.clients.values():
            if hasattr(client, "session"):
                await client.session.close()

    async def isrc(self, track: Request, info: Logger) -> Download | None:
        for source, client in self.active_clients():
            try:
                match client:
                    case QobuzClient():
                        dl = await self.qobuz(client, track)
                    case TidalClient():
                        dl = await self.tidal(client, track)
                    case DeezerClient():
                        dl = await self.deezer(client, track)
                    case SoundcloudClient():
                        dl = await self.soundcloud(client, track)

                if dl is not None:
                    return dl

                info.debug(f"{source} missing song, checking next source")
            except Exception:
                info.exception(f"{source} exception")

        return None

    async def search(self, track: Request, logger: Logger) -> Download | None:
        # [Similarity (0 - 100), Preference from client order (-i)]
        # By using `-i` as a fallback to compare during sorting when ratings are equal, we will prefer higher quality clients
        type Score = tuple[float, int]

        similar: list[tuple[Score, TrackSummary, Client]] = []

        for i, (source, client) in enumerate(self.active_clients()):
            try:
                query = f"{track.artist} - {track.name}"
                pages = await client.search("track", query)
                search = SearchResults.from_pages(client.source, "track", pages)

                if len(search.results) == 0:
                    logger.debug(f"No search results on {source}")
                    continue

                for item in search.results:
                    rating = similarity(
                        track.name, item.name, track.artist, item.artist
                    )

                    if rating >= 99.0:
                        logger.debug(f"Perfect match on {source}")
                        return await self.resolve(client, item.id)

                    similar.append(((rating, -i), item, client))
            except Exception:
                logger.exception(f"{source} exception")

        if len(similar) == 0:
            return None

        similar.sort(key=lambda track: track[0])

        rating, item, client = similar[-1]

        if rating[0] < 85.0:
            logger.debug(f"Closest match: {rating:.2f}%, giving up")
            return None

        try:
            return await self.resolve(client, item.id)
        except Exception:
            logger.exception(f"{source} exception")

    async def qobuz(self, qobuz: QobuzClient, track: Request) -> Download | None:
        pages = await qobuz.search("track", track.isrc)
        search = SearchResults.from_pages("qobuz", "track", pages)

        if len(search.results) == 0:
            return None

        return await self.resolve(qobuz, search.results[0].id)

    async def tidal(self, tidal: TidalClient, track: Request) -> Download | None:
        result = await tidal._api_request(
            "/tracks",
            {"filter[isrc]": track.isrc},
            "https://openapi.tidal.com/v2",
        )

        if len(result["data"]) == 0:
            return None

        return await self.resolve(tidal, result["data"][0]["id"])

    async def deezer(self, deezer: DeezerClient, track: Request) -> Download | None:
        try:
            result = deezer.client.api.get_track_by_ISRC(track.isrc)
        except DataException:
            return None

        return await self.resolve(deezer, result["id"])

    async def soundcloud(
        self, soundcloud: SoundcloudClient, track: Request
    ) -> Download | None:
        pages = await soundcloud.search("track", f"{track.artist} {track.name}")
        search = SearchResults.from_pages("soundcloud", "track", pages)

        if len(search.results) == 0:
            return None

        return await self.resolve(soundcloud, search.results[0].id)

    async def resolve(self, client: Client, id: str) -> Download | None:
        track = await PendingSingle(id, client, self.config, self.db).resolve()

        if track is None:
            raise Exception(f"{client.source} resolve failed")

        await track.rip()

        return Download(client.source.capitalize(), track.download_path)

    def active_clients(self) -> Iterator[tuple[str, Client]]:
        return ((k, v) for k, v in self.clients.items() if v.logged_in)
