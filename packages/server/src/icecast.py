import asyncio
from typing import TYPE_CHECKING

from loguru import logger
from models import IcecastStatus

if TYPE_CHECKING:
    from state import State

POLL_INTERVAL = 1


async def poll_icecast(state: State):
    while True:
        async with state.session.get(
            f"{state.config.ICECAST_BASE_URL}/status-json.xsl"
        ) as response:
            response.raise_for_status()
            data = await response.json()

            try:
                status = IcecastStatus(**data["icestats"])
                state.status.update(status)
            except Exception as e:
                logger.debug(f"Icecast poll error: {e}")

        await asyncio.sleep(POLL_INTERVAL)
