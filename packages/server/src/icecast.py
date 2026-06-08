import asyncio
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from state import State

POLL_INTERVAL = 1


async def poll_icecast(state: State):
    while True:
        try:
            async with state.session.get(
                f"{state.config.ICECAST_BASE_URL}/status-json.xsl"
            ) as response:
                response.raise_for_status()
                data = await response.json()

                state.status.update(data)
        except Exception as e:
            logger.debug(f"Icecast poll error: {e}")

        await asyncio.sleep(POLL_INTERVAL)
