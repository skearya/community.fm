import asyncio
from typing import TYPE_CHECKING

from loguru import logger
from pls.models import Download, Media, Playlist, Track
from yt_dlp import YoutubeDL

if TYPE_CHECKING:
    from loguru import Logger


class YoutubePls:
    def __init__(self, downloads_folder: str):
        self.ydl_opts = {
            "quiet": True,
            "final_ext": "mp3",
            "format": "bestaudio/best",
            "outtmpl": f"{downloads_folder}/%(title)s.%(ext)s",
            "writethumbnail": True,
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"},
                {"key": "FFmpegMetadata"},
                {"key": "EmbedThumbnail"},
            ],
        }

    async def login(self):
        pass

    async def logout(self):
        pass

    async def url(self, url: str) -> Media | None:
        if any(
            other in url
            for other in ["qobuz", "tidal", "deezer", "soundcloud", "spotify"]
        ):
            return None

        return await self.extract(url)

    async def info(self, source: str, id: str) -> Media | None:
        if source != "youtube":
            return None

        return await self.extract(id)

    async def id(self, logger: Logger, source: str, id: str) -> Download | None:
        if source != "youtube":
            return None

        return await self.resolve(logger, id)

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
                        "youtube", info["requested_downloads"][0]["filepath"]
                    )
            except Exception:
                logger.warning("youtube missing ISRC or failed to DL")
                return None

        return await asyncio.to_thread(run)

    async def extract(self, query: str) -> Media | None:
        def track(entry: dict) -> Track:
            return Track(
                id=("youtube", entry["id"]),
                url=entry.get("url"),
                isrc=None,
                title=entry.get("title"),
                artist=entry.get("channel"),
            )

        info_ydl_opts = {"quiet": True, "skip_download": True, "extract_flat": True}

        def run() -> Media | None:
            try:
                with YoutubeDL(info_ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)

                    if "entries" in info:
                        return Playlist(
                            title=info["title"],
                            items=[track(entry) for entry in info["entries"]],
                        )

                    return track(info)
            except Exception:
                logger.error(f"youtube failed to get info on id: {id}")
                return None

        return await asyncio.to_thread(run)
