import asyncio
import csv
import sys

from loguru import logger
from sources.streamrip import StreamripPls
from sources.youtube import YoutubePls
from utils import Request

logger.remove()

format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "{extra} | <level>{message}</level>"
)

logger.add(
    sys.stderr,
    backtrace=False,
    diagnose=False,
    format=format,
)

logger.add(
    "logs/out.log",
    format=format,
)


async def main():
    async with StreamripPls() as streamrip, YoutubePls() as youtube:
        with open("src/tests/stress.csv", newline="") as file:
            for row in csv.DictReader(file):
                request = Request(
                    "?", row["ISRC"], row["Track Name"], row["Artist Name(s)"]
                )

                track_logger = logger.bind(item=str(request))

                dl = await streamrip.rip(request, track_logger) or await youtube.rip(
                    request, track_logger
                )

                if dl is not None:
                    track_logger.success(f"Downloaded from {dl.source}: {dl.path}")
                else:
                    track_logger.critical("Failed to download!")


if __name__ == "__main__":
    asyncio.run(main())
