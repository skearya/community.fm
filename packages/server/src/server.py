import secrets
from aiohttp.typedefs import Handler
import asyncio
import json
from aiohttp import ClientConnectionResetError, web
from aiohttp_sse import sse_response
from loguru import logger
from state import State
from os import environ


routes = web.RouteTableDef()
STATE_KEY = web.AppKey("STATE_KEY", State)

LIQUIDSOAP_TOKEN = environ["LIQUIDSOAP_TOKEN"]
LIQUIDSOAP_ONLY_ROUTES = set()


def liquidsoap_only(handler: Handler):
    """Only liquidsoap may call this route using the secret."""
    LIQUIDSOAP_ONLY_ROUTES.add(handler)
    return handler


@web.middleware
async def liquidsoap_only_auth(request: web.Request, handler: Handler):
    if handler in LIQUIDSOAP_ONLY_ROUTES:
        token = request.headers.get("X-Liquidsoap-Token", "")
        if not secrets.compare_digest(token, LIQUIDSOAP_TOKEN):
            raise web.HTTPForbidden(reason="Liquidsoap-only route; token required.")
    return await handler(request)


@routes.get("/next")
@liquidsoap_only
async def next(request: web.Request) -> web.Response:
    state = request.app[STATE_KEY]

    return web.Response(text=await state.mode.next())


@routes.post("/metadata")
@liquidsoap_only
async def update_metadata(request: web.Request) -> web.Response:
    state = request.app[STATE_KEY]
    state.metadata = await request.json()

    for queue in state.metadata_listeners:
        await queue.put(state.metadata)

    logger.info(f"Received metadata update: {state.metadata['title']}")
    return web.Response(status=200)


@routes.get("/metadata")
async def get_metadata(request: web.Request) -> web.StreamResponse:
    state = request.app[STATE_KEY]
    queue = asyncio.Queue()

    state.metadata_listeners.add(queue)

    try:
        async with sse_response(request) as resp:
            if metadata := state.metadata:
                await resp.send(json.dumps(metadata))

            while True:
                metadata = await queue.get()
                await resp.send(json.dumps(metadata))
    except ClientConnectionResetError:
        pass
    except Exception:
        logger.exception("Metadata SSE failed?")
    finally:
        state.metadata_listeners.remove(queue)

    return resp


async def start(state: State):
    app = web.Application(middlewares=[liquidsoap_only_auth])
    app[STATE_KEY] = state

    app.add_routes(routes)
    app.add_routes([web.static("/", "/static")])

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()

    logger.info(f"HTTP server started at {site.name}")

    await asyncio.Event().wait()
