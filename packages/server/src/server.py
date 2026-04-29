import asyncio
import json

from aiohttp import ClientConnectionResetError, web
from aiohttp_sse import sse_response
from loguru import logger
from state import State

routes = web.RouteTableDef()
STATE_KEY = web.AppKey("STATE_KEY", State)


# TODO: Make sure ONLY liquidsoap can get to this (listen on non-exposed port?)
@routes.get("/next")
async def handle_next(request: web.Request) -> web.Response:
    state = request.app[STATE_KEY]

    return web.Response(text=await state.mode.next())


# TODO: Make sure ONLY liquidsoap can post to this (listen on non-exposed port?)
@routes.post("/metadata")
async def handle_update_metadata(request: web.Request) -> web.Response:
    state = request.app[STATE_KEY]
    state.metadata = await request.json()

    for queue in state.metadata_listeners:
        await queue.put(state.metadata)

    logger.info(f"Received metadata update: {state.metadata['title']}")
    return web.Response(status=200)


@routes.get("/metadata")
async def handle_get_metadata(request: web.Request) -> web.StreamResponse:
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
    app = web.Application()
    app[STATE_KEY] = state

    app.add_routes(routes)
    app.add_routes([web.static("/", "/static")])

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()

    logger.info(f"HTTP server started at {site.name}")

    await asyncio.Event().wait()
