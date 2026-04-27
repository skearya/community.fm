import asyncio
from typing import TYPE_CHECKING

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

    async def isrc(self, logger: Logger, isrc: str) -> Download | None:
        def run(isrc: str) -> Download | None:
            with YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{isrc}")

                if len(info["entries"]) == 0:
                    logger.debug("YouTube missing song")
                    return None

                return Download(
                    "YouTube", info["entries"][0]["requested_downloads"][0]["filepath"]
                )

        return await asyncio.to_thread(run, isrc)
