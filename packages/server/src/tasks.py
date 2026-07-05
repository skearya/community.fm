import asyncio
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from state import State

ICECAST_POLL_INTERVAL = 1
MODE_RELOAD_INTERVAL = 60 * 30


async def icecast_poller(state: State):
    while True:
        try:
            async with state.session.get(
                f"{state.config.ICECAST_BASE_URL}/status-json.xsl"
            ) as response:
                response.raise_for_status()
                data = await response.json()

                state.icecast.update(data)
        except Exception as e:
            logger.debug(f"Icecast poll error: {e}")

        await asyncio.sleep(ICECAST_POLL_INTERVAL)


async def mode_reloader(state: State):
    while True:
        await asyncio.sleep(MODE_RELOAD_INTERVAL)

        try:
            await state.manager.reload()
        except Exception as e:
            logger.exception(f"Mode reload error: {e}")
