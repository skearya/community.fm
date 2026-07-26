from operator import itemgetter

from loguru import logger

from pls.models import (
    Download,
    Media,
    MediaType,
    SearchQuery,
    Summary,
    Track,
)
from pls.sources.streamrip import StreamripPls
from pls.sources.youtube import YoutubePls
from pls.utils import similarity


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
        if (
            track.url
            and not (track.id or track.title or track.artist)
            and (updated := await self.url(track.url))
        ):
            assert isinstance(updated, Track)
            track = updated

        if track.id and (dl := await self.id(*track.id, "track")):
            return dl

        if track.isrc and (dl := await self.isrc(track.isrc)):
            return dl

        if (
            (track.title and track.artist)
            and (summary := await self.best((track.artist, track.title), "track"))
            and (dl := await self.id(*summary.id, "track"))
        ):
            return dl

        return None

    async def url(self, url: str) -> Media | None:
        for pls in [self.streamrip, self.youtube]:
            try:
                if result := await pls.url(url):
                    return result
            except Exception:
                logger.exception(f"{pls.name()} url")

        return None

    async def info(self, source: str, id: str, type: MediaType) -> Media | None:
        for pls in [self.streamrip, self.youtube]:
            try:
                if result := await pls.info(source, id, type):
                    return result
            except Exception:
                logger.exception(f"{pls.name()} info")

        return None

    async def id(self, source: str, id: str, type: MediaType) -> Download | None:
        for pls in [self.streamrip, self.youtube]:
            try:
                if result := await pls.id(source, id, type):
                    return result
            except Exception:
                logger.exception(f"{pls.name()} id")

        return None

    async def isrc(self, isrc: str) -> Download | None:
        for pls in [self.streamrip, self.youtube]:
            try:
                if result := await pls.isrc(isrc):
                    return result
            except Exception:
                logger.exception(f"{pls.name()} isrc")

        return None

    async def search(
        self,
        query: SearchQuery,
        type: MediaType,
        services: list[str] | None = None,
    ) -> list[Summary]:
        text = f"{query[0]} - {query[1]}" if isinstance(query, tuple) else query

        try:
            results = await self.streamrip.search(text, type, services)
        except Exception:
            logger.exception("streamrip search")
            return []

        ranked = [
            ((rank(result, query), preference), result)
            for preference, result in results
        ]

        ranked.sort(key=itemgetter(0), reverse=True)

        return list(map(itemgetter(1), ranked))

    async def best(
        self, query: SearchQuery, type: MediaType, services: list[str] | None = None
    ) -> Summary | None:
        MINIMUM_ACCEPTABLE_THRESHOLD = 95.0

        if not (results := await self.search(query, type, services or self.services())):
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
