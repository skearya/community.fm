import asyncio
from typing import TYPE_CHECKING
from models import IcecastStatus

if TYPE_CHECKING:
    from state import State


async def poll_icecast(state: State):
    while True:
        async with state.session.get(
            f"{state.config.ICECAST_BASE_URL}/status-json.xsl"
        ) as response:
            response.raise_for_status()
            data = await response.json()
            status = IcecastStatus(**data["icestats"])

        state.status.update(status)
        await asyncio.sleep(1)
