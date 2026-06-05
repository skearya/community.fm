from operator import itemgetter
from typing import TYPE_CHECKING

from loguru import logger

from pls.models import Download, Media, MediaType, SearchQuery, Summary, Track
from pls.sources.streamrip import StreamripPls
from pls.sources.youtube import YoutubePls
from pls.utils import similarity

if TYPE_CHECKING:
    from loguru import Logger


class Pls:
    def __init__(self, downloads_folder: str):
        self.streamrip = StreamripPls(downloads_folder)
        self.youtube = YoutubePls(downloads_folder)

    async def login(self):
        await self.streamrip.login()
        await self.youtube.login()

    async def logout(self):
        await self.streamrip.logout()
        await self.youtube.logout()

    def services(self) -> list[str]:
        return self.streamrip.services()

    async def give(self, track: Track) -> Download | None:
        tlogger = logger.bind(media=track)

        if (
            track.url
            and not (track.id or track.title or track.artist)
            and (updated := await self.url(track.url))
        ):
            assert isinstance(updated, Track)
            track = updated

        if track.id and (dl := await self.id(tlogger, *track.id, "track")):
            return dl

        if track.isrc and (dl := await self.isrc(tlogger, track.isrc)):
            return dl

        if (
            (track.title and track.artist)
            and (summary := await self.best((track.artist, track.title), "track"))
            and (dl := await self.id(tlogger, *summary.id, "track"))
        ):
            return dl

        return None

    async def url(self, url: str) -> Media | None:
        return await self.streamrip.url(url) or await self.youtube.url(url)

    async def info(self, source: str, id: str, type: MediaType) -> Media | None:
        return await self.streamrip.info(source, id, type) or await self.youtube.info(
            source, id
        )

    async def id(
        self, logger: Logger, source: str, id: str, type: MediaType
    ) -> Download | None:
        return await self.streamrip.id(
            logger, source, id, type
        ) or await self.youtube.id(logger, source, id)

    async def isrc(self, logger: Logger, isrc: str) -> Download | None:
        return await self.streamrip.isrc(logger, isrc) or await self.youtube.isrc(
            logger, isrc
        )

    async def search(
        self,
        query: SearchQuery,
        type: MediaType,
        services: list[str] | None = None,
    ) -> list[Summary]:
        query = f"{query[0]} - {query[1]}" if isinstance(query, tuple) else query

        results = await self.streamrip.search(query, type, services)

        ranked = [
            ((rank(result, query), preference), result)
            for preference, result in results
        ]

        ranked.sort(key=itemgetter(0), reverse=True)

        return list(map(itemgetter(1), ranked))

    async def best(
        self, query: SearchQuery, type: MediaType, services: list[str] | None = None
    ) -> Summary | None:
        MINIMUM_ACCEPTABLE_THRESHOLD = 90.0

        results = await self.search(query, type, services or self.services())

        if not results:
            return None

        summary = results[0]
        score = rank(summary, query)

        if score < MINIMUM_ACCEPTABLE_THRESHOLD:
            logger.warning(f"Closest similarity: {score:.2f}%")
            return None

        return summary


def rank(summary: Summary, info: SearchQuery) -> int | float:
    match info:
        case [artist, title]:
            return similarity(title, summary.title, artist, summary.artist)
        case query:
            return similarity(query, f"{summary.artist} - {summary.title}")
