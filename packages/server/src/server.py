import asyncio

from aiohttp import web
from loguru import logger
from state import State

routes = web.RouteTableDef()
STATE_KEY = web.AppKey("STATE_KEY", State)


@routes.get("/next")
async def handle(request: web.Request) -> web.Response:
    state = request.app[STATE_KEY]

    return web.Response(text=await state.mode.next())


async def start(state: State):
    app = web.Application()
    app[STATE_KEY] = state
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()

    logger.info(f"HTTP server started at {site.name}")

    await asyncio.Event().wait()
