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

# fmt: off
problematic = [
    ("Jane Remover, Danny Brown", "Psychoboost"),
    ('lapix, Mylta, RANASOL', 'Trajectory'),
    ('sasalasa, sasakure.UK, lasah', 'LIN NE KRO NE'),
    ('James Landino, Slyleaf', 'Reaction - Osu Edit'),
    ('Silentroom, Frums', 'Aegleseeker'),
    ('Silentroom, Frums', 'Aegleseeker - "Afterworld" Full Version'),
    ('かめりあ', "chrono diver -fragment- (かめりあ's “crossroads of chrono” remix)"),
    ('kanemiko, うさぎでんき', 'Impermanence'),
    ('ShibayanRecords', 'タイニーリトル・アジアンタム'),
    ('kamome sano, Ayaka Igasaki', 'clover  - Camellia\'s "Floating Hypnosys" Remix'),
    ('Mitchie M, Hatsune Miku, OSTER project', 'Love! Snow! Really Magic (feat. Hatsune Miku) - OSTER project Remix'),
    ('OSTER project', 'ピアノ×フォルテ×スキャンダル -初音ミク「マジカルミライ 2014」Live-'),
    ('Yutaka Yamada, Soru', 'Alone - Soru Remix'),
    ('kessoku band', 'ギターと孤独と蒼い惑星'),
    ('Porter Robinson, Anamanaguchi', 'Get Your Wish - Anamanaguchi Remix'),
    ('uma, Morimori Atsushi, MisoilePunch♪', "you're Nxt -Dreams Remix- (feat. MisoilePunch)"),
    ('Nanahira, Camellia', 'Kansoku-eisei'),
    ('Tyler, The Creator, Daniel Caesar', 'St. Chroma (feat. Daniel Caesar)'),
    ('Danny Brown, ta Ukrainka, Zheani, Cynthoni', 'The End'),
    ('matt proxy, Current Joys, never goodbye', 'God (with current joys & never goodbye)'),
    ('Jamie Paige, unit.0', 'Dyad'),
]
# fmt: on


async def main():
    pls = Pls(os.getcwd())

    await pls.login()

    for query in problematic:
        if results := await pls.search(query, "track", pls.services()):
            score, summary = results[0]

            rich.print(f"{score}: {query} | {summary}")
        else:
            rich.print(f"Failed! {query}")

    await pls.logout()


if __name__ == "__main__":
    asyncio.run(main())
