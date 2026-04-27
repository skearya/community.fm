import asyncio
from typing import TYPE_CHECKING

import yt_dlp
from pls.utils import Download
from yt_dlp import YoutubeDL

if TYPE_CHECKING:
    from loguru import Logger


class YoutubePls:
    def __init__(self, downloads_folder: str):
        self.ydl_opts = {
            "quiet": True,
            "format": "bestaudio/best",
            "outtmpl": f"{downloads_folder}/%(title)s.%(ext)s",
            "writethumbnail": True,
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "m4a"},
                {"key": "FFmpegMetadata"},
                {"key": "EmbedThumbnail"},
            ],
        }

    async def login(self):
        pass

    async def logout(self):
        pass

    async def url(self, logger: Logger, url: str) -> Download | None:
        extractors = yt_dlp.extractor.gen_extractors()

        for e in extractors:
            if e.suitable(url) and e.IE_NAME != "generic":
                return await self.resolve(logger, url)

        logger.info("Failed to parse URL with YouTube")
        return None

    async def isrc(self, logger: Logger, isrc: str) -> Download | None:
        return await self.resolve(logger, f"ytsearch1:{isrc}")

    async def resolve(self, logger: Logger, query: str) -> Download | None:
        def run() -> Download | None:
            try:
                with YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(query)

                    if "entries" in info:
                        info = info["entries"][0]

                    return Download(
                        "YouTube", info["requested_downloads"][0]["filepath"]
                    )
            except Exception:
                logger.debug("YouTube missing ISRC, checking next")
                return None

        return await asyncio.to_thread(run)
