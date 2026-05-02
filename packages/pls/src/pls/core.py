import dataclasses
import json
import shelve
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from pls.sources.streamrip import StreamripPls
from pls.sources.youtube import YoutubePls
from pls.utils import Download, Request

if TYPE_CHECKING:
    from loguru import Logger


class Pls:
    def __init__(self, database_file: str, downloads_folder: str):
        self.db = shelve.open(database_file)
        self.streamrip = StreamripPls(downloads_folder)
        self.youtube = YoutubePls(downloads_folder)

    async def login(self):
        await self.streamrip.login()
        await self.youtube.login()

    async def logout(self):
        self.db.close()
        await self.streamrip.logout()
        await self.youtube.logout()

    async def give(self, track: Request) -> Download | None:
        tlogger = logger.bind(track=track)

        key = json.dumps(dataclasses.asdict(track), sort_keys=True)

        if dl := self.db.get(key):
            dl = Download(**dl)

            if Path(dl.path).is_file():
                tlogger.debug("Found request from database")
                return dl

        if dl := await self.download(tlogger, track):
            self.db[key] = dataclasses.asdict(dl)
            return dl

        return None

    async def download(self, tlogger: Logger, track: Request) -> Download | None:
        if track.url and (
            dl := await self.streamrip.url(tlogger, track.url)
            or await self.youtube.url(tlogger, track.url)
        ):
            return dl

        if track.isrc and (
            dl := await self.streamrip.isrc(tlogger, track.isrc)
            or await self.youtube.isrc(tlogger, track.isrc)
        ):
            return dl

        if (
            track.artist
            and track.name
            and (dl := await self.streamrip.search(tlogger, track.artist, track.name))
        ):
            return dl

        return None
