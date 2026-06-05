import asyncio
import os
import sys

import rich
from loguru import logger
from pls import Pls

logger.remove()

format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "{extra} | <level>{message}</level>"
)

logger.add(
    sys.stderr,
    format=format,
)

singles = [
    "https://open.qobuz.com/track/320260958",
    "https://tidal.com/track/421826024/u",
    "https://www.deezer.com/us/track/3262183051",
    "https://soundcloud.com/janeremover/twice-removed",
]

albums = [
    "https://open.qobuz.com/album/zed343s3nmsvb",
    "https://www.qobuz.com/us-en/album/revengeseekerz-jane-remover/zed343s3nmsvb",
    "https://tidal.com/album/421826023",
    "https://tidal.com/album/421826023/u",
    "https://www.deezer.com/us/album/722106551",
    "https://soundcloud.com/janeremover/sets/revengeseekerz",
]

playlists = [
    "https://open.qobuz.com/playlist/2049430",
    "https://tidal.com/playlist/34c543c9-bb74-4b79-91a8-feb6d815f43c",
    "https://www.deezer.com/us/playlist/2098157264",
    "https://soundcloud.com/trending-music-us/sets/electronic-1",
]


async def main():
    pls = Pls(os.getcwd())

    await pls.login()

    for url in [*singles, *albums, *playlists]:
        rich.print(await pls.url(url))

    await pls.logout()


if __name__ == "__main__":
    asyncio.run(main())
