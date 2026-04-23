from typing import TYPE_CHECKING

from deezer.errors import DataException
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
from streamrip.metadata import SearchResults
from utils import Download, Request

if TYPE_CHECKING:
    from loguru import Logger


class StreamripPls:
    config: Config
    db: Database
    clients: dict[str, Client]

    def __init__(self):
        self.config = Config(DEFAULT_CONFIG_PATH)
        self.config.session.cli.text_output = False
        self.config.session.cli.progress_bars = False

        self.db = Database(
            downloads=Dummy(),
            failed=Dummy(),
        )

        self.clients = {
            "qobuz": QobuzClient(self.config),
            "tidal": TidalClient(self.config),
            "deezer": DeezerClient(self.config),
            "soundcloud": SoundcloudClient(self.config),
        }

    async def __aenter__(self) -> StreamripPls:
        for client in self.clients.values():
            await client.login()

        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        for client in self.clients.values():
            if hasattr(client, "session"):
                await client.session.close()

    async def rip(self, track: Request, logger: Logger) -> Download | None:
        for source, client in self.clients.items():
            try:
                source = client.source.capitalize()

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

                logger.debug(f"{source} missing song, checking next source")
            except Exception:
                logger.exception(f"{source} exception")

        return None

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
