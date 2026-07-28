# ruff: noqa: ASYNC230

import asyncio
import csv
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


async def main():
    pls = Pls(os.getcwd())

    await pls.login()

    with open("data/playlist.csv") as file:
        for row in csv.DictReader(file):
            query = (row["Artist Name(s)"], row["Track Name"])

            if results := await pls.search(query, "track", pls.services()):
                score, summary = results[0]

                rich.print(f"{score}: {query} | {summary}")
            else:
                rich.print(f"Failed! {query}")

    await pls.logout()


if __name__ == "__main__":
    asyncio.run(main())
