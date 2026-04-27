from loguru import logger

from pls.sources.streamrip import StreamripPls
from pls.sources.youtube import YoutubePls
from pls.utils import Download, Request


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

    async def give(self, track: Request) -> Download | None:
        tlogger = logger.bind(track=track)

        if track.url and (dl := await self.streamrip.url(tlogger, track.url)):
            return dl

        if track.isrc and (
            dl := await self.streamrip.isrc(tlogger, track.isrc)
            or await self.youtube.isrc(tlogger, track.isrc)
        ):
            return dl

        if dl := await self.streamrip.search(tlogger, track.artist, track.name):
            return dl

        return None
