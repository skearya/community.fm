import asyncio

from loguru import logger
from pls.models import Download, Media, MediaType, Playlist, Summary, Track
from yt_dlp import YoutubeDL
from ytmusicapi import YTMusic


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
                {"key": "FFmpegMetadata", "add_chapters": False},
                {"key": "EmbedThumbnail"},
            ],
        }

        self.ytmusic = YTMusic()

    def name(self) -> str:
        return "yt-dlp"

    async def login(self):
        pass

    async def logout(self):
        pass

    def services(self) -> list[str]:
        return ["youtube"]

    async def url(self, url: str) -> Media | None:
        return await self.extract(url)

    async def search(
        self,
        query: str,
        type: MediaType,
        services: list[str] | None,
    ) -> list[Summary]:
        if services and "youtube" not in services:
            return []

        def run() -> list[Summary]:
            def item(result: dict) -> Summary | None:
                if not (
                    id := result.get("videoId")
                    or result.get("albumId")
                    or result.get("playlistId")
                    or "browseId" in result
                    and result["browseId"].replace("VL", "", 1)
                ):
                    return None

                artists = (
                    ", ".join(artist["name"] for artist in result["artists"])
                    if "artists" in result
                    else result["author"]
                )

                return Summary(
                    ("youtube", id),
                    type,
                    result["title"],
                    artists,
                )

            kinds = {
                "track": ["song", "video"],
                "album": ["album"],
                "playlist": ["playlist"],
            }

            try:
                results = self.ytmusic.search(query)

                mapped = (
                    item(result)
                    for result in results
                    if result["resultType"] in kinds[type]
                )

                return [item for item in mapped if item]
            except Exception:
                logger.exception("youtube music failed to search")
                return []

        return await asyncio.to_thread(run)

    async def info(self, source: str, id: str, type: MediaType) -> Media | None:
        if source not in self.services():
            return None

        return await self.extract(id)

    async def id(self, source: str, id: str, type: MediaType) -> Download | None:
        if source not in self.services():
            return None

        return await self.resolve(id)

    async def isrc(self, isrc: str) -> Download | None:
        return await self.resolve(f"ytsearch1:{isrc}")

    async def resolve(self, id: str) -> Download | None:
        def run() -> Download | None:
            try:
                with YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(id)

                    if "entries" in info:
                        info = info["entries"][0]

                    return Download(
                        "youtube", info["requested_downloads"][0]["filepath"]
                    )
            except Exception:
                logger.warning("youtube missing ISRC or failed to DL")
                return None

        return await asyncio.to_thread(run)

    async def extract(self, id: str) -> Media | None:
        def run() -> Media | None:
            def item(entry: dict) -> Track:
                return Track(
                    id=("youtube", entry["id"]),
                    url=entry.get("url"),
                    isrc=None,
                    title=entry.get("title"),
                    artist=entry.get("uploader"),
                )

            opts = {"quiet": True, "skip_download": True, "extract_flat": "in_playlist"}

            try:
                with YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(id, download=False)

                    if "entries" in info:
                        return Playlist(
                            title=info["title"],
                            items=[item(entry) for entry in info["entries"]],
                        )

                    return item(info)
            except Exception:
                logger.error("youtube failed to get info")
                return None

        return await asyncio.to_thread(run)
