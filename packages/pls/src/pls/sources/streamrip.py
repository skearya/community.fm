from typing import TYPE_CHECKING, Iterator

from deezer.errors import DataException
from loguru import logger
from pls.utils import Download, similarity
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
from streamrip.rip.parse_url import parse_url

if TYPE_CHECKING:
    from loguru import Logger


class StreamripPls:
    def __init__(self, downloads_folder: str):
        self.config = Config(DEFAULT_CONFIG_PATH)

        self.config.session.downloads.folder = downloads_folder
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

    async def login(self) -> StreamripPls:
        for source, client in self.clients.items():
            try:
                await client.login()
            except Exception:
                logger.error(f"{source} failed to login!")

        return self

    async def logout(self):
        for client in self.clients.values():
            if hasattr(client, "session"):
                await client.session.close()

    async def url(self, logger: Logger, url: str) -> Download | None:
        parsed = parse_url(url)

        if parsed is None:
            logger.debug("Failed to parse URL with Streamrip")
            return None

        client = self.clients[parsed.source]
        pending = await parsed.into_pending(client, self.config, self.db)

        if not isinstance(pending, PendingSingle):
            logger.warning("URL pointed to something other than a single")
            return None

        return await self.resolve(client, pending)

    async def isrc(self, logger: Logger, isrc: str) -> Download | None:
        for source, client in self.active_clients():
            try:
                match client:
                    case QobuzClient():
                        dl = await self.qobuz(client, isrc)
                    case TidalClient():
                        dl = await self.tidal(client, isrc)
                    case DeezerClient():
                        dl = await self.deezer(client, isrc)
                    case SoundcloudClient():
                        continue

                if dl is not None:
                    return dl

                logger.debug(f"{source} missing ISRC, checking next")
            except Exception:
                logger.exception(f"{source} exception")

        return None

    async def search(self, logger: Logger, artist: str, name: str) -> Download | None:
        PERFECT_MATCH_THRESHOLD = 99.0
        MINIMUM_ACCEPTABLE_THRESHOLD = 85.0

        # Score: [Similarity (0 - 100), Client preference by index (-i)]
        type Score = tuple[float, int]

        similar: list[tuple[Score, TrackSummary, Client]] = []

        for i, (source, client) in enumerate(self.active_clients()):
            try:
                query = f"{artist} - {name}"
                pages = await client.search("track", query)
                search = SearchResults.from_pages(client.source, "track", pages)

                if len(search.results) == 0:
                    logger.debug(f"No results on {source}, checking next")
                    continue

                for item in search.results:
                    score = similarity(name, item.name, artist, item.artist)

                    if score >= PERFECT_MATCH_THRESHOLD:
                        logger.debug(f"Perfect match on {source}")
                        return await self.resolve(
                            client, PendingSingle(item.id, client, self.config, self.db)
                        )

                    similar.append(((score, -i), item, client))
            except Exception:
                logger.exception(f"{source} exception")

        if len(similar) == 0:
            return None

        similar.sort(key=lambda track: track[0], reverse=True)
        score, item, client = similar[0]

        if score[0] < MINIMUM_ACCEPTABLE_THRESHOLD:
            logger.debug(f"Closest match: {score[0]:.2f}%, giving up")
            return None

        try:
            return await self.resolve(
                client, PendingSingle(item.id, client, self.config, self.db)
            )
        except Exception:
            logger.exception(f"{client.source} exception")
            return None

    async def qobuz(self, qobuz: QobuzClient, isrc: str) -> Download | None:
        pages = await qobuz.search("track", isrc)
        search = SearchResults.from_pages("qobuz", "track", pages)

        if len(search.results) == 0:
            return None

        return await self.resolve(
            qobuz, PendingSingle(search.results[0].id, qobuz, self.config, self.db)
        )

    async def tidal(self, tidal: TidalClient, isrc: str) -> Download | None:
        result = await tidal._api_request(
            "/tracks", {"filter[isrc]": isrc}, "https://openapi.tidal.com/v2"
        )

        if len(result["data"]) == 0:
            return None

        return await self.resolve(
            tidal, PendingSingle(result["data"][0]["id"], tidal, self.config, self.db)
        )

    async def deezer(self, deezer: DeezerClient, isrc: str) -> Download | None:
        try:
            result = deezer.client.api.get_track_by_ISRC(isrc)
        except DataException:
            return None

        return await self.resolve(
            deezer, PendingSingle(result["id"], deezer, self.config, self.db)
        )

    async def resolve(self, client: Client, single: PendingSingle) -> Download:
        track = await single.resolve()

        if track is None:
            raise Exception(f"{client.source} resolve failed")

        await track.rip()

        return Download(client.source.capitalize(), track.download_path)

    def active_clients(self) -> Iterator[tuple[str, Client]]:
        return ((k, v) for k, v in self.clients.items() if v.logged_in)
