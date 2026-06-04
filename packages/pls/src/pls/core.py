from operator import itemgetter
from typing import TYPE_CHECKING

from loguru import logger

from pls.models import Download, Media, MediaType, Summary, Track
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

    async def give(self, track: Track) -> Download | None:
        tlogger = logger.bind(media=track)

        if (
            track.url
            and not (track.id and track.title and track.artist)
            and (updated := await self.url(track.url))
        ):
            assert isinstance(updated, Track)
            track = updated

        if track.id and (
            dl := await self.streamrip.id(tlogger, *track.id, "track")
            or await self.youtube.id(tlogger, *track.id)
        ):
            return dl

        if track.isrc and (
            dl := await self.streamrip.isrc(tlogger, track.isrc)
            or await self.youtube.isrc(tlogger, track.isrc)
        ):
            return dl

        if (
            track.title
            and track.artist
            and (dl := await self.best(tlogger, track.title, track.artist, "track"))
        ):
            return dl

        return None

    async def url(self, url: str) -> Media | None:
        return await self.streamrip.url(url) or await self.youtube.url(url)

    async def info(self, source: str, id: str, type: MediaType) -> Media | None:
        return await self.streamrip.info(source, id, type) or await self.youtube.info(
            source, id
        )

    async def search(
        self, title: str | None, artist: str | None, query: str | None, type: MediaType
    ) -> list[Summary]:
        assert (title and artist) or query

        results = await self.streamrip.search(logger, title, artist, query, type)

        def rank(summary: Summary) -> int | float:
            if title and artist:
                return similarity(title, summary.title, artist, summary.artist)
            elif query:
                return similarity(query, f"{summary.artist} - {summary.title}")
            else:
                raise Exception()

        ranked = [
            ((rank(result), preference), result) for preference, result in results
        ]

        ranked.sort(key=itemgetter(0), reverse=True)

        return list(map(itemgetter(1), ranked))

    async def best(
        self, logger: Logger, title: str, artist: str, type: MediaType
    ) -> Download | None:
        MINIMUM_ACCEPTABLE_THRESHOLD = 90.0

        results = await self.search(title, artist, None, type)

        if not results:
            return None

        summary = results[0]
        score = similarity(title, summary.title, artist, summary.artist)

        if score < MINIMUM_ACCEPTABLE_THRESHOLD:
            logger.warning(f"Closest similarity: {score:.2f}%")
            return None

        if summary.id and (
            dl := await self.streamrip.id(logger, *summary.id, "track")
            or await self.youtube.id(logger, *summary.id)
        ):
            return dl

        return None
