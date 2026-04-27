import asyncio
import csv
import os
import sys
from io import StringIO

import rich
from loguru import logger
from pls.core import Pls
from pls.utils import Request

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


data = """"Track URI","Track Name","Artist URI(s)","Artist Name(s)","Album URI","Album Name","Album Artist URI(s)","Album Artist Name(s)","Album Release Date","Album Image URL","Disc Number","Track Number","Track Duration (ms)","Track Preview URL","Explicit","Popularity","ISRC","Added By","Added At"
"spotify:track:17McTYdz0Hhtf1Vd7H85q2","Sunset Memory","spotify:artist:15scGTX3RG92n1iw3XDveV, spotify:artist:7FLncERjIjQ8ESzMPYHGWx","lone distance driver, 오미일곱 omilgop","spotify:album:5T9f6pZDg3wBiaxsS4pCPR","our unsung memories","spotify:artist:15scGTX3RG92n1iw3XDveV, spotify:artist:7FLncERjIjQ8ESzMPYHGWx","lone distance driver, 오미일곱 omilgop","2025-10-17","https://i.scdn.co/image/ab67616d0000b273091661e42aac43254eb04345","1","3","367250","https://p.scdn.co/mp3-preview/7facc3798516915aa8aeb3dbec46e060f2109660?cid=9950ac751e34487dbbe027c4fd7f8e99","false","4","QT3FD2539598","spotify:user:srz3wg23iyukf5vxpa74i37to","2026-04-16T23:00:13Z"
"spotify:track:2PuvoxtrLu3MzCLfq68b2B","Story -Extended mix- / Vo.きらぴかみうな","spotify:artist:4YlOMzdVKMLLaYe5sWijAE","ナイフ","spotify:album:5qSoL7y6KSTV1tQETWDhR0","媚薬","spotify:artist:4YlOMzdVKMLLaYe5sWijAE","ナイフ","2018-12-30","https://i.scdn.co/image/ab67616d0000b2737fc2b0ee342ad44e8c578002","1","2","286107","https://p.scdn.co/mp3-preview/c510ac741b8a9360200c624965d09ea9300a4d75?cid=9950ac751e34487dbbe027c4fd7f8e99","false","1","JPW561903038","spotify:user:srz3wg23iyukf5vxpa74i37to","2026-04-16T23:00:17Z"
"spotify:track:0jiDTif2izwSDYOclIAK5F","Mario Moore","spotify:artist:7wDbVfM9I4kikWhVEuD3jt","Ministerio de Obras Públicas","spotify:album:1okHiAugOELs2MqwYI7dWT","Mario Moore","spotify:artist:7wDbVfM9I4kikWhVEuD3jt","Ministerio de Obras Públicas","2023-08-08","https://i.scdn.co/image/ab67616d0000b2731ca6525b0669320c159af817","1","1","222926","https://p.scdn.co/mp3-preview/05bb505deb6a39a8eb867f360616a46129496fb8?cid=9950ac751e34487dbbe027c4fd7f8e99","false","1","GX3HH2349280","spotify:user:srz3wg23iyukf5vxpa74i37to","2026-04-16T23:00:20Z"
"spotify:track:1bk1LIZMroo8DTSonGpim0","Synchronicity","spotify:artist:6XBzH0KBUstRwk0q8tnP3g","goche'","spotify:album:7yJWD2mzQR2GD6jQqpsjOC","シンクロニシティ","spotify:artist:6XBzH0KBUstRwk0q8tnP3g","goche'","2011-09-07","https://i.scdn.co/image/ab67616d0000b273245e85281c0545fa73aa6b57","1","3","366253","https://p.scdn.co/mp3-preview/cb26377260162dbdc5409a8dc391e0dc112090c6?cid=9950ac751e34487dbbe027c4fd7f8e99","false","3","JPB951104788","spotify:user:srz3wg23iyukf5vxpa74i37to","2026-04-16T23:00:22Z"
"""


async def main():
    pls = Pls(os.path.join(os.getcwd(), "tracks.db"), os.getcwd())

    await pls.login()

    for row in csv.DictReader(StringIO(data)):
        request = Request(None, row["ISRC"], row["Track Name"], row["Artist Name(s)"])
        rich.print(await pls.give(request))

    await pls.logout()


if __name__ == "__main__":
    asyncio.run(main())
