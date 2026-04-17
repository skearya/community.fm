import sys
import asyncio
import csv
from dataclasses import dataclass

from deezer.errors import DataException
from loguru import logger
from streamrip.client import (
    Client,
    DeezerClient,
    QobuzClient,
    SoundcloudClient,
    TidalClient,
)
from streamrip.config import DEFAULT_CONFIG_PATH, Config
from streamrip.db import Database, Dummy
from streamrip.media import PendingSingle, Track
from streamrip.metadata import SearchResults

logger.remove()

format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "{extra} | <level>{message}</level>"
)

logger.add(
    sys.stderr,
    backtrace=False,
    diagnose=False,
    format=format,
)

logger.add(
    "logs/out.log",
    format=format,
)


@dataclass
class SpotifyTrack:
    uri: str
    name: str
    artist_uris: str
    artist_names: str
    album_uri: str
    album_name: str
    album_artist_uris: str
    album_artist_names: str
    album_release_date: str
    album_image_url: str
    disc_number: str
    track_number: str
    track_duration: str
    track_preview_url: str
    explicit: str
    popularity: str
    isrc: str
    added_by: str
    added_at: str


async def rip(
    clients: list[Client],
    config: Config,
    db: Database,
    track: SpotifyTrack,
) -> Track | None:
    track_logger = logger.bind(song=(track.artist_names, track.name, track.isrc))

    for client in clients:
        try:
            match client:
                case QobuzClient():
                    result = await qobuz(client, config, db, track)
                case TidalClient():
                    result = await tidal(client, config, db, track)
                case DeezerClient():
                    result = await deezer(client, config, db, track)
                case SoundcloudClient():
                    result = await soundcloud(client, config, db, track)

            if result is not None:
                track_logger.success(
                    f"Downloaded from {client.source.capitalize()}: {result.download_path}"
                )
                return result
            else:
                track_logger.debug(
                    f"{client.source.capitalize()} doesn't have the song, checking next source"
                )
        except Exception:
            track_logger.exception(f"{client.source.capitalize()} error")

    track_logger.critical("Failed to download after trying every source!")
    return None


async def qobuz(
    qobuz: QobuzClient, config: Config, db: Database, track: SpotifyTrack
) -> Track | None:
    pages = await qobuz.search("track", track.isrc)
    search = SearchResults.from_pages("qobuz", "track", pages)

    if len(search.results) == 0:
        return None

    return await resolve(qobuz, config, db, search.results[0].id)


async def tidal(
    tidal: TidalClient, config: Config, db: Database, track: SpotifyTrack
) -> Track | None:
    result = await tidal._api_request(
        "/tracks",
        {"filter[isrc]": track.isrc},
        "https://openapi.tidal.com/v2",
    )

    if len(result["data"]) == 0:
        return None

    return await resolve(tidal, config, db, result["data"][0]["id"])


async def deezer(
    deezer: DeezerClient, config: Config, db: Database, track: SpotifyTrack
) -> Track | None:
    try:
        result = deezer.client.api.get_track_by_ISRC(track.isrc)
    except DataException:
        return None

    return await resolve(deezer, config, db, result["id"])


async def soundcloud(
    soundcloud: SoundcloudClient, config: Config, db: Database, track: SpotifyTrack
) -> Track | None:
    pages = await soundcloud.search("track", f"{track.artist_names} {track.name}")
    search = SearchResults.from_pages("soundcloud", "track", pages)

    if len(search.results) == 0:
        return None

    return await resolve(soundcloud, config, db, search.results[0].id)


async def resolve(
    client: Client, config: Config, db: Database, id: str
) -> Track | None:
    pending = PendingSingle(id, client, config, db)
    track = await pending.resolve()

    if track is None:
        raise Exception(f"{client.source} resolve failed")

    await track.rip()
    return track


async def main():
    config = Config(DEFAULT_CONFIG_PATH)

    config.session.cli.text_output = False
    config.session.cli.progress_bars = False

    db = Database(
        downloads=Dummy(),
        failed=Dummy(),
    )

    clients: list[Client] = [
        QobuzClient(config),
        TidalClient(config),
        DeezerClient(config),
        SoundcloudClient(config),
    ]

    try:
        for client in clients:
            await client.login()

        with open("src/tests/stress.csv", newline="") as file:
            reader = csv.reader(file)
            header = next(reader)

            for row in reader:
                assert len(header) == len(row)
                await rip(clients, config, db, SpotifyTrack(*row))
    finally:
        for client in clients:
            if client.logged_in:
                await client.session.close()


if __name__ == "__main__":
    asyncio.run(main())
