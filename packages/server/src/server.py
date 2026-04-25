import asyncio

from aiohttp import web
from loguru import logger

routes = web.RouteTableDef()


@routes.get("/get")
async def handle(request: web.Request) -> web.Response:
    name = request.match_info.get("name", "Anonymous")
    text = "Hello, " + name

    return web.Response(text=text)


async def start():
    app = web.Application()
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner)
    await site.start()

    logger.info(f"HTTP server started at {site.name}")

    await asyncio.Event().wait()
