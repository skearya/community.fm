import asyncio
import csv

from loguru import logger

from pls.sources.streamrip import StreamripPls
from pls.sources.youtube import YoutubePls
from pls.utils import Request


async def main():
    async with StreamripPls() as streamrip, YoutubePls() as youtube:
        with open("src/tests/stress.csv", newline="") as file:
            for row in csv.DictReader(file):
                request = Request(
                    "?", row["ISRC"], row["Track Name"], row["Artist Name(s)"]
                )

                track_logger = logger.bind(item=str(request))

                dl = await streamrip.isrc(request, track_logger) or await youtube.rip(
                    request, track_logger
                )

                if dl is not None:
                    track_logger.success(f"Downloaded from {dl.source}: {dl.path}")
                else:
                    track_logger.critical("Failed to download!")


if __name__ == "__main__":
    asyncio.run(main())
