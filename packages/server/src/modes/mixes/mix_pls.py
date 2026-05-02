from loguru import logger
import asyncio
from yt_dlp import YoutubeDL
from typing import List


class MixPls:
    def __init__(self, playlist_id: str):
        self.playlist_id = playlist_id
        self.ydl_opts = {
            "quiet": True,
            "ignoreerrors": True,
            "extract_flat": "in_playlist",
        }

    async def get_video_ids(self) -> List[str]:
        def run() -> List[str]:
            try:
                with YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(self.playlist_id, download=False)
                    if "entries" in info:
                        return [e["id"] for e in info["entries"]]
                    else:
                        raise ValueError("Key 'entries' not found")
            except Exception as e:
                logger.debug(f"Failed to get playlist: {e}")
                return []

        return await asyncio.to_thread(run)
