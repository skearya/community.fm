import asyncio
from typing import TYPE_CHECKING

from utils import Download, Request
from yt_dlp import YoutubeDL

if TYPE_CHECKING:
    from loguru import Logger


ydl_opts = {
    "quiet": True,
    "format": "bestaudio/best",
    "outtmpl": "%(title)s.%(ext)s",
    "writethumbnail": True,
    "postprocessors": [
        {"key": "FFmpegExtractAudio", "preferredcodec": "m4a"},
        {"key": "FFmpegMetadata"},
        {"key": "EmbedThumbnail"},
    ],
}


class YoutubePls:
    async def __aenter__(self) -> YoutubePls:
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        pass

    async def rip(self, track: Request, logger: Logger) -> Download | None:
        def run(track: Request) -> Download | None:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{track.isrc}")

                if len(info["entries"]) == 0:
                    logger.debug("YouTube missing song")
                    return None

                return Download(
                    "YouTube", info["entries"][0]["requested_downloads"][0]["filepath"]
                )

        return await asyncio.to_thread(run, track)
